import os

inputs = [
    'FEASIBLE1',
    'INFEASIBLE1',
    'INLIMITED1',
    
    'FEASIBLE2',
    'INFEASIBLE2',
    'INLIMITED2',
    
    'INLIMITED3',
    'FEASIBLE3',
    'INFEASIBLE3',
    
    'DEGENERATED',
]

path_input = './tests/inputs/'
path_output = './tests/outputs/'

for i, input in enumerate(inputs):
    entradas = f'{path_input}{input}.txt'
    saidas = f'{path_output}{input}_out.txt'
    print('==>', input)
    os.system(f"python3 simplex.py {entradas} {saidas}")
