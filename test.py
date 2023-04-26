import os

path = './tests/'
num_files = len([f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))])

for i in range(round(num_files/2)):
    entradas = f'{path}t{i+1}_in.txt'
    saidas = f'{path}t{i+1}_out.txt'
    os.system(f"python3 simplex.py {entradas} {saidas}")
