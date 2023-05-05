operations = ['+', '-' , '*', '/']
folgas = ['>=', '<=']
comparisons = [*folgas, '==']
functions = ['MAX', 'MIN']

# Usando minha matrícula na esperança de garantir a unicidade do identificador 
tag_folga = 'f_2021037961_'
tag_livre = 'l_2021037961_'
tag_auxiliar = 'auxiliar_2021037961_'
tag_controle = 'CONTROL_2021037961_'

epsilon = 0.00001
precisao = 3
verbose = False
validar_certificado = False

def show(*args,**kwargs):
    if verbose:
        print(*args,**kwargs)
