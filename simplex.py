import numpy as np
import re
from collections import OrderedDict

operations = ['+', '-' , '*', '/']
comparisons = ['>=', '<=', '==']
functions = ['MAX', 'MIN']

# ler arquivo de entrada e armazenar equações em lista
with open('ENTRADAS.txt', 'r') as f:
    equacoes = [linha.strip() for linha in f.readlines()]


# identificar variáveis presentes nas equações
variaveis = OrderedDict()
for eq in equacoes:
    for termo in eq.split():
        result = re.split("[+-/*]", termo)[-1]
        if result not in [*comparisons, *functions, ''] and not result[0].isdigit():
            variaveis[result] = None
objetivo = equacoes.pop(0)
# TODO: separar um array de restrições de não negatividade para não poluir o vetor b

# TODO: adicionar na lista de variáveis (pode ser feito no momento de calcular n_folgas e n_livres)
# * Folgas: f_x1, f_aux2...
# * Variáveis livres: - 2 * x1 -> - 2 * (x1 - l_x1) = - 2 * x1 + 2 * l_x1 
# (a parte positiva mantém o sinal e a parte negativa ficará com o sinal invertido)
variaveis = list(variaveis.keys())

# determinar quantidade de equações e variáveis
n_eq = len(equacoes) or 0
n_var = len(variaveis) or 0
n_folgas = len(list(filter(lambda x: x in comparisons, ' '.join(equacoes).split(' ')))) or 0
# TODO: Controlar melhor as variáveis livres
# * Considerar como não negatividade:
#   x >= 0 || - x <= 0 || -x <= NEGATIVO || x >= POSITIVO
n_livres = len(list(filter(lambda x: (f"{x} >= 0" not in equacoes and f"- {x} <= 0" not in equacoes), variaveis))) or 0

# criar matriz A e vetor b
A = np.zeros((n_eq, n_var + n_folgas + n_livres))
b = np.zeros(n_eq)

print("Variáveis: ", variaveis)
print("Função objetivo: ", objetivo)
print("Equações: ", equacoes)
print("Número de folgas: ", n_folgas)
print("Número de variáveis livres: ", n_livres)

for i, eq in enumerate(equacoes):
    termos = eq.split()
    print('Equação: ', termos)
    proximo_negativo = False
    tem_numerador = False
    fator = None
    
    # Caso seja uma condição de maior ou igual devemos inverter o sinal dos termos
    # O sistema será da forma Ax <= b, sendo apenas necessário adicionar as folgas
    inversor = -1 if '>=' in termos else 1
    for termo in termos:
        if termo in comparisons:
            valor = float(termos[termos.index(termo) + 1])
            b[i] = valor * inversor if valor != 0.0 else valor
        elif termo in operations:
            if termo == '+':
                proximo_negativo = False
                continue
            elif termo == '-':
                proximo_negativo = True
                continue
            elif termo == '*':
                continue
            elif termo == '/':
                tem_numerador = True
                continue
        elif termo.isdigit():
            if tem_numerador:
                tem_numerador = False
                fator = fator / float(termo)
                continue
            fator = float(termo)
            continue
        else:
            fator = 1 if fator == None else fator
            fator = -fator if proximo_negativo else fator
            fator = fator * inversor if fator != 0.0 else fator
            j = variaveis.index(termo)
            A[i, j] = fator
            fator = None
            continue

print(A)
print(b)