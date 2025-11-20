import numpy as np
from scipy.special import erfc
import matplotlib.pyplot as plt
from scipy.optimize import least_squares
#from encontrar_parametros import encontrar_parametros

# [1] Analysis of Peukert Generalized Equations Use for Estimation of Remaining Capacity of Automotive-Grade Lithium-Ion Batteries by Nataliya N. Yazvinskaya 1,*ORCID,Mikhail S. Lipkin 2,Nikolay E. Galushkin 3ORCID and Dmitriy N. Galushkin 3
# [2] Código Peukert.m no teams (Projeto elétrico > Projetos > Projeto 2021 > Modelagem): https://cefetrjbr.sharepoint.com/:u:/s/VenturiAerodesign/EaMmT0s1MqZDjFJNO64XyX4BZpBAbGAyHWAQ1vftGOpJsw?e=df4I29
# [3] Documentação da implementação do método de otimização (por especificidade e replicabilidade, pode valer pôr no relatório): https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.least_squares.html



############ NCONTRAR PARÂMETROS ################

def encontrar_parametros(C_observado, i):
    """
    Faz uso de Mínimos Quadrados por Levenberg Marquardt, na equação 12 em [1], para estimar os parametros de peukert

    Exemplo
    Argumentos:
        - C_observado (numpy.ndarray): np.array([15.054043042538622, 25.81989538243598, 38.59230288240648])
        - i (numpy.ndarray): np.array([10, 7.5, 5])*Cm = [612.85, 459.6375, 306.425]
        - Cm_parametro = 61.285

    Retorna:
        (Cm, n, ik): [61.2850, 0.6530, 321,9] (em que a matriz é x = [3x1])
    """

    # Modelo que deve ser otimizado. Equação 12 em [1] <-- Cálculo da capacidade da bateria* 
    def modelo(params, i):
        Cm, n, ik = params  # Parâmetro a otimizar
        return ( Cm/erfc(-n) ) * erfc( ((i/ik) - 1)/(1/n) )
    

    # Residuais são apenas a diferença entre o estimado e o observado
    def residuals(params, i, C_observado):
        C_estimado = modelo(params, i)
        return C_estimado - C_observado
    
    # Dados
    Cm_parametro = 61.285
    i = np.array([10, 7.5, 5])*Cm_parametro  # Corrente como variável independente, = [612.85, 459.6375, 306.425]
    C_observado = np.array([15.054043042538622, 25.81989538243598, 38.59230288240648])  # Capacidade como variável dependente (calculada abaixo também)*
    
    # Parametros inciais (um chute ruim dos valores pode trazer vários problemas)
    params_iniciais = np.array([100, 0.5, 300])
    
    # Mínimos Quadrados por Levenberg-Marquardt (obs: Método LM é apropriado para pequenos sistemas de equações não lineares)
    resultado = least_squares(residuals, params_iniciais, args=(i, C_observado), method='lm')
    
    print("Parametros Otimizados:")
    print(f"Cm = {resultado.x[0]:.4f}")
    print(f"n = {resultado.x[1]:.4f}")
    print(f"ik = {resultado.x[2]:.4f}")
    
    print(f"Soma residual dos quadrados: {resultado.cost:.4e}")
    return resultado



############ CALCULAR CAPACIDADE DA BATERIA ################

def calculo_capacidade(Cm, i, ik, n):
    """
    Cálcula a capacidade da bateria para a menor corrente de descarga [A] (baseada na equação 12 em [1])
        - Cm : float - [A] Capacidade experimental
        - i : float - [A] Corrente de descarga
        - ik : float - [A] Corrente experimental que torna a capacidade igual a Cm/erfc(-n)
        - n : float - [Adimensional] Relação experimental que influencia na taxa de redução da capacidade

    Exemplo: 
    - Cm = 61.2850 
    - i = 5*Cm (menor valor de correte para i com base no método def acima: i (numpy.ndarray): np.array([10, 7.5, 5])*Cm)
    - n = 0.653  
    - ik = 321.9

    Retorna:
     - 38.5923
    """
    C = (Cm/erfc(-n) ) * erfc( ((i/ik) - 1)/(1/n))
    return C



############ PEUKERT ################

def peukert(n, R, i, C):
    """
    Baseado em [2]. Resulta no tempo de operação em horas, sendo seus argumentos:
        1) n float: [h] uma constante de peukert
        2) R float: [adimensional] taxa C da bateria
        3) i float: [A] corrente de operação
        4) C float: [Ah] capacidade da bateria

    Exemplo: 
    - n = 0.6530
    - R = 100
    - i = 80
    - C = 6

    Resultado:
        - 0.03733333 horas * 60 = 2.24 minutos

    """
    # TODO Validar que os tempos são válidos em horas. Se assume que se usa o tempo em horas como na capacidade e resultado da equação
    #n = (np.log10(t1)-np.log10(t2))/(np.log10(i2)-np.log10(i1)) # Cálculo de n pelo método em [2]
    R = 1/R
    t = (R*(C/R)**n) / (i**n)
    return t



############ GRÁFICO ################

def plotar():
    horizontal = np.linspace(0.1, 100, 100)
    vertical = []
    
    for j in horizontal:
        valor = peukert(0.6530, 100, j, 6)*60
        vertical.append(valor)
        if len(vertical) == 1: minimo = [j, valor]
        if len(vertical) == 50: meio = [j, valor]
        if len(vertical) == 100: maximo = [j, valor]
    
    plt.plot(horizontal, vertical)
    
    xlabel = 'corrente [A]'
    ylabel = 'duração [min]'
    
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.grid('True')
    
    plt.scatter(minimo[0], minimo[1], color='red')
    plt.text(minimo[0], minimo[1], f'({minimo[0]:.2e}, {minimo[1]:.2e})', fontsize=12, ha='left')
    plt.scatter(meio[0], meio[1], color='red')
    plt.text(meio[0], meio[1], f'({meio[0]:.2e}, {meio[1]:.2e})', fontsize=12, ha='right')
    plt.scatter(maximo[0], maximo[1], color='red')
    plt.text(maximo[0], maximo[1], f'({maximo[0]:.2e}, {maximo[1]:.2e})', fontsize=12, ha='right')
    
    plt.savefig(f'{ylabel} x {xlabel}')
    plt.show()
    
    
def main():
    
    i_descarga = 5*61.285
    
    Cm, n, ik = encontrar_parametros(np.array([612.85, 459.6375, 306.425]), np.array([612.85, 459.6375, 306.425])).x
    capacidade_A = calculo_capacidade(Cm, i_descarga, ik, n)
    duracao_h = peukert(n, 100, 80, 6)

    print(f"Capacidade bateria: {capacidade_A:.2f} Ah")
    print(f"{duracao_h*60:.2f} Minutos")
    
    plotar()

    
main()