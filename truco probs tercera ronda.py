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
    return ' '.join(sorted(combinacion))

def analizar_probabilidades_tercera_ronda(max_combinaciones_9=10, max_combinaciones_6=50):
    print("Iniciando análisis de probabilidades para la tercera ronda...")
    inicio_total = time.time()
    todas_las_cartas = list(cartas.keys())
    resultados_por_pg_super_reducido = defaultdict(list)
    detalles = []

    for pg in range(15, 100):
        print(f"\nProcesando PG original {pg}...")
        combinaciones_9 = []
        for combinacion in combinations(todas_las_cartas, 9):
            if len(combinaciones_9) < max_combinaciones_9:
                combinaciones_9.append(combinacion)
            else:
                break
        for idx_9, combinacion_9 in enumerate(combinaciones_9, 1):
            print(f"  Combinación 9 cartas {idx_9}/{len(combinaciones_9)}: {formatear_combinacion(combinacion_9)}")
            mazo_reducido = list(set(todas_las_cartas) - set(combinacion_9))  # 31 cartas
            total_combinaciones_6 = math.comb(len(mazo_reducido), 6)
            if total_combinaciones_6 <= max_combinaciones_6:
                combinaciones_6 = list(combinations(mazo_reducido, 6))
            else:
                combinaciones_6 = [tuple(random.sample(mazo_reducido, 6)) for _ in range(max_combinaciones_6)]
            for idx_6, combinacion_6 in enumerate(combinaciones_6, 1):
                pg_6 = calcular_puntos(combinacion_6)
                pg_super_reducido = pg - pg_6
                mazo_hiper_reducido = list(set(mazo_reducido) - set(combinacion_6))  # 25 cartas
                combinaciones_3 = list(combinations(mazo_hiper_reducido, 3))  # 2300
                cuenta_ganar = 0
                for comb_3 in combinaciones_3:
                    pg_3 = calcular_puntos(comb_3)
                    if pg_super_reducido > pg_3:
                        cuenta_ganar += 1
                probabilidad = cuenta_ganar / len(combinaciones_3) if combinaciones_3 else 0
                resultados_por_pg_super_reducido[pg_super_reducido].append(probabilidad)
                detalles.append({
                    'PG_original': pg,
                    'Combinacion_9': formatear_combinacion(combinacion_9),
                    'Cartas_rival_6': formatear_combinacion(combinacion_6),
                    'PG_super_reducido': pg_super_reducido,
                    'Probabilidad': probabilidad
                })
            print(f"    Completadas todas las combinaciones de 6 cartas del rival para esta combinación de 9 cartas.")
        print(f"  Completado PG {pg}.")
    resumen = []
    for pg_sup_red in sorted(resultados_por_pg_super_reducido.keys()):
        probs = resultados_por_pg_super_reducido.get(pg_sup_red, [])
        if probs:
            resumen.append({
                'PG_super_reducido': pg_sup_red,
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
    nombre_archivo_resumen = os.path.join(ruta_guardado, f'probabilidades_tercera_ronda_resumen_{max_combinaciones_9}_{max_combinaciones_6}.csv')
    df_resumen.to_csv(nombre_archivo_resumen, index=False, encoding='utf-8')
    nombre_archivo_detalles = os.path.join(ruta_guardado, f'probabilidades_tercera_ronda_detalles_{max_combinaciones_9}_{max_combinaciones_6}.csv')
    df_detalles.to_csv(nombre_archivo_detalles, index=False, encoding='utf-8')
    print(f"\nResultados de la tercera ronda guardados en:")
    print(f"  Resumen: '{nombre_archivo_resumen}'")
    print(f"  Detalles: '{nombre_archivo_detalles}'")
    print(f"Tiempo total de cálculo: {time.time() - inicio_total:.2f} segundos")

if __name__ == "__main__":
    print("\n--- Parámetros para el cálculo de probabilidades de la tercera ronda ---")
    max_combinaciones_9 = int(input("Ingrese el límite de combinaciones de 9 cartas por PG para la PRIMERA ronda (default 10): ") or 10)
    max_combinaciones_6 = int(input("Ingrese el límite de combinaciones de 6 cartas para la SEGUNDA ronda (default 50): ") or 50)
    analizar_probabilidades_tercera_ronda(max_combinaciones_9=max_combinaciones_9, max_combinaciones_6=max_combinaciones_6) 
