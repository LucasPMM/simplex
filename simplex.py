import numpy as np
import sys
from data_management import read_data
import globals

class Tableau:
    def __init__(self):
        self.A = []
        self.b = []
        self.c = []
        self.valor_inicial = 0.0
        self.variaveis = []
        self.output_file = None

        self.tableau_auxiliar = None
        self.variaveis_auxiliares = []

        self.base_viavel = []
        self.tableau = None

    def _check(self, tableau):
        linhas, colunas = tableau.shape
        linhas -= 1
        c_t = [tableau[0][0]] if colunas-1 == 0 else tableau[0][linhas:colunas-1]
        if min(c_t) >= 0: 
            return True
        return False

    def _pivotear(self, tableau, i, j):
        n = tableau.shape[0]
        tableau[i] = (tableau[i] / tableau[i, j]) if (tableau[i, j] != 0).any() else 0.0 # divide a linha i pela entrada ij
        for k in range(n):
            if k == i:
                continue
            tableau[k] -= tableau[i] * tableau[k, j] # subtrai um múltiplo da linha i da linha k
        return tableau

    def _problema_auxiliar(self):
        # Encontra uma base viável
        # Coloca o tableau original na forma canonica
        linhas, colunas = self.A.shape
        tableau_dash = np.zeros((linhas, colunas + linhas + 1))
        b_dash = self.b
        A_dash = self.A
        for i, b_i in enumerate(b_dash):
            if b_i <= 0:
                A_dash[i] = A_dash[i] * -1
                b_dash[i] = b_dash[i] * -1

        certificados = np.zeros(linhas)
        certificados = np.concatenate(([certificados], np.identity(linhas)), axis=0)
        # Como o vetor c é invertido no tableau, colocamos 1's no lugar dos -1's
        c_dash = np.concatenate(([np.zeros(len(self.c))], [np.ones(linhas) * (1)], np.array(self.valor_inicial).reshape(-1, 1)), axis=1)
        tableau_dash = np.concatenate((A_dash, np.identity(linhas), np.array(b_dash).reshape(-1, 1)), axis=1)
        tableau = np.concatenate((c_dash, tableau_dash), axis=0)
        tableau = np.concatenate((certificados, tableau), axis=1)

        print('Tableau auxiliar:\n', tableau)
        tableau, _ = self._padronizar_tableau(tableau)
        print('Tableau auxiliar padronizado:\n', tableau)

        self.tableau_auxiliar = self._solve_tableau(tableau)
        print('Tableau auxiliar otimo:\n', self.tableau_auxiliar)

        linhas, colunas = self.tableau_auxiliar.shape
        otimo = self.tableau_auxiliar[linhas-1][colunas-1]
        if otimo < 0:
            self.simplex_inviavel(self.tableau_auxiliar)
        print('BASE FINAL: ', self.base_viavel)

        # Se usa alguma variável auxiliar => substituir por alguma não básica
        base_otima = self.base_viavel
        for idx, variavel in enumerate(self.base_viavel):
            if globals.tag_auxiliar in variavel:
                disponiveis = list(filter(lambda x: x not in base_otima, self.base_viavel)) or []
                base_otima[idx] = disponiveis[0]
        self.base_viavel = base_otima
        return base_otima
    
    def _padronizar_tableau(self, tableau, base=None):
        linhas, colunas = tableau.shape
        identidade = np.identity(linhas-1)

        if base != None:
            for idx, variavel in enumerate(base):
                j = self.variaveis_auxiliares.index(variavel)
                tableau = self._pivotear(tableau, idx + 1, j + linhas-1)

            # Retornando True pois o tableau já está na forma canonica
            return tableau, True

        # colunas-2 para ignorar a coluna do vetor b e -1 para ir até a primeira coluna
        # começa da ultima para já identificar a base do problema auxiliar
        for j in range(colunas-2,linhas-2,-1):
            col_j = tableau[:, j]
            candidata = np.count_nonzero(col_j[1:]) == 1
            if candidata:
                i = np.nonzero(col_j[1:])[0][0] + 1
                if i != None:
                    try:
                        identidade_gerada = np.zeros(linhas-1)
                        identidade_gerada[i-1] = 1
                        identidade = np.delete(identidade, i-1, axis=1)
                        tableau = self._pivotear(tableau, i, j)

                        entra_na_base = self.variaveis_auxiliares[j-(linhas-1)]
                        sai_da_base = self.base_viavel[i-1]
                        print('Sai da base: ', sai_da_base, ". Entra na base: ", entra_na_base)
                        self.base_viavel[i-1] = entra_na_base

                    except IndexError:
                        pass
                if identidade.shape[1] == 0:
                    break
        tem_base_trivial = identidade.shape[1] == 0
        return tableau, tem_base_trivial

    def _solve_tableau(self, tableau):
        linhas, colunas = tableau.shape
        linhas = linhas - 1

        while not self._check(tableau):
            # Escolher o ci de menor indice tal que ci < 0 (Regra de Bland)
            c = tableau[0][linhas:colunas-1]
            j = linhas
            for idx, ci in enumerate(c):
                if ci < 0:
                    j += idx
                    break

            # Escolher a menor razão (positiva) de bj / aij
            menor_razao = float('inf')
            i = None
            for k in range(1, linhas + 1):
                b_k = tableau[k,colunas-1]
                a_kj = tableau[k,j]
                # TODO: perguntar o professor se devemos avaliar o caso em que bk = 0 e akj < 0
                razao = -1 if a_kj == 0.0 or (a_kj < 0 and b_k == 0.0) else b_k / a_kj
                # TODO: verificar possibilidade de loopar
                # TODO: verificar os impactos do b_k = 0
                #  razao < menor_razao e não <= para priorizar os menores indices
                if razao >= 0 and (razao < menor_razao or menor_razao == None):
                    i = k
                    menor_razao = razao

            # Pivotear o elemento aij de forma a transformar a coluna i em uma subcoluna da matriz identidade
            if i != None and j != None:
                tableau = self._pivotear(tableau, i,j)
                entra_na_base = self.variaveis_auxiliares[j-linhas]
                sai_da_base = self.base_viavel[i-1]
                print('Solving: Sai da base: ', sai_da_base, ". Entra na base: ", entra_na_base)
                self.base_viavel[i-1] = entra_na_base

                print('Iteração:\n ', tableau)
            else:
                self.simplex_ilimitado(tableau)

        return tableau


    def solve(self):
        linhas, colunas = self.A.shape
        certificados = np.zeros(linhas)
        certificados = np.concatenate(([certificados], np.identity(linhas)), axis=0)

        tableau_dash = np.zeros((linhas, colunas + linhas + 1))
        c_dash = np.concatenate(([(self.c * -1)], np.array(self.valor_inicial).reshape(-1, 1)), axis=1)
        tableau_dash = np.concatenate((self.A, np.array(self.b).reshape(-1, 1)), axis=1)
        tableau = np.concatenate((c_dash, tableau_dash), axis=0)
        # Montando o tableau estendido ANTES colocá-lo na forma canônica
        tableau = np.concatenate((certificados, tableau), axis=1)
       
        print('Tableau inicial:\n', tableau)
        tableau, tem_base_trivial = self._padronizar_tableau(tableau)
        print('Tableau padronizado:\n', tableau)
        print('Base trivial:\n', tem_base_trivial, self.base_viavel)

        # Checar se já é ótimo:
        if self._check(tableau) and tem_base_trivial:
            self.simplex_otimo(tableau)

        # Checar se A = 0 => problema ilimitado: (como já foi checada a otimalidade, só pode ser ilimitada)
        if np.all(self.A == 0):
            self.simplex_ilimitado(self.tableau)

        # Setar as novas variáveis como a base da PL auxiliar
        self.base_viavel = self.variaveis_auxiliares[-linhas:]
        base = self._problema_auxiliar()

        tableau, tem_base_trivial = self._padronizar_tableau(tableau, base)
        self.tableau = tableau
        print('Tableau na base viável:\n', t.tableau)
     
        # Checar novamente se já é ótimo:
        if self._check(self.tableau) and tem_base_trivial:
            self.simplex_otimo(self.tableau)
        
        self.tableau = self._solve_tableau(self.tableau)
        self.simplex_otimo(self.tableau)

    def simplex_otimo(self, tableau):
        print('Tableau OTIMO:\n', tableau)
        linhas, _ = tableau.shape
        otimo = tableau[0,-1]
        
        with open(self.output_file, "w") as arquivo:
            arquivo.write("Status: otimo\n")
            arquivo.write(f"Objetivo: {otimo}\n")
            arquivo.write("Solucao:\n")
            solucao = ''
            for i, variavel in enumerate(self.variaveis):
                if variavel in self.base_viavel:
                    idx = self.base_viavel.index(variavel)
                    solucao += f"{tableau[idx+1,-1]} "
                else:
                    solucao += "0.0 "
            arquivo.write(f"{solucao}\n")
            arquivo.write("Certificado:\n")
            certificado = ''
            for i in tableau[0][0:linhas-1]:
                certificado += f"{i} "
            arquivo.write(f"{certificado}")
        sys.exit()

    def simplex_inviavel(self, tableau):
        print('Tableau INVIAVEL:\n', tableau)
        linhas, _ = tableau.shape
        
        with open(self.output_file, "w") as arquivo:
            arquivo.write("Status: inviavel\n")
            arquivo.write("Certificado:\n")
            certificado = ''
            for i in tableau[0][0:linhas-1]:
                certificado += f"{i} "
            arquivo.write(f"{certificado}")
        sys.exit()

    def simplex_ilimitado(self, tableau):
        print('Tableau ILIMITADO:\n', tableau)
        linhas, colunas = tableau.shape
        
        with open(self.output_file, "w") as arquivo:
            arquivo.write("Status: ilimitado\n")
            arquivo.write("Certificado:\n")
            certificado = ''
            for _, variavel in enumerate(self.variaveis):
                if None not in self.base_viavel:
                    idx_col = self.variaveis.index(variavel)
                    fail_idx = None
                    c = tableau[0][linhas-1:colunas-1]
                    for index, ci in enumerate(c):
                        if ci < 0:
                            fail_idx = index
                            break
                    if variavel in self.base_viavel:
                        # Variáveis básicas recebem os valores da coluna que falhou
                        idx = self.base_viavel.index(variavel)
                        if fail_idx != None:
                            certificado += f"{abs(tableau[idx+1,fail_idx+linhas-1])} "
                    elif tableau[0][idx_col+linhas-1] < 0:
                        # A variavel que falhou entra como 1.0. Ela será o primeiro ci negativo
                        certificado += "1.0 "
                    else:
                        # Variáveis não básicas entram como 0.0
                        certificado += "0.0 "
                else:
                    # Caso não tenha encontrado uma base viável, o certificado é composto por 0's
                    certificado += "0.0 "

            arquivo.write(f"{certificado}")
        sys.exit()

if __name__ == '__main__':
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    t = Tableau()
    t.output_file = output_file
    read_data(t, input_file)
    
    print(t.variaveis)
    print('c: ', t.c)
    print('A: ', t.A)
    print('b: ', t.b)

    t.solve()
