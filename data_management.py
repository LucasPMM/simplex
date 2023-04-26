import globals
import numpy as np
from collections import OrderedDict
import re

def _adicionar_restricao(self, i, eq, variaveis, A, b, c):
    termos = eq.split()
    proximo_negativo = False
    tem_numerador = False
    fator = None
    valor_final = False
    funcao_objetivo = False
    valor_inicial = 0.0
    is_min = False
    # Caso seja uma condição de maior ou igual devemos inverter o sinal dos termos
    # O sistema será da forma Ax <= b, sendo apenas necessário adicionar as folgas
    inversor = -1 if '>=' in termos else 1
    for idx, termo in enumerate(termos):
        if termo in globals.comparisons:
            # Atribuir o valor 1 as folgas da equação correspondente
            if termo in globals.folgas:
                label_folga = 'f_' + str(i)
                j = -1
                try:
                    j = variaveis.index(label_folga)
                except ValueError:
                    pass

                if j != -1:
                    A[i-1,j] = 1

            valor_final = True
            fator = None

        elif termo in globals.operations:
            if termo == '+':
                if fator != None:
                    fator = -fator if proximo_negativo else fator
                    fator = fator * inversor if fator != 0.0 else fator
                    valor_inicial = fator
                    fator = None
                proximo_negativo = False
                continue
            elif termo == '-':
                if fator != None:
                    fator = -fator if proximo_negativo else fator
                    fator = fator * inversor if fator != 0.0 else fator
                    valor_inicial = fator
                    fator = None
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
                fator = 0.0 if float(termo) == 0.0 else fator / float(termo)
                if not valor_final:
                    continue
            else:
                fator = float(termo)
            if idx == len(termos) - 1:
                if valor_final and not funcao_objetivo:
                    fator = 1 if fator == None else fator
                    fator = -fator if proximo_negativo else fator
                    fator = fator * inversor if fator != 0.0 else fator
                    b[i-1] = fator
                    break
                elif funcao_objetivo:
                    fator = 0 if fator == None else fator
                    fator = -fator if proximo_negativo else fator
                    fator = fator * inversor if fator != 0.0 else fator
                    valor_inicial = fator
            continue
        elif termo in globals.functions:
            is_min = True if termo == 'MIN' else False
            funcao_objetivo = True
        elif termo in variaveis:
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
    if funcao_objetivo:
        print('VALOR INICIAL', valor_inicial)
        self.valor_inicial = valor_inicial

def read_data(self, file):
    # ler arquivo de entrada e armazenar equações em lista
    with open(file, 'r') as f:
        equacoes = [linha.strip() for linha in f.readlines()]

    # identificar variáveis presentes nas equações
    variaveis = OrderedDict()
    for eq in equacoes:
        for termo in eq.split():
            result = re.split("[+-/*]", termo)[-1]
            if result not in [*globals.comparisons, *globals.functions, ''] and not result[0].isdigit():
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
    n_folgas = len(list(filter(lambda x: x in globals.folgas, ' '.join(equacoes).split(' ')))) or 0
    indices_folgas = np.where(['>=' in eq or '<=' in eq for eq in equacoes])[0]
    for i in indices_folgas:
        variaveis.append('f_' + str(i))

    # Criar matriz A e vetor b
    A = np.zeros((n_eq, n_var + n_folgas + n_livres))
    c = np.zeros(n_var + n_folgas + n_livres)
    b = np.zeros(n_eq)

    # ====== TEST INPUT ====== #
    print('*******************************************')
    print("Variáveis: ", variaveis)
    print("Função objetivo: ", equacoes[0])
    print("Equações: ", equacoes)
    print("Não negatividade: ", nao_negatividade)
    print("Número de folgas: ", n_folgas)
    print("Número de variáveis livres: ", n_livres)
    print('*******************************************')
    # ======================== #

    for i, eq in enumerate(equacoes):
        _adicionar_restricao(self, i, eq, variaveis, A, b, c)
    # TODO: Se A não tiver restrições, colocar uma linhas de 0's
    self.A = np.zeros((1, n_var + n_folgas + n_livres)) if n_eq == 0 else A
    self.b = [0] if n_eq == 0 else b
    self.c = c
    self.variaveis = variaveis
