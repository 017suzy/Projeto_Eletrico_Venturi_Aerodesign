import numpy as np
import matplotlib.pyplot as plt

'''
[1] Southwire power cable manual: https://www.southwire.com/medias/sys_master/installation-manuals/installation-manuals/hc5/hcd/8887676076062/Power-Cable-Installation-Guide-Southwire.pdf
[2] teste_bitola.m: https://cefetrjbr.sharepoint.com/sites/VenturiAerodesign/Documentos%20Compartilhados/Forms/DispForm.aspx?ID=1212
[3] calculator.net: https://www.calculator.net/voltage-drop-calculator.html
[4] Resistividade do cobre [(ohm*mm2)/m]: https://ucil.com.pk/2023/07/04/electrical-conductors-universal-cables/
[5] https://www.thefitoutpontoon.co.uk/electrics/voltage-drop/
[6] https://www.componentshop.co.uk/dupont-connector.html#:~:text=Contact%20spacing:%202.54mm%20/%200.1,2%20Pin
[7] https://errebishop.com/en/raster-signal-connectors-/4226-dupont-connector-male-13x2-way.html
[8] Yaskawa America - Servo Motor Sizing Basics Part 1: https://youtu.be/4MaGqSQfYOk?si=tbpo4NaSCHvJN37E
[9] Recomendado deixar a queda inferior a 4% como determinado em 6.2.7.2: NBR 5410
'''


######### RESISTIVIDADE ##############

def resistividade_temperatura(resistividade_ohm_mm2_por_m,
                              temperatura_inicial_celsius,
                              temperatura_final_celsius):
    """
    # Aproximação Linear de Resistividade
    - resistividade_temperatura_inicial * (1 + (coeficiente_temperatura_inicial * (temperatura_final - temperatura_inicial)))
    - R_1 * (1 + alpha_1 * (T_2 - T_1))
    
    2-16; formula 2-2 [1]
            
    # Exemplo (typical calculations 2-6 southwire power cable manual):
        - resistividade_ohm_mm2_por_m: 0.102
        - coeficiente_temperatura_inicial_para_material_condutor: 0.00395
        - temperatura_inicial_celsius: 25
        - temperatura_final_celsius: 90

    # Retorna:
        - 0.1281885
    """
    # Assume cobre Annealed / Recozido. Em Southwire power cable manual 2-16 [1]
    coeficiente_temperatura_inicial_para_material_condutor = 0.00395
    
    return (resistividade_ohm_mm2_por_m*
            (1 + (coeficiente_temperatura_inicial_para_material_condutor
                  *(temperatura_final_celsius - temperatura_inicial_celsius))))




######### QUEDA DE TENSÃO ##############

def queda_tensão(
    resistividade_condutor_ohm_mm2_por_m,
    corrente_maxima_A,
    comprimento_m,
    bitola_awg,
    resistencia_conexoes_ohm
    ):

    """
    Baseado em teste_bitola.m [2] e Validado com calculadora [3]

    # Exemplo
        - resistividade_ohm_mm2_por_m ( [4] otimista: 0.017241): queda_tensão(resistividade_temperatura(0.018,20,75)), ou seja, = 0.018
        - corrente_maxima_A: 2
        - comprimento_m: 2
        - bitola_awg: 14
        - resistencia_conexoes_ohm: np.array([0])
        
    # Retorna
        - 0.06946
    """

    # conversão awg para mm2
    bitola_mm = 0.127 * 92 ** ((36-bitola_awg)/39) # = 1.627726 mm                                
    area_secao_fio = np.pi * (bitola_mm/2)**2 # = 2.080906 mm²
    
    # Round trip [5]
    comprimento_m = comprimento_m*2 # = 4 
    
    # 2 lei de ohm r = pl/a
    resistencia_Ohm = (resistividade_condutor_ohm_mm2_por_m * comprimento_m) / area_secao_fio  # = 0.03460031 Ω·mm²/m
    resistencia_Ohm += np.sum(resistencia_conexoes_ohm) # 0.03473 + 0=0.03473Ω
    
    # 1 lei de ohm
    return corrente_maxima_A * resistencia_Ohm # = 0.06946V



######### FORÇAS ##############

def forca_necessaria(forca_esperada, queda_tensao, forca_maior, tensao_maior, forca_menor, tensao_menor):
    """Assume uma relação linear entre força e tensão
        - y = (m * a) + b
        
        - Se realiza um sistema com:
        - y_esperada = m(x) + b
        - y_final = m(x-queda_tensao) + b
        - Encontrando: y_final = y_esperada + m(queda_tensao)
        - Onde m = (x1- x0)/(y1 - y0)

        Ou seja, as fórmulas que iremos utilizar serão:

        1) m = (F_maior - F_menor) / (V_maior - V_menor)
        2) F_necessaria = F_esperada + |m * queda_tensao|

        como estão montadas no código abaixo
        
        # Exemplo
        - forca_esperada: 7
        - queda_tensao: 0.24
        - forca_maior (especificação): 8.93
        - tensao_maior (especificação): 6
        - forca_menor (especificação): 7.13
        - forca_maior (especificação): 4.8
        
        resultado: 7.359999999999999
    """
    m = (forca_maior - forca_menor)/(tensao_maior - tensao_menor)
    return forca_esperada + abs(m*(queda_tensao))



def forca_necessaria_final(resistividade_condutor_ohm_mm2_por_m,
                           resistencia_conexoes_ohm:np.array,
                           temperatura_inicial_celsius,
                           temperatura_final_celsius,
                           corrente_maxima_A,
                           comprimento_m,
                           bitola_awg,
                           forca_esperada,
                           forca_maior_servo,
                           tensao_maior_servo,
                           forca_menor_servo,
                           tensao_menor_servo,
                           ):
    
    """ Retorna o valor necessário para compensar a perda de carga de acordo com dimensoes e parametros dos componentes, 
    ajustados para temperatura

    # Exemplo:
    - resistividade_condutor_ohm_mm2_por_m: 1.74e-4
    - resistencia_conexoes_ohm (np.array)([6][7]): np.array([45e-3, 45e-3, 45e-3])
    - temperatura_inicial_celsius: 20
    - temperatura_final_celsius: 50
    - corrente_maxima_A: 2
    - comprimento_m: 3
    - bitola_awg: 26
    - forca_esperada: 7
    - forca_maior_servo: 8.93
    - tensao_maior_servo: 6
    - forca_menor_servo: 7.13
    - tensao_menor_servo: 4.8

    # Retorna
        7.466345986941278
    """
    
    resistividade_condutor = resistividade_temperatura(resistividade_condutor_ohm_mm2_por_m,
                                                       temperatura_inicial_celsius,
                                                       temperatura_final_celsius)
    
    resistencia_condutores = resistividade_temperatura(resistencia_conexoes_ohm,
                                                       temperatura_inicial_celsius,
                                                       temperatura_final_celsius)
    
    queda = queda_tensão(resistividade_condutor,
                 corrente_maxima_A,
                 comprimento_m,
                 bitola_awg,
                 resistencia_condutores)

    return forca_necessaria(forca_esperada,
                     queda,
                     forca_maior_servo,
                     tensao_maior_servo,
                     forca_menor_servo,
                     tensao_menor_servo)


######### PERDA DE ENRGIA E INPUTS NO TERMINAL ##############

def perda_energia(resistividade_condutor_ohm_mm2_por_m,
    corrente_maxima_A,
    comprimento_m,
    bitola_awg,
    resistencia_conexoes_ohm):
    
    perda = 1-(6-queda_tensão(resistividade_condutor_ohm_mm2_por_m,
    corrente_maxima_A,
    comprimento_m,
    bitola_awg,
    resistencia_conexoes_ohm))/6
    
    return perda*100


#Mostrar valores calculados no terminal

print(f"Perda de energia {perda_energia(0.018,
                                        1,
                                        2,
                                        20,
                                        np.array([20e-3, 20e-3, 20e-3])):.2f} %") # [6][7]

forca_final = forca_necessaria_final(0.018,
                              np.array([20e-3, 20e-3, 20e-3]),
                              20,
                              50,
                              1,
                              2,
                              20,
                              7,
                              8.93,
                              6,
                              7.13,
                              4.8)
print(f"forca final {forca_final} kg")
print(f"forca recomendada para velocidade máxima (+3/5) {forca_final*(1+3/5):.2f} kg") # [8]



############ GRÁFICO ################

horizontal = np.linspace(7.13,20, 100)
vertical = []
for i in horizontal:
    valor = forca_necessaria_final(
                              0.018,
                              np.array([20e-3, 20e-3, 20e-3]),
                              20,
                              50,
                              2,
                              3,
                              i,
                              7,
                              8.93,
                              6,
                              7.13,
                              4.8)
    vertical.append(valor)
    if len(vertical) == 1: minimo = [i, valor]
    if len(vertical) == 50: meio = [i, valor]
    if len(vertical) == 100: maximo = [i, valor]

plt.plot(horizontal, vertical)

xlabel = 'bitola awg'
ylabel = 'força necessária final'

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
