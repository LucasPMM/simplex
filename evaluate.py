import os

inputs = [
    'FEASIBLE1',
    'INLIMITED1',
    'INLIMITED2',
    'INLIMITED3',
    'INFEASIBLE1',
    'INFEASIBLE2',
    'INFEASIBLE3',
    'HARD2',

    # 'HARD1',
    # 'HARD3',
    # 'HARD4',
    # 'HARD5',

    # 'FEASIBLE2',
    # 'FEASIBLE3',
    # 'DEGENERATED',
]

path_input = './tests/inputs/'
path_output = './tests/outputs/'

for i, input in enumerate(inputs):
    entradas = f'{path_input}{input}.txt'
    saidas = f'{path_output}{input}_out.txt'
    print('==>', input)
    os.system(f"python3 simplex.py {entradas} {saidas}")
