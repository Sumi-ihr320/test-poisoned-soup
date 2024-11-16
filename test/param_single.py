import random
import string
import os
import json

def generate_random_combination(total, parts):
    # 区切りをランダムに
    break_points = sorted(random.sample(range(1, total), parts - 1))
    break_points = [0] + break_points + [total]
    params = [break_points[i + 1] - break_points[i] for i in range(parts)]
    return params

with open("Profession.json",encoding="utf-8_sig") as f:
    json_load = json.load(f)

# パラメータ
total = 100
parts = 8
num_patterns = len(json_load)

new_json = {}

# num_patterns に合わせて、複数のパターンを生成（あんまり大きい数だとメモリエラーになる）
for prof in json_load:
    param_names = json_load[prof]
    random_combination = generate_random_combination(total, len(param_names))
    new_json[prof] = {}
    for name, value in zip(param_names, random_combination):
        new_json[prof][name] = value

print(new_json)
with open("Profession.json","w",encoding="utf-8_sig") as f:
    json.dump(new_json,f)

