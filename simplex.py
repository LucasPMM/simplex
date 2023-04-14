import numpy as np
import re

# ler arquivo de entrada e armazenar equações em lista
with open('ENTRADAS.txt', 'r') as f:
    equacoes = [linha.strip() for linha in f.readlines()]

objetivo = equacoes.pop(0)
print(objetivo)
print(equacoes)
# identificar variáveis presentes nas equações
variaveis = set()
for eq in equacoes:
    for termo in eq.split():
        result = re.split("[+-/*]", termo)[-1]
        if result not in ['>=', '<=', ''] and not result[0].isdigit():
            variaveis |= set([result])

# determinar quantidade de equações e variáveis
n_eq = len(equacoes)
n_var = len(variaveis)
print("Variáveis: ", list(variaveis))
# criar matriz A e vetor b
A = np.zeros((n_eq, n_var))
b = np.zeros(n_eq)
for i, eq in enumerate(equacoes):
    termos = eq.split()
    print('termos: ', termos)
    proximo_negativo = False
    for termo in termos:
        if termo in ['==', '>=', '<=']:
            b[i] = float(termos[termos.index(termo) + 1])
        elif termo in ['+', '-']:
            if termo == '-':
                proximo_negativo = True
                continue
        else:
            print('procurando termo: ', termo, list(variaveis))
            j = list(variaveis).index(termo)
            print('j', j, termos.index(termo))
            A[i, j] = (-1.0 if proximo_negativo else 1.0) * float(termos[termos.index(termo) - 1])
       

print(A)
print(b)