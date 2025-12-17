import pygame

from constans import InputMode
from input_mode_manager import input_mode_manager
from virtual_cursor import VirtualCursor

# キーボードによる選択アイテム移動システム
class FocusManager:
    def __init__(self, screen):
        self.screen = screen

        self.page_elements = []
        self.optional_elements = []
        self.elements = []  # 登録順のリスト
        self.focus_idx = 0
        self.virtual_cursor = VirtualCursor(screen)

    # 要素登録
    def register(self, element):
        # フォーカス対象の要素を登録
        if element.is_focusable():
            self.elements.append(element)

    # 初期化
    def clear(self):
        self.elements.clear()
        self.focus_idx = 0

    # イベント分岐
    def handle_event(self, event):
        # キー押下でモード切替
        if event.type == pygame.KEYDOWN:
            if input_mode_manager.is_mouse():
                pos = self.switch_from_mouse()
                before_mode = input_mode_manager.get_before_mode()
                if before_mode == InputMode.KEYBOARD or before_mode is None:
                    self.switch_to_keyboard(pos)
                elif before_mode == InputMode.CURSOR:
                    self.switch_to_cursor(pos)

            # CapsLockでcursorモードとkeyboardモード切り替え
            if event.key == pygame.K_CAPSLOCK:
                if input_mode_manager.is_cursor():
                    pos = self.switch_from_cursor()
                    self.switch_to_keyboard(pos)
                else:
                    pos = self.switch_from_keyboard()
                    self.switch_to_cursor(pos)
                
        # マウス操作でマウスモードに切り替え
        elif event.type == pygame.MOUSEMOTION:
            if abs(event.rel[0]) > 1 or abs(event.rel[1]) > 1:
                if input_mode_manager.is_keyboard():
                    pos = self.switch_from_keyboard()
                elif input_mode_manager.is_cursor():
                    pos = self.switch_from_cursor()
                else:
                    pos = None

                if pos:
                    self.switch_to_mouse(pos)

        if input_mode_manager.is_mouse():
            action = self._handle_mouse(event)
            return action
        elif input_mode_manager.is_cursor():
            self._handle_virtual_cursor(event)
        elif input_mode_manager.is_keyboard():
            self._handle_keyboard(event)

    # マウス操作処理
    def _handle_mouse(self, event):
        if event.type == pygame.MOUSEMOTION:
            pos = event.pos
            for el in self.elements:
                el.handle_mouse_hover(pos)
        
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for el in self.elements:
                if el.collidepoint(pos):
                    self._set_focus(el)
                    el.handle_click(pos)
                    return "dicide"

        return None

    # 仮想カーソル処理
    def _handle_virtual_cursor(self, event):
        # 仮想カーソルを動かしてhover対象をfocus
        self.virtual_cursor.update(event)

        pos = self.virtual_cursor.get_pos()
        for el in self.elements:
            el.handle_mouse_hover(pos)

        # 仮想カーソル決定ボタン
        if event.type == pygame.KEYDOWN and event.key in (pygame.K_RETURN, pygame.K_SPACE):
            hovered = self.virtual_cursor.check_hover(self.elements)
            if hovered:
                self._set_focus(hovered) 
                hovered.handl_click(pos)

    # キーボード操作処理
    def _handle_keyboard(self, event):
        if event.type != pygame.KEYDOWN:
            return
        
        if event.key in (pygame.K_UP,):
            self._move_focus_grid("up")
        elif event.key in (pygame.K_LEFT,):
            self._move_focus_grid("left")
        elif event.key in (pygame.K_DOWN,):
            self._move_focus_grid("down")
        elif event.key in (pygame.K_RIGHT,):
            self._move_focus_grid("right")
        elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
            focused = self.get_focused()
            if focused:
                pos = focused.get_center()
                focused.handle_click(pos)

    # フォーカス関連
    def _move_focus_linear(self, delta):
        if not self.elements:
            return
        
        self.focus_idx = (self.focus_idx + delta) % len(self.elements)
        self._apply_focus()

    def _move_focus_grid(self, direction):
        if not self.elements:
            return
        
        current = None
        if 0 <= self.focus_idx < len(self.elements):    
            current = self.elements[self.focus_idx]

        if current is None:
            self.focus_idx = 0
            self._apply_focus()
            return

        cur_r, cur_c = getattr(current, "row", None), getattr(current, "col", None)
        if cur_r is None or cur_c is None:
            self.focus_idx = 0
            self._apply_focus()
            return
            
        candidates = []
        for i, el in enumerate(self.elements):
            if el is current:
                continue
            
            r, c = getattr(el, "row", None), getattr(el, "col", None)
            if r is None or c is None:
                continue

            # 上側の候補 => 優先は同列 (col差が小さい)、次に行差が小さい
            if direction == "up" and r < cur_r:
                candidates.append((i, el, cur_r - r, abs(cur_c - c)))
            elif direction == "down" and r > cur_r:
                candidates.append((i, el, r - cur_r, abs(cur_c - c)))
            elif direction == "left" and c < cur_c:
                candidates.append((i, el, cur_c - c, abs(cur_r - r)))
            elif direction == "right" and c > cur_c:
                candidates.append((i, el, c - cur_c, abs(cur_r - r)))
        
        if not candidates:
            # フォールバック（線形移動）
            self._move_focus_linear(-1 if direction in ("up", "left") else 1)
            return
                
        # ソート：まず行/列差が小さい（近いもの優先）、同差なら列/行差が小さい
        # candidates entries: (index, el, primary_dist, secondary_dist)
        candidates.sort(key=lambda t: (t[2], t[3]))
        chosen_index = candidates[0][0]
        self.focus_idx = chosen_index
        self._apply_focus()
        
    # elementからfocusをセットする
    def _set_focus(self, element):
        # element が elements の中に無ければindex0にフォーカス
        if element in self.elements:
            self.focus_idx = self.elements.index(element)
        else:
            # 見つからない場合は0にフォーカス
            self.focus_idx = 0 if self.elements else -1
        self._apply_focus()

        """
        if element in self.elements:
            for el in self.elements:
                el.set_focus(el == element)
            if element in self.elements:
                self.focus_idx = self.elements.index(element)
        else:
            # どれにも当たらなかった → index0 にフォーカス
            if self.elements:
                fallback = self.elements[0]
                for el in self.elements:
                    el.set_focus(el is fallback)
                self.focus_idx = 0
            else:
                # elementsが空 → 何もしない
                self.focus_idx = -1
        """

    # indexからfocusをセットする
    def _apply_focus(self):
        if not self.elements:
            self.focus_idx = -1
            return
        
        if self.focus_idx < 0 or self.focus_idx >= len(self.elements):
            self.focus_idx = 0

        for i, el in enumerate(self.elements):
            is_focus = (i == self.focus_idx)
            el.set_focus(is_focus)

    # 現在focus中のアイテムをゲットする
    def get_focused(self):
        if not self.elements:
            return None
        return self.elements[self.focus_idx]

    # マウスモードから他モードへ切り替え
    def switch_from_mouse(self):
        pygame.mouse.set_visible(False)
        return pygame.mouse.get_pos()

    # 他モードからマウスモードへ切り替え
    def switch_to_mouse(self, pos):
        input_mode_manager.set_mode(InputMode.MOUSE)
        pygame.mouse.set_pos(pos)
        pygame.mouse.set_visible(True)

    # 仮想カーソルモードから他モードへ切り替え
    def switch_from_cursor(self):
        self.virtual_cursor.visible = False
        pos = self.virtual_cursor.get_pos()
        return pos

    # 他モードから仮想カーソルモードへ切り替え
    def switch_to_cursor(self, pos):
        input_mode_manager.set_mode(InputMode.CURSOR)
        self.virtual_cursor.set_pos(pos)
        self.virtual_cursor.visible = True

    # キーボードモードから他モードへ切り替え
    def switch_from_keyboard(self):
        focused = self.get_focused()
        if focused:
            pos = focused.get_center()
        else:
            pos = pygame.Vector2(self.screen.get_width() // 2, self.screen.get_height() // 2)
        return pos

    # キーボードモードに切り替え
    def switch_to_keyboard(self, pos):
        input_mode_manager.set_mode(InputMode.KEYBOARD)
        found = False
        for el in self.elements:
            if el.collidepoint(pos):
                self._set_focus(el)
                found = True
                break
        if not found:
            if self.elements:
                self._set_focus(self.elements[0])

    # input_mode_managerの値からモードを設定する
    def setting_mode(self, mode):
        if mode == InputMode.MOUSE:
            pygame.mouse.set_visible(True)
        elif mode == InputMode.KEYBOARD:
            pygame.mouse.set_visible(False)
            if self.elements:
                self._set_focus(self.elements[0])
        elif mode == InputMode.CURSOR:
            pos = pygame.mouse.get_pos()
            pygame.mouse.set_visible(False)
            self.virtual_cursor.set_pos(pos)
            self.virtual_cursor.visible = True

    def draw(self):
        self.virtual_cursor.draw() 


