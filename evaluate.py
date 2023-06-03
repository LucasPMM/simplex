import os

inputs = [
    # 'DEGENERATED',
    # 'FEASIBLE2',
    'HARD1',
    # 'HARD3',
    # 'HARD5',
    'INFEASIBLE2',
    # 'INLIMITED1', (ok)
    # 'INLIMITED3',
    # 'FEASIBLE1', (ok)
    # 'FEASIBLE3',
    # 'HARD2',
    # 'HARD4',
    # 'INFEASIBLE1', (ok)
    # 'INFEASIBLE3',
    'INLIMITED2',
]

path_input = './tests/inputs/'
path_output = './tests/outputs/'

for i, input in enumerate(inputs):
    entradas = f'{path_input}{input}.txt'
    saidas = f'{path_output}{input}_out.txt'
    print('==>', input)
    os.system(f"python3 simplex.py {entradas} {saidas}")
