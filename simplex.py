import numpy as np
import sys
import re
from collections import OrderedDict

# TODO: resolver uma PL auxiliar caso uma ótima não base não seja trivial
# Na PL auxiliar o b >= 0 (multiplicar por -1 a linha em que bi < 0)

operations = ['+', '-' , '*', '/']
folgas = ['>=', '<=']
comparisons = [*folgas, '==']
functions = ['MAX', 'MIN']

class Tableau:
    def __init__(self):
        self.A = []
        self.b = []
        self.c = []
        self.tableau = None
        self.variaveis = []

    def _adicionar_restricao(self, i, eq, variaveis, A, b, c):
        termos = eq.split()
        proximo_negativo = False
        tem_numerador = False
        fator = None
        valor_final = False
        funcao_objetivo = False
        is_min = False
        # Caso seja uma condição de maior ou igual devemos inverter o sinal dos termos
        # O sistema será da forma Ax <= b, sendo apenas necessário adicionar as folgas
        inversor = -1 if '>=' in termos else 1
        for idx, termo in enumerate(termos):
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

                valor_final = True
                fator = None

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
                    if not valor_final:
                        continue
                else:
                    fator = float(termo)
                if valor_final and idx == len(termos) - 1:
                    fator = 1 if fator == None else fator
                    fator = -fator if proximo_negativo else fator
                    fator = fator * inversor if fator != 0.0 else fator
                    b[i-1] = fator
                    break
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

    def read_data(self, file):
        # ler arquivo de entrada e armazenar equações em lista
        with open(file, 'r') as f:
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
            self._adicionar_restricao(i, eq, variaveis, A, b, c)
        self.A = A
        self.b = b
        self.c = c
        self.variaveis = variaveis

    def montar_tableau(self):
        linhas, colunas = self.A.shape
        tableau_dash = np.zeros((linhas, colunas + linhas + 1))
        c_dash = np.concatenate(([np.zeros(linhas)], [(self.c * -1)], [np.zeros(1)]), axis=1)
        tableau_dash = np.concatenate((np.identity(linhas), self.A, np.array(self.b).reshape(-1, 1)), axis=1)
        tableau = np.concatenate((c_dash, tableau_dash), axis=0)
        self.tableau = tableau

    def _check(self):
        linhas, _ = self.A.shape
        _, colunas = self.tableau.shape
        c = self.tableau[0][linhas:colunas-1]
        if min(c) >= 0: 
            return True
        return False

    def _pivotear(self, i, j):
        n = self.tableau.shape[0]
        self.tableau[i] /= self.tableau[i, j] # divide a linha i pela entrada ij
        for k in range(n):
            if k == i:
                continue
            self.tableau[k] -= self.tableau[i] * self.tableau[k, j] # subtrai um múltiplo da linha i da linha k

    def _problema_auxiliar(self):
        # Econtra uma base viável
        # Coloca o tableau original na forma canonica
        linhas, colunas = self.A.shape
        tableau_dash = np.zeros((linhas, colunas + linhas + 1))
        b_dash = self.b
        A_dash = self.A
        for i, b_i in enumerate(b_dash):
            if b_i <= 0:
                A_dash[i] = A_dash[i] * -1
                b_dash[i] = b_dash[i] * -1

        c_dash = np.concatenate(([np.zeros(len(self.c))], [np.ones(linhas) * (-1)], [np.zeros(1)]), axis=1)
        tableau_dash = np.concatenate((A_dash, np.identity(linhas), np.array(b_dash).reshape(-1, 1)), axis=1)
        tableau = np.concatenate((c_dash, tableau_dash), axis=0)
        print('Tableau auxiliar:\n', tableau)

        return
    
    def _padronizar_tableau(self):
        linhas, colunas = self.tableau.shape
        identidade = np.identity(linhas-1)
        for j in range(colunas-1,linhas-2,-1):
            col_j = self.tableau[:, j]
            # TODO: tratar tablaeus com zero/uma restrição
            candidata = np.count_nonzero(col_j[1:]) == linhas - 2
            i = np.nonzero(col_j[1:])[0][0] + 1
            if candidata:
                self._pivotear(i, j)
                identidade_gerada = np.zeros(linhas-1)
                identidade_gerada[i-1] = 1
                identidade = np.delete(identidade, i-1, axis=1)
                # Se já completou a base trivial pode parar o loop
                if identidade.shape[1] == 0:
                    break

        print('Tableau canonico:\n', self.tableau)
        tem_base_trivial = identidade.shape[1] == 0
        return tem_base_trivial

    def solve(self):
        # (1) Colocar o tableau em forma canonica (zerar as variáveis ci correspondentes as variáveis básicas)
        tem_base_trivial = self._padronizar_tableau()
        # (2) Econtrar uma base viável caso necessário (PL auxiliar)
        if not tem_base_trivial:
            self._problema_auxiliar()
    
        linhas, _ = self.A.shape
        _, colunas = self.tableau.shape
        while not self._check():
            # (3) Escolher o menor ci tal que ci < 0
            c = self.tableau[0][linhas:colunas-1]
            j = np.where(c == min(c))[0][0] + linhas
            
            # (4) Escolher a menor razão (positiva) de bj / aij
            menor_razao = float('inf')
            i = None
            for k in range(1, linhas + 1):
                b_k = self.tableau[k,colunas-1]
                a_kj = self.tableau[k,j]
                razao = b_k / a_kj
                # TODO: verificar possibilidade de loopar
                if razao >= 0 and (razao <= menor_razao or menor_razao == None):
                    i = k
                    menor_razao = razao

            # (5) Pivotear o elemento aij de forma a transformar a coluna i em uma subcoluna da matriz identidade
            self._pivotear(i,j)

    def salvar_resposta(self, file):
        tableau = self.tableau
        otimo = tableau[0,-1]
        linhas, colunas = tableau.shape
        with open(file, "w") as arquivo:
            if otimo >= 0:
                arquivo.write("Status: otimo\n")
                arquivo.write(f"Objetivo: {otimo}\n")
                arquivo.write("Solucao:\n")
                solucao = ''
                for i in tableau[0][linhas-1:colunas-1]:
                    solucao += f"{i} "
                arquivo.write(f"{solucao}\n")
                arquivo.write("Certificado:\n")
                certificado = ''
                for i in tableau[0][0:linhas-1]:
                    certificado += f"{i} "
                arquivo.write(f"{certificado}")
            elif otimo < 0:
                print('solução inviável')
            # TODO: como saber se é ilimitada?
            # for linha in self.x:

if __name__ == '__main__':
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    t = Tableau()
    t.read_data(input_file)
    
    print(t.variaveis)
    print('c: ', t.c)
    print('A: ', t.A)
    print('b: ', t.b)

    t.montar_tableau()
    print('Tableau:\n', t.tableau)

    t.solve()
    print('Tableau resolvido:\n', t.tableau)

    t.salvar_resposta(output_file)


# Testar: 

# Problema "identidade" (multiplas bases viáveis possíveis):
# Ex1:
# MAX x1 + x2 + x3
# x1 <= 3
# x2 <= 3
# x3 <= 3
# x >= 0
#     x1 x2 x3 f1 f2 f3 b
#  [[ 0  0  1  1  1  1  0]
#   [ 1  0  0  1  0  0  3]
#   [ 0  1  0  0  1  0  3]
#   [ 0  0  1  0  0  1  3]]

# Problema "degenerado":
# Ex1:
# MAX

# Ex2:
# MAX x1 + x2

# Ex3:
# MAX
# x1 + x2 <= 10

# Ex4:
# MAX x1 + x2
# x3 + x4 >= 4