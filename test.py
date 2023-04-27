import os

path_input = './tests/in/'
path_output = './tests/out/'
num_files = len([f for f in os.listdir(path_input) if os.path.isfile(os.path.join(path_input, f))])

for i in range(num_files):
    entradas = f'{path_input}t{i+1}_in.txt'
    saidas = f'{path_output}t{i+1}_out.txt'
    os.system(f"python3 simplex.py {entradas} {saidas}")
