import numpy as np
import sys
from data_management import read_data

class Tableau:
    def __init__(self):
        self.A = []
        self.b = []
        self.c = []
        self.valor_inicial = 0.0
        self.variaveis = []

        self.tableau_auxiliar = None
        self.base_viavel = []
        self.tableau = None
        self.variaveis_basicas = []

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
        # TODO: Se for inviável retornar
        # TODO: Definir base para o problema original e retorná-la
        return
    
    def _padronizar_tableau(self, tableau, base=None):
        linhas, colunas = tableau.shape
        identidade = np.identity(linhas-1)
        # colunas-2 para ignorar a coluna do vetor b e -1 para ir até a primeira coluna
        # começa da ultima para já identificar a base do problema auxiliar
        # Obs: se a entrada for um tableau estendido, trocar -1 por linhas-2
        for j in range(colunas-2,linhas-2,-1):
            col_j = tableau[:, j]
            # TODO: tratar tablaeus com zero restrições
            candidata = np.count_nonzero(col_j[1:]) == linhas - 2 if linhas - 2 > 0 else col_j[1] != 0
            if candidata:
                i = np.nonzero(col_j[1:])[0][0] + 1
                if i != None:
                    try:
                        identidade_gerada = np.zeros(linhas-1)
                        identidade_gerada[i-1] = 1
                        identidade = np.delete(identidade, i-1, axis=1)
                        tableau = self._pivotear(tableau, i, j)
                        # self.variaveis_basicas(self.variaveis[j-1])
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
            # (3) Escolher o menor ci tal que ci < 0
            c = tableau[0][linhas:colunas-1]
            j = np.where(c == min(c))[0][0] + linhas

            # (4) Escolher a menor razão (positiva) de bj / aij
            menor_razao = float('inf')
            i = None
            for k in range(1, linhas + 1):
                b_k = tableau[k,colunas-1]
                a_kj = tableau[k,j]
                razao = -1 if a_kj == 0.0 else b_k / a_kj
                # TODO: verificar possibilidade de loopar
                # TODO: verificar os impactos do b_k = 0
                if razao >= 0 and (razao < menor_razao or menor_razao == None):
                    i = k
                    menor_razao = razao

            # (5) Pivotear o elemento aij de forma a transformar a coluna i em uma subcoluna da matriz identidade
            if i != None and j != None:
                tableau = self._pivotear(tableau, i,j)
                print('Iteração:\n ', tableau)
            else:
                print('Ilimitada!')
                return

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

        base = self._problema_auxiliar()

        tableau, tem_base_trivial = self._padronizar_tableau(tableau, base)
        self.tableau = tableau
        print('Tableau:\n', t.tableau)

        if self._check(self.tableau) and tem_base_trivial:
            print('Tableau já em estado de ótimo')
            return
        
        self.tableau = self._solve_tableau(self.tableau)

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

if __name__ == '__main__':
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    t = Tableau()
    read_data(t, input_file)
    
    print(t.variaveis)
    print('c: ', t.c)
    print('A: ', t.A)
    print('b: ', t.b)

    t.solve()
    print('Tableau resolvido:\n', t.tableau)

    t.salvar_resposta(output_file)
