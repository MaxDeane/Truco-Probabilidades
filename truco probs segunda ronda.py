from itertools import combinations
from collections import defaultdict
import time
import pandas as pd
import numpy as np
import math
import random
import os

# Definición de las cartas y sus ponderaciones
cartas = {
    '4E': 1, '4O': 1, '4B': 1, '4C': 1,
    '5E': 2, '5O': 2, '5B': 2, '5C': 2,
    '6E': 3, '6O': 3, '6B': 3, '6C': 3,
    '7B': 4, '7C': 4,
    '10E': 5, '10O': 5, '10B': 5, '10C': 5,
    '11E': 6, '11O': 6, '11B': 6, '11C': 6,
    '12E': 7, '12O': 7, '12B': 7, '12C': 7,
    '1C': 8, '1O': 8,
    '2E': 9, '2O': 9, '2B': 9, '2C': 9,
    '3E': 10, '3O': 10, '3B': 10, '3C': 10,
    '7O': 11,
    '7E': 12,
    '1B': 13,
    '1E': 14
}

def calcular_puntos(combinacion):
    return sum(cartas[carta] for carta in combinacion)

def formatear_combinacion(combinacion):
    """Formatea una combinación de cartas para mostrarla de manera legible"""
    return ' '.join(sorted(combinacion))

def calcular_combinaciones_por_pg(max_combinaciones):
    """
    Calcula hasta max_combinaciones combinaciones de 9 cartas por cada PG, de forma eficiente y sin consumir mucha memoria.
    """
    todas_las_cartas = list(cartas.keys())
    representativas_por_pg = defaultdict(list)
    for combinacion in combinations(todas_las_cartas, 9):
        pg = calcular_puntos(combinacion)
        if len(representativas_por_pg[pg]) < max_combinaciones:
            representativas_por_pg[pg].append(combinacion)
    return representativas_por_pg

def analizar_probabilidades_segunda_ronda(max_combinaciones_9=10, max_combinaciones_6=50):
    """
    Calcula las probabilidades ajustadas de que el rival tenga un PG mayor al propio en la segunda ronda,
    conociendo 3 de las 9 cartas del rival. Guarda los resultados en un archivo Excel.
    """
    print("Iniciando análisis de probabilidades para la segunda ronda...")
    inicio_total = time.time()
    todas_las_cartas = list(cartas.keys())
    resultados_por_pg_reducido = defaultdict(list)  # {pg_reducido: [probabilidades]}
    detalles = []

    # Para cada PG posible (15 a 99)
    for pg in range(15, 100):
        print(f"\nProcesando PG original {pg}...")
        combinaciones_por_pg = calcular_combinaciones_por_pg(max_combinaciones_9)
        if pg not in combinaciones_por_pg:
            continue
        combinaciones_9 = combinaciones_por_pg[pg]
        for idx_9, combinacion_9 in enumerate(combinaciones_9, 1):
            print(f"  Combinación {idx_9}/{len(combinaciones_9)}: {formatear_combinacion(combinacion_9)}")
            mazo_rival = list(set(todas_las_cartas) - set(combinacion_9))
            total_combinaciones_3 = math.comb(len(mazo_rival), 3)
            for idx_3, comb_3 in enumerate(combinations(mazo_rival, 3), 1):
                if idx_3 == 1 or idx_3 % 500 == 0 or idx_3 == total_combinaciones_3:
                    print(f"    Procesando combinación rival 3 cartas {idx_3:,}/{total_combinaciones_3:,}...", end='\r')
                suma_3 = calcular_puntos(comb_3)
                pg_reducido = pg - suma_3
                mazo_super_reducido = list(set(mazo_rival) - set(comb_3))
                total_posibles_6 = math.comb(len(mazo_super_reducido), 6)
                if total_posibles_6 <= max_combinaciones_6:
                    combinaciones_6 = list(combinations(mazo_super_reducido, 6))
                else:
                    combinaciones_6 = [tuple(random.sample(mazo_super_reducido, 6)) for _ in range(max_combinaciones_6)]
                cuenta_mayores = 0
                for comb_6 in combinaciones_6:
                    pg_rival = calcular_puntos(comb_6)
                    if pg_rival < pg_reducido:
                        cuenta_mayores += 1
                probabilidad = cuenta_mayores / len(combinaciones_6) if combinaciones_6 else 0
                resultados_por_pg_reducido[pg_reducido].append(probabilidad)
                detalles.append({
                    'PG_original': pg,
                    'Combinacion_9': formatear_combinacion(combinacion_9),
                    'Cartas_rival_3': formatear_combinacion(comb_3),
                    'PG_reducido': pg_reducido,
                    'Probabilidad': probabilidad
                })
            print(f"    Completadas todas las combinaciones de 3 cartas del rival para esta combinación de 9 cartas.")
        print(f"  Completado PG {pg}.")
    resumen = []
    for pg_red in range(-24, 97):
        probs = resultados_por_pg_reducido.get(pg_red, [])
        if probs:
            resumen.append({
                'PG_reducido': pg_red,
                'Cantidad': len(probs),
                'Probabilidad_promedio': np.mean(probs),
                'Probabilidad_min': np.min(probs),
                'Probabilidad_max': np.max(probs),
                'Desviacion_std': np.std(probs)
            })
    df_resumen = pd.DataFrame(resumen)
    df_detalles = pd.DataFrame(detalles)
    ruta_guardado = 'E:\\TRUCO'
    if not os.path.exists(ruta_guardado):
        os.makedirs(ruta_guardado)
    
    # Guardar resumen en CSV
    nombre_archivo_resumen = os.path.join(ruta_guardado, f'probabilidades_segunda_ronda_resumen_{max_combinaciones_9}_{max_combinaciones_6}.csv')
    df_resumen.to_csv(nombre_archivo_resumen, index=False, encoding='utf-8')
    
    # Guardar detalles en CSV
    nombre_archivo_detalles = os.path.join(ruta_guardado, f'probabilidades_segunda_ronda_detalles_{max_combinaciones_9}_{max_combinaciones_6}.csv')
    df_detalles.to_csv(nombre_archivo_detalles, index=False, encoding='utf-8')
    
    print(f"\nResultados de la segunda ronda guardados en:")
    print(f"  Resumen: '{nombre_archivo_resumen}'")
    print(f"  Detalles: '{nombre_archivo_detalles}'")
    print(f"Tiempo total de cálculo: {time.time() - inicio_total:.2f} segundos")

def pedir_limite(mensaje, minimo=1, maximo=1000, valor_default=10):
    while True:
        try:
            entrada = input(f"{mensaje} (mínimo {minimo}, máximo {maximo}, default {valor_default}): ")
            if entrada.strip() == '':
                return valor_default
            valor = int(entrada)
            if minimo <= valor <= maximo:
                return valor
            else:
                print(f"Por favor, ingrese un número entre {minimo} y {maximo}.")
        except ValueError:
            print("Por favor, ingrese un número válido.")

if __name__ == "__main__":
    print("\n--- Parámetros para el cálculo de probabilidades de la segunda ronda ---")
    max_combinaciones_9 = pedir_limite(
        "Ingrese el límite de combinaciones de 9 cartas por PG para la PRIMERA ronda",
        minimo=1, maximo=1000, valor_default=10)
    max_combinaciones_6 = pedir_limite(
        "Ingrese el límite de combinaciones de 6 cartas para la SEGUNDA ronda",
        minimo=1, maximo=1000, valor_default=50)
    analizar_probabilidades_segunda_ronda(max_combinaciones_9=max_combinaciones_9, max_combinaciones_6=max_combinaciones_6)
