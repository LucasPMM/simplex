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
                    valor_inicial = fator
                    fator = None
                proximo_negativo = False
                continue
            elif termo == '-':
                if fator != None:
                    fator = -fator if proximo_negativo else fator
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
                    valor_inicial = fator
            continue
        elif termo in globals.functions:
            self.minimizacao = True if termo == 'MIN' else False
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

    # Remover parênteses:
    for idx, eq in enumerate(equacoes):
        equacoes[idx] = re.sub("[()]", "", eq)

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
    restricoes_com_uma_variavel = list(filter(lambda x: _conta_variavel(x) == 1, equacoes))
    candidatas = []
    for candidata in restricoes_com_uma_variavel:
        # * Considerar como não negatividade:
        # x >= 0 || - x <= 0
        # -x <= -|| x >= +
        tokens = candidata.split()
        lados = re.split(r"(<=|>=)", candidata)
        zero = [' 0', ' - 0']
        if ('>=' in tokens and ('-' not in candidata)) or ('<=' in tokens and ('-' in lados[0] and ('-' in lados[-1] or lados[-1] in zero))):
            candidatas.append(candidata)

    nao_negatividade = []
    remover_da_pl = []

    for x in variaveis:
        for equacao in candidatas:
            if x in equacao and x not in nao_negatividade:
                nao_negatividade.append(x)
                remover_da_pl.append(f"{x} >= 0")
                remover_da_pl.append(f"{x} >= - 0")
                remover_da_pl.append(f"- {x} <= 0")
                remover_da_pl.append(f"- {x} <= - 0")

    # Tirando as restrições de não negatividade das restrições normais
    equacoes = list(filter(lambda x: x not in remover_da_pl, equacoes)) or []

    variaveis = list(variaveis.keys())

    # Determinar quantidade de equações e variáveis
    n_eq = (len(equacoes) - 1) or 0
    n_var = len(variaveis) or 0

    variaveis_livres = []
    for x in variaveis:
        if x not in nao_negatividade and x not in variaveis_livres:
            variaveis_livres.append(x)

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
    for i in range(n_eq if n_eq > 0 else 1):  
        auxiliares.append(f"{globals.tag_auxiliar}" + str(i+1))
    self.variaveis_auxiliares = [*variaveis, *auxiliares]
    self.base_viavel = [None] * (n_eq or 1)
    if self.minimizacao:
        self.c *= -1
        self.valor_inicial *= -1
