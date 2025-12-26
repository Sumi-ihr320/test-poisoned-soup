import os, sys, glob, argparse

# プロジェクトルートをsys.pathに追加
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils import load_and_normalize_json, save_json
from manager.event_processors.normalize import normalize_step

def convert_file(path, apply=False):
    scenarios_by_id = load_and_normalize_json(path)
    for sid, steps in scenarios_by_id.items():
        new_steps = [normalize_step(s) for s in steps]
        if steps == new_steps:
            print(f"{path}: {sid}: no changes")
            continue
        print(f"{path}: {sid}: will change")
        # サンプル差分を表示（最初に異なるステップのみ）
        for i, (a, b) in enumerate(zip(steps, new_steps)):
            if a != b:
                print("  first diff index: ", i)
                print("  before: ", a)
                print("  after: ", b)
                break
        if apply:
            scenarios_by_id[sid] = new_steps

    if apply:
        save_json(path, scenarios_by_id)
        print (f"{path}: written")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()
    for p in glob.glob("d:\\python_sp\\poison_soup\\Scenario\\*.json"):
        convert_file(p, apply=args.apply)        
