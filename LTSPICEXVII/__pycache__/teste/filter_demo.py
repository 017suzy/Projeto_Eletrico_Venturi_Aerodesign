#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
from apply_ltspice_filter import apply_ltspice_filter, convolution_filter, get_impulse_response

##################################################
##        função: resistência do cabo           ##
##################################################

def queda_tensao(
    resistividade_condutor_ohm_mm2_por_m,
    corrente_maxima_A,
    comprimento_m,
    bitola_awg,
    resistencia_conexoes_ohm=np.array([0])
    ):
    """
    Calcula a queda de tensão no cabo e retorna a resistência equivalente [Ω].
    """
    # conversão AWG → mm²
    bitola_mm = 0.127 * 92 ** ((36-bitola_awg)/39)
    area_secao_fio = np.pi * (bitola_mm/2)**2
    
    # ida e volta
    comprimento_m = comprimento_m * 2
    
    # ρ·L/A
    resistencia_Ohm = (resistividade_condutor_ohm_mm2_por_m * comprimento_m) / area_secao_fio
    resistencia_Ohm += np.sum(resistencia_conexoes_ohm)
    
    return resistencia_Ohm


##################################################
##        parâmetros do cabo e do filtro        ##
##################################################

resistividade_cobre = 0.018   # ohm·mm²/m
comprimento_cabo = 2          # m
bitola_awg = 14
resistencia_conexoes = np.array([0.01])  # cada conector ~0.01 Ω
corrente_servo = 2.0          # A nominal

# resistência total
R_cabo = queda_tensao(resistividade_cobre, corrente_servo, comprimento_cabo, bitola_awg, resistencia_conexoes)

print(f"Resistência total do cabo: {R_cabo:.5f} Ω")

##################################################
##             gerar sinal PWM simulado         ##
##################################################

sample_width = 100e-3
delta_t = 0.1e-3
samples = int(sample_width/delta_t)
time = np.linspace(0, sample_width, samples)

# sinal representando PWM médio
signal_a = 0 + 5*((time > 10e-3) * (time < 30e-3)) + 2*((time > 40e-3) * (time < 70e-3))

##################################################
##          simulação no LTSpice (PyLTSpice)    ##
##################################################

filter_configuration = {
  "C": 100e-6,   # 100 µF
  "L": 200e-3,   # 200 mH
  "R_cabo": R_cabo  # resistência equivalente do fio
}

dummy, signal_b = apply_ltspice_filter(
      "filter_circuit.asc",
      time, signal_a,
      params=filter_configuration
)

##################################################
##             resposta ao impulso              ##
##################################################

kernel_delay = 10e-3
kernel_sample_width = 100e-3

kernel_time, kernel = get_impulse_response(
        "filter_circuit.asc",
        params=filter_configuration,
        sample_width=kernel_sample_width,
        delta_t=delta_t,
        kernel_delay=kernel_delay
)

plt.plot(kernel_time, kernel, label="resposta ao impulso")
plt.xlabel("tempo (s)")
plt.ylabel("tensão (V)")
plt.title("Resposta ao impulso do circuito com resistência do cabo")
plt.legend()
plt.show()

##################################################
##           comparação de sinais               ##
##################################################

signal_b_conv = convolution_filter(
  signal_a,
  kernel,
  delta_t=delta_t,
  kernel_delay=kernel_delay
)

plt.plot(time, signal_a, label="Entrada (sinal do controlador)")
plt.plot(time, signal_b, label="Saída LTSpice (servo)")
plt.plot(time, signal_b_conv, label="Saída via convolução", linestyle="--")
plt.xlabel("tempo (s)")
plt.ylabel("tensão (V)")
plt.title("Tensão de entrada vs tensão no servo (após R_cabo)")
plt.legend()
plt.show()

##################################################
##          gráfico de queda de tensão          ##
##################################################

queda_tensao_cabo = signal_a - signal_b
plt.plot(time, queda_tensao_cabo, color="red", label="queda de tensão no cabo")
plt.xlabel("tempo (s)")
plt.ylabel("ΔV (V)")
plt.title("Queda de tensão ao longo do cabo")
plt.legend()
plt.show()
