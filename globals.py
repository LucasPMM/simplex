operations = ['+', '-' , '*', '/']
folgas = ['>=', '<=']
comparisons = [*folgas, '==']
functions = ['MAX', 'MIN']

tag_folga = 'f_'
tag_livre = 'l_'
tag_auxiliar = 'auxiliar_'
tag_controle = 'CONTROL_'

epsilon = 0.00001
precisao = 3
verbose = False
validar_certificado = False

def show(*args,**kwargs):
    if verbose:
        print(*args,**kwargs)
