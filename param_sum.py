import random
import string

def generate_random_combination(total, parts):
    break_points = sorted(random.sample(range(1, total), parts - 1))
    break_points = [0] + break_points + [total]
    params = [break_points[i + 1] - break_points[i] for i in range(parts)]
    return params

# パラメータ
total = 100
parts = 8
num_patterns = 27

param_names = list(string.ascii_uppercase[:parts])

for i in range(num_patterns):
    random_combination = generate_random_combination(total, parts)


    assert sum(random_combination) == total, f"Sum of parameters is not {total}: {random_combination}"
    print(f"Pattern {i + 1}:")
    for name, value in zip(param_names, random_combination):
        print(f"  {name}: {value}")
    print()

