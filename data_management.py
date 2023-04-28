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

    for idx, termo in enumerate(termos):
        if termo in globals.comparisons:
            # Atribuir o valor 1 as folgas da equação correspondente
            if termo in globals.folgas:
                label_folga = globals.tag_folga + str(i)
                j = -1
                try:
                    j = variaveis.index(label_folga)
                except ValueError:
                    pass

                if j != -1:
                    A[i-1,j] = -1 if '>=' in termos else 1

            valor_final = True
            fator = None
            proximo_negativo = False

        elif termo in globals.operations:
            if termo == '+':
                if fator != None:
                    fator = -fator if proximo_negativo else fator
                    valor_inicial = -fator if is_min else fator
                    fator = None
                proximo_negativo = False
                continue
            elif termo == '-':
                if fator != None:
                    fator = -fator if proximo_negativo else fator
                    valor_inicial = -fator if is_min else fator
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
                if not valor_final and not funcao_objetivo:
                    continue
            else:
                fator = float(termo)
            if idx == len(termos) - 1:
                if valor_final and not funcao_objetivo:
                    fator = 1 if fator == None else fator
                    fator = -fator if proximo_negativo else fator
                    b[i-1] = fator
                    break
                elif funcao_objetivo:
                    fator = 0 if fator == None else fator
                    fator = -fator if proximo_negativo else fator
                    valor_inicial = -fator if is_min else fator
            continue
        elif termo in globals.functions:
            is_min = True if termo == 'MIN' else False
            funcao_objetivo = True
        elif termo in variaveis:
            fator = 1 if fator == None else fator
            fator = -fator if proximo_negativo else fator
            j = variaveis.index(termo)

            # Verificar se a variável e livre e, caso seja, atribuir (-1)*fator a parte negativa dela 
            k = -1
            try:
                k = variaveis.index(globals.tag_livre + termo)
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
        globals.show('VALOR INICIAL', valor_inicial)
        self.valor_inicial = valor_inicial

def _conta_variavel(equacao):
    contador = 0
    for termo in equacao.split():
        if termo not in [*globals.comparisons, *globals.functions, *globals.operations] and not termo.isdigit():
            contador += 1

    return contador

def read_data(self, file):
    # Ler arquivo de entrada e armazenar equações em lista
    with open(file, 'r') as f:
        equacoes = [linha.strip() for linha in f.readlines()]

    # Identificar restrições de igualdade de uma variável só e trocar por duas de >= e <=
    for i, eq in enumerate(equacoes.copy()):
        if '==' in eq and _conta_variavel(eq) == 1:
            aux1 = eq.replace('==', '<=')
            aux2 = eq.replace('==', '>=')
            equacoes.remove(eq)
            equacoes.insert(i, aux1)
            equacoes.insert(i, aux2)

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
        variaveis.append(globals.tag_livre + i)

    # Determinando as folgas e suas variáveis
    n_folgas = len(list(filter(lambda x: x in globals.folgas, ' '.join(equacoes).split(' ')))) or 0
    indices_folgas = np.where(['>=' in eq or '<=' in eq for eq in equacoes])[0]
    for i in indices_folgas:
        variaveis.append(globals.tag_folga + str(i))

    # Criar matriz A e vetor b
    A = np.zeros((n_eq, n_var + n_folgas + n_livres))
    c = np.zeros(n_var + n_folgas + n_livres)
    b = np.zeros(n_eq)

    # ====== TEST INPUT ====== #
    globals.show('*******************************************')
    globals.show("Variáveis: ", variaveis)
    globals.show("Função objetivo: ", equacoes[0])
    globals.show("Equações: ", equacoes)
    globals.show("Não negatividade: ", nao_negatividade)
    globals.show("Número de folgas: ", n_folgas)
    globals.show("Número de variáveis livres: ", n_livres)
    globals.show('*******************************************')
    # ======================== #

    for i, eq in enumerate(equacoes):
        _adicionar_restricao(self, i, eq, variaveis, A, b, c)

    self.A = A
    self.b = [0] if n_eq == 0 else b
    self.c = c
    self.variaveis = variaveis

    # Função objetivo vazia? MAX 0
    objetivo = equacoes[0] + ' 0' if equacoes[0] == 'MAX' or equacoes[0] == 'MIN' else equacoes[0]
    objetivo = objetivo.split()
    # Função objetivo sem variáveis e sem restrições? Adiciona uma variável de controle
    if len(variaveis) == 0 and n_eq == 0:
        variaveis.append(globals.tag_controle)
        self.c = np.zeros(1)
        self.A = np.ones((1,1))
    # Função objetivo com variáveis e sem restrições? Adiciona uma linha de zeros
    if len(variaveis) > 0 and variaveis[0] != globals.tag_controle and n_eq == 0:
        self.A = np.zeros((1, n_var + n_folgas + n_livres))
        
    auxiliares = []
    for i in range(n_eq):  
        auxiliares.append(f"{globals.tag_auxiliar}" + str(i+1))
    self.variaveis_auxiliares = [*variaveis, *auxiliares]
    self.base_viavel = [None] * (n_eq or 1)
