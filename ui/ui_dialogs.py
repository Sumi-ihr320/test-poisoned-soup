
import tkinter as tk
from tkinter import simpledialog, messagebox, ttk

from utils import validate_input, validate_int, validate_num, ime_on, ime_off, TopmostManager

# simpledialogの代わり(モーダルはうまくいかないがエラーメッセージの日本語化はできた)
class CustomDialog(simpledialog.Dialog):
    def __init__(self, parent, title="title", text="文字列を入力してください", input_value="", input_type=None, min_value=0, max_value=99, num=None):
        
        self.text = text    # ダイアログに表示するテキスト
        self.input_type = input_type
        self.min_value = min_value      # 入力できる最小値
        self.max_value = max_value      # 入力できる最大値
        self.num = num                  # 入力可能文字数
        self.value = tk.StringVar()
        self.value.set(input_value)
        
        super().__init__(parent, title)

    def body(self, frame):
        # ラベル作成
        label = ttk.Label(frame, text=self.text).pack(pady=10)

        # エントリー作成
        vcmd = (self.register(validate_input), "\%d", "%P", self.input_type, self.num)
        func = ime_on if self.input_type == str else ime_off
        self.entry = ttk.Entry(frame, textvariable=self.value, validate="key", validatecommand=vcmd)
        self.entry.pack(pady=10)
        self.entry.bind(sequence="ForcusIn", func=func)

        return self.entry

    # OKボタンを押したとき
    def apply(self):
        if self.validate():
            try:
                self.result = int(self.value.get())
            except ValueError:
                self.result = self.value.get()

    # 入力を検証する
    def validate(self):
        if self.input_type == int:
            if not validate_int(self.value.get()):
                with TopmostManager(self):
                    messagebox.showerror("入力エラー", f"数字を入力してください")
                return False
            
            value = int(self.value.get())
            # 値がmin-maxの間かどうかをチェックする
            if not (self.min_value <= value <= self.max_value):
                with TopmostManager(self):
                    messagebox.showerror("入力エラー", f"入力値は{self.min_value}から{self.max_value}の間で入力してください")
                return False
            
        if not validate_num(self.value.get(), self.num):
            with TopmostManager(self):
                messagebox.showerror("入力エラー", f"文字数制限を超えています")
            return False

        return True
