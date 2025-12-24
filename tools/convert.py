from utils import load_and_normalize_json

def convert_file(path, apply=None):
    scenarios_by_id = load_and_normalize_json(path)
    for steps in scenarios_by_id.values:
        pass