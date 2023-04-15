import numpy as np
import re
from collections import OrderedDict

operations = ['+', '-' , '*', '/']
folgas = ['>=', '<=']
comparisons = [*folgas, '==']
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

# Separando as restrições de não negatividade 
nao_negatividade = list(filter(lambda x: (f"{x} >= 0" in equacoes or f"- {x} <= 0" in equacoes), variaveis)) or []
nao_negatividade = list(map(lambda x: f"{x} >= 0" if f"{x} >= 0" in equacoes else f"- {x} <= 0", nao_negatividade))

# Tirando as restrições de não negatividade das restrições normais
equacoes = list(filter(lambda x: x not in nao_negatividade, equacoes)) or []

variaveis = list(variaveis.keys())

# Determinar quantidade de equações e variáveis
n_eq = (len(equacoes) - 1) or 0
n_var = len(variaveis) or 0

# TODO: Controlar melhor as variáveis livres
# * Considerar como não negatividade:
#   x >= 0 (ok) || - x <= 0 (ok) || -x <= NEGATIVO (?) || x >= POSITIVO (?)
variaveis_livres = list(filter(lambda x: (f"{x} >= 0" not in nao_negatividade and f"- {x} <= 0" not in nao_negatividade), variaveis))
n_livres = len(variaveis_livres) or 0
for i in variaveis_livres:
    variaveis.append('l_' + i)

# Determinando as folgas e suas variáveis
n_folgas = len(list(filter(lambda x: x in folgas, ' '.join(equacoes).split(' ')))) or 0
indices_folgas = np.where(['>=' in eq or '<=' in eq for eq in equacoes])[0]
for i in indices_folgas:
    variaveis.append('f_' + str(i))

# Criar matriz A e vetor b
A = np.zeros((n_eq, n_var + n_folgas + n_livres))
c = np.zeros(n_var + n_folgas + n_livres)
b = np.zeros(n_eq)

print("Variáveis: ", variaveis)
print("Função objetivo: ", equacoes[0])
print("Equações: ", equacoes)
print("Não negatividade: ", nao_negatividade)
print("Número de folgas: ", n_folgas)
print("Número de variáveis livres: ", n_livres)

for i, eq in enumerate(equacoes):
    termos = eq.split()
    proximo_negativo = False
    tem_numerador = False
    fator = None
    funcao_objetivo = False
    is_min = False
    # Caso seja uma condição de maior ou igual devemos inverter o sinal dos termos
    # O sistema será da forma Ax <= b, sendo apenas necessário adicionar as folgas
    inversor = -1 if '>=' in termos else 1
    for termo in termos:
        if termo in comparisons:
            # Atribuir o valor 1 as folgas da equação correspondente
            if termo in folgas:
                label_folga = 'f_' + str(i)
                j = -1
                try:
                    j = variaveis.index(label_folga)
                except ValueError:
                    pass

                if j != -1:
                    A[i-1,j] = 1

            valor = float(termos[termos.index(termo) + 1])
            b[i-1] = valor * inversor if valor != 0.0 else valor
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
        elif termo in functions:
            is_min = True if termo == 'MIN' else False
            funcao_objetivo = True
        else:
            fator = 1 if fator == None else fator
            fator = -fator if proximo_negativo else fator
            fator = fator * inversor if fator != 0.0 else fator
            j = variaveis.index(termo)

            # Verificar se a variável e livre e, caso seja, atribuir (-1)*fator a parte negativa dela 
            k = -1
            try:
                k = variaveis.index('l_' + termo)
            except ValueError:
                pass

            if funcao_objetivo:
                fator = -fator if is_min else fator
                c[j] = fator
                if k != -1:
                    c[k] = -fator
            else:
                A[i-1, j] = fator
                if k != -1:
                    A[i-1,k] = -fator
            fator = None
            continue
print('\n===============================================\n')
print(variaveis)
print('c: ', c)
print('A: ', A)
print('b: ', b)