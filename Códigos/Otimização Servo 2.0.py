import numpy as np
from scipy.optimize import minimize
import matplotlib.pyplot as plt

# Baseado em https://automaticaddison.com/how-to-determine-what-torque-you-need-for-your-servo-motors/

# Valor Padrão. Em São José será por volta de 0.002 m/s2 menor devido a altitude https://en.wikipedia.org/wiki/Standard_gravity
gravidade_ms2 = 9.80665



################ CÁLCULO DE TORQUE RESULTANTE ################

def torque_carga_max(massa_kg, distancia_centro_massa_m):
    """
    torque_N_m = massa_kg * gravidade_ms2 * distancia_centro_massa_m
    
    - Se possível pode ser efetivamente zero ao se posicionar o horn no centro de massa da superfície
    - Assume a força peso perpendicular a superfície. A situação com maior torque
    
    # Exemplo:
    - massa_kg: 1
    - distancia_centro_massa_m: 0.1
    
    ## Retorna
        0.980665
    """
    
    peso_superficie = massa_kg*gravidade_ms2
    return (peso_superficie*
            distancia_centro_massa_m*
            np.sin(np.pi/2)) # np.sin(np.pi/2) = 1


def torque_links_max(massa_kg, distancias_m):
    """
    Fórmula assume o centro de massa do link no meio da largura do link:
        - (1/2) * g * m_n * r_n
            - g: gravidade
            - m_n: Massa de um dado link
            - r_n: Largura de um dado link
    
    # Exemplo:
        massa_kg (np.array): np.array([0.04, 0.08, 0.06])
        distancias_m (np.array): np.array([0.075, 0.3, 0.075])
    
    ## Retorna
        0.1544547375
    """
    
    return np.sum(
                (1/2)*
                gravidade_ms2*
                massa_kg*
                distancias_m)


def torque_max_pontos_rotacao(massa_kg, distancias_m):
    """Determinado a partir da formula:
    - torque = (gravidade * massa) + extensao

    - Pode ser usado o array com as distancias dos links, mesmo ele possuindo um tamanho maior, dado que o 
    código o ajusta o tamanho das listas

    # Exemplo:
        massa_kg (np.array): np.array([0.001, 0.001])
        distancias_m (np.array): np.array([0.075, 0.3, 0.075])

    ## Retorna:
       Torque=(0.001*9.80665*0.075)+(0.001*9.80665*0.3) = 0.00367749375
    """
    return np.sum([massa_kg*
                gravidade_ms2*
                distancias_m[:(len(massa_kg))]]) # ajusta o array com um slice para a quantidade de pontos de rotação


def torque_resultante(massa_superficie_kg,
                      distancia_centro_massa_m,
                      massa_links_kg, distancias_links_m,
                      massa_pontos_rotacao_kg):
    """
    # Exemplo:
        massa_superficie_kg: 0.3
        distancia_centro_massa_m: 0.1
        massa_links_kg (np.array): np.array([0.04, 0.08, 0.06])
        distancias_links_m (np.array): np.array([0.075, 0.3, 0.075])
        massa_pontos_rotacao_kg (np.array): np.array([0.001, 0.001])

    ## Retorna:
        0.45233173125
    """
    return np.sum(
               [torque_carga_max(massa_superficie_kg, distancia_centro_massa_m),
               torque_links_max(massa_links_kg, distancias_links_m),
               torque_max_pontos_rotacao(massa_pontos_rotacao_kg, distancias_links_m)])



################ CÁLCULO DE MOMENTO RESULTANTE ################

def momento_servomotor(raio_conexao_motor_m, massa_conexao_motor_kg):
    """
    - Assume que essa conexão é um anel (superdimensionado ao consider que o raio externo forma vãos, como em um dissipador de calor) com momento de formula:
        - I = m.R^2

    # Retorna:
    - (numeric): Momento do componente em formato de anel que conecta o motor do servo ao braço do servo 
    
    # Exemplo:
        raio_conexao_motor_m: 0.05
        massa_conexao_motor_kg: 0.05

    ## Retorna:
        0.0006129156250000001
    """
    return (1/2*
            massa_conexao_motor_kg*
            gravidade_ms2*
            raio_conexao_motor_m**2)


def momento_links(massa_kg, distancias_m):
    """
    - Assume momento em uma barra fina / Haste delgada na extremidade de formula:
        - I = (1/3).M.L^2
    
    # Exemplo:
    
        massa_kg (np.array): np.array([0.04, 0.08, 0.06])
        distancias_m (np.array): np.array([0.075, 0.3, 0.075]) 
    
    ## Retorna:
        0.0025875
    """

    return np.sum((1/3)*
                (massa_kg)*
                (distancias_m**2))


def momento_superficie(massa_kg, lado_a_m, lado_b_m):
    """
    - Assume que o momento na superfície se manifesta como em uma barra fina com fórmula:
        - I = (M/3)(a^2+b^2)
            - Onde 'a' e 'b' são os lados, dada uma superfície retangular
            
    Exemplo:
        massa_superficie_kg = 0.3
        lado_a_m = 0.1
        lado_b_m = 0.5
    
    Retorna:
        0.026
    """
    
    return (massa_kg/3)*(
            (lado_a_m**2)+
            (lado_b_m**2))

def momento_resultante(massa_superficie_kg,
                       lado_a_m,
                       lado_b_m,
                       massa_links_kg,
                       distancia_links_kg,
                       raio_conexao_motor_m,
                       massa_conexao_motor_kg):
    """
    - Cálcula e soma os momentos
        
    # Exemplo:
        massa_superficie_kg: 0.3
        lado_a_m: 0.1
        lado_b_m: 0.5
        massa_links_kg (np.array): np.array([0.04, 0.08, 0.06])
        distancia_links_kg (np.array) = np.array([0.075, 0.3, 0.075])
        raio_conexao_motor_m: 0.05
        massa_conexao_motor_kg: 0.05

    ## Retorna:
        0.029200415625
    """
    return (momento_superficie(massa_superficie_kg, lado_a_m, lado_b_m)+
            momento_links(massa_links_kg, distancia_links_kg)+
            momento_servomotor(raio_conexao_motor_m, massa_conexao_motor_kg))

print(f"momento resultante: {momento_resultante(0.3,
                                                0.1,
                                                0.5,
                                                np.array([0.04, 0.08, 0.06]), 
                                                np.array([0.075, 0.3, 0.075]),
                                                0.005,
                                                0.005)}")



################ MOMENTO DO TORQUE RESULTANTE, TORQUE TOTAL E RESULTANTE ################

def torque_resultante_momento(
                               massa_superficie_kg,
                               lado_a_m,
                               lado_b_m, 
                               massa_links_kg,
                               raio_conexao_motor_m,
                               massa_conexao_motor_kg,
                               velocidade_servo_60_graus_por_seg #Esses parâmetros serão utilizados na var momento abaixo
                               ):
    """
    Baseado no documento a seguir, em F-4, Start-Stop Operation: https://www.orientalmotor.com/products/pdfs/F_TecRef/TecMtrSiz.pdf. 
    Oriental Motor, Technical Reference, Motor Sizing Calculations
    
    Onde há duas considerações sobre a fórmula no documento:
    1. A fórmula não está em métrico e o momento é convertido para o sistema na fórmula. E com isso o resultado é convertido de volta para Nm
    2. f_2 Pulse Speed [Hz] é estimado a partir da especificação de velocidade sec/60° do servo

    
    FÓRMULAS:
       - Momento resultante:
       M_total = M_superficie + M_links + M_conexao_motor

       - Momento da superfície:
         M_superficie = f(massa_superficie_kg, lado_a_m, lado_b_m)

       - Momento dos links:
         M_links = Σ(massa_link_i * g * distancia_link_i)/ 2

       - Momento da conexão do motor (anel):
         M_conexao_motor = (1/2) * m * g * R²


    # Exemplo:
        - massa_superficie_kg: 0.3
        - lado_a_m: 0.1
        - lado_b_m: 0.5
        - massa_links_kg: (np.array): np.array([0.04, 0.08, 0.06])
        - raio_conexao_motor_m: 0.05
        - massa_conexao_motor_kg: 0.05
        - momento_pontual_N_m: 0
        - velocidade_servo_60_graus_por_seg: 0.11

    ## Retorna: 0.0004312594693708283
    """
    
    momento = momento_resultante(massa_superficie_kg,
                               lado_a_m,
                               lado_b_m, 
                               massa_links_kg,
                               raio_conexao_motor_m,
                               raio_conexao_motor_m,
                               massa_conexao_motor_kg
                               )
    
    conversao_onin2_kgcm2 = 0.00001828997852042 # https://www.translatorscafe.com/unit-converter/en-US/moment-of-inertia/7-1/ounce%20inch%C2%B2-kilogram%20meter%C2%B2/
    conversao_ozin_Nm = 0.0070615518333333 # https://www.convertunits.com/from/oz-in/to/N-m
    
    return conversao_ozin_Nm*((momento/conversao_onin2_kgcm2) 
                              * (np.pi*0.72*1)*((1/(velocidade_servo_60_graus_por_seg*6))**2)/(90*3.6) * 1/(12*32))




def torque_total_kg_cm(
                massa_superficie_kg,
                distancia_centro_massa_m,
                massa_links_kg,
                distancias_links_m,
                massa_pontos_rotacao_kg,
                lado_a_m,
                lado_b_m,
                raio_conexao_motor_m,
                massa_conexao_motor_kg,
                velocidade_servo_60_graus_por_seg
                ):
    """
    # Exemplo:

        Torque_total = Torque_resultante + Momento_resultante
    
        massa_superficie_kg: 0.3
        distancia_centro_massa_m: 0.1
        massa_links_kg: np.array([0.04, 0.08, 0.06])
        distancias_links_m: np.array([0.075, 0.3, 0.075])
        massa_pontos_rotacao_kg: np.array([0.001, 0.001])
        lado_a_m: 0.1
        lado_b_m: 0.5
        raio_conexao_motor_m: 0.05
        massa_conexao_motor_kg: 0.05
        momento_pontual_N_m: 0
        velocidade_servo_60_graus_por_seg: 0.11
    
    ## Retorna:
        4.6168976227290495
    """
    
    fator_conversao_Nm_kg_cm = 10.197162129779 # https://www.convertunits.com/from/N-m/to/kg-cm
    return ((torque_resultante(
                            massa_superficie_kg,
                            distancia_centro_massa_m,
                            massa_links_kg,
                            distancias_links_m,
                            massa_pontos_rotacao_kg)+
            torque_resultante_momento(massa_superficie_kg,
                                      lado_a_m,
                                      lado_b_m,
                                      massa_links_kg,
                                      raio_conexao_motor_m,
                                      massa_conexao_motor_kg,
                                      velocidade_servo_60_graus_por_seg))*
            fator_conversao_Nm_kg_cm)


def fator_segurança():
    """
    # Subdimensionamentos:
    - 0.5 Falta de validação empírica
    - 0.2 Resistência do ar e outros efeitos aerodinamicos
    - 0.01 Momento dos pontos de movimento
    - potencial: posição e efeitos do momento pontual
    - potencial: dados e fatores de correcao empiricos
    
    # Superdimensionamentos:
    - 0.1 Momento gerado pela geometria de certos objetos
    - 0.2 Perda de velocidade de acordo com o esforço em que ele está sujeito
    """
    return (1/3)+1

#Mostrar valores calculados no terminal

print(f"Torque Total kgcm (com fator segurança): {fator_segurança()*
      torque_total_kg_cm(
             0.3,
             0.1,
             np.array([0.04, 0.08, 0.06]),
             np.array([0.075, 0.3, 0.075]),
             np.array([0.001, 0.001]),
             0.1,
             0.5,
             0.05,
             0.05,
             0.11)}")

print(f"Torque resultante kgcm: {10.197162129779*torque_resultante(
      0.3,
      0.1,
      np.array([0.04, 0.08, 0.06]),
      np.array([0.075, 0.3, 0.075]),
      np.array([0.001, 0.001]))}\nTorque resultante momento kgcm: {10.197162129779*torque_resultante_momento(0.3,
      0.1,
      0.5,
      np.array([0.04, 0.08, 0.06]),
      0.05,
      0.05,
      0.11)}")


################ GRÁFICO ################
#Input dos valors exemplificados anteriormente no gráfico 

horizontal = np.linspace(0, 1, 100)
vertical = []

for i in horizontal:
    valor = torque_total_kg_cm(
             0.3,
             0.1,
             np.array([0.04, 0.08, 0.06]),
             np.array([0.075, 0.3, 0.075]),
             np.array([0.001, 0.001]),
             0.1,
             0.5,
             0.05,
             0.05,
             i,)
    vertical.append(valor)
    if len(vertical) == 1: minimo = [i, valor]
    if len(vertical) == 50: meio = [i, valor]
    if len(vertical) == 100: maximo = [i, valor]

plt.plot(horizontal, vertical)

xlabel = 'velocidade_servo_60_graus_por_seg'
ylabel = 'Torque kgcm final (sem fator segurança)'

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