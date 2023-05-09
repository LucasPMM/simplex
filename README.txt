## Instruções: basta utilizar o seguinte comando

python3 simplex.py ENTRADAS.txt SAIDAS.txt

Infelizemente não implementei funções, então considerei um epsilon = 0.00001 definido no arquivo `globals.py`
Sendo assim, as comparações ficam da seguinte forma:
x >= 0: x >= -globals.epsilon
x <= 0: x <= globals.epsilon
x > 0: x > globals.epsilon
x < 0: x < -globals.epsilon
x == 0: -globals.epsilon <= x <= globals.epsilon

Além disso, limitei a saída a 3 casas decimais, que pode ser alterado no arquivo `globals.py` mudando a variável `precisao`