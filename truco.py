from itertools import combinations
from collections import defaultdict, Counter
import time
import pandas as pd
import numpy as np
import string
import math
import random
import os
import tempfile
import shutil

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

def obtener_letra_combinacion(idx):
    """Convierte un índice en una letra o serie de letras (A, B, C, ..., Z, AA, AB, ...)"""
    if idx <= 26:
        return string.ascii_uppercase[idx - 1]
    else:
        q, r = divmod(idx - 1, 26)
        return string.ascii_uppercase[q - 1] + string.ascii_uppercase[r]

def obtener_numero_combinaciones():
    """
    Solicita al usuario el número de combinaciones a analizar por PG.
    Retorna un número válido entre 1 y 1000.
    """
    while True:
        try:
            num = int(input("\nIngrese el número de combinaciones a analizar por PG (1-1000): "))
            if 1 <= num <= 1000:
                return num
            else:
                print("Por favor, ingrese un número entre 1 y 1000.")
        except ValueError:
            print("Por favor, ingrese un número válido.")

def find_representative_combinations(combinations, max_representatives):
    """
    Randomly selects combinations up to max_representatives.
    If there are fewer than max_representatives combinations, returns all of them.
    """
    if len(combinations) <= max_representatives:
        return combinations
    return random.sample(combinations, max_representatives)

def calcular_probabilidades_por_pg(max_combinaciones):
    """
    Calcula combinaciones posibles y las agrupa por PG.
    Para PG con menos combinaciones que max_combinaciones, analiza todas.
    Para PG con más combinaciones, selecciona las más representativas.
    """
    todas_las_cartas = list(cartas.keys())
    combinaciones_por_pg = defaultdict(list)
    total_combinaciones = math.comb(len(todas_las_cartas), 9)
    procesadas = 0
    
    print(f"Calculando combinaciones iniciales...")
    inicio = time.time()
    
    # Primera pasada: recolectar todas las combinaciones por PG
    for comb in combinations(todas_las_cartas, 9):
        pg = calcular_puntos(comb)
        combinaciones_por_pg[pg].append(comb)
        
        procesadas += 1
        if procesadas % 10000 == 0:
            porcentaje = (procesadas / total_combinaciones) * 100
            print(f"\rAgrupando combinaciones: {porcentaje:.1f}% - Combinaciones procesadas: {procesadas:,}", end="")
    
    print("\nSeleccionando combinaciones para análisis...")
    
    # Segunda pasada: seleccionar las combinaciones para análisis
    representativas_por_pg = {}
    for pg, combinaciones in combinaciones_por_pg.items():
        total_combinaciones = len(combinaciones)
        if total_combinaciones <= max_combinaciones:
            print(f"\rPG {pg}: Analizando todas las {total_combinaciones} combinaciones...", end="")
            representativas_por_pg[pg] = combinaciones
        else:
            print(f"\rPG {pg}: Seleccionando {max_combinaciones} combinaciones representativas de {total_combinaciones}...", end="")
            representativas = find_representative_combinations(combinaciones, max_representatives=max_combinaciones)
            representativas_por_pg[pg] = representativas
    
    print("\n\nResumen de combinaciones por PG:")
    for pg in sorted(representativas_por_pg.keys()):
        num_original = len(combinaciones_por_pg[pg])
        num_final = len(representativas_por_pg[pg])
        if num_original <= max_combinaciones:
            print(f"PG {pg}: Analizando todas las {num_final} combinaciones disponibles.")
        else:
            print(f"PG {pg}: Analizando {max_combinaciones} combinaciones representativas de {num_original} totales.")
    
    print(f"\nSe procesarán combinaciones para {len(representativas_por_pg)} valores de PG diferentes")
    return representativas_por_pg

def calcular_probabilidad_condicional(combinacion_base, todas_las_cartas, max_muestras=10000):
    """
    Calcula la probabilidad de que una combinación del mazo restante sume más puntos
    que la combinación base, usando muestreo aleatorio para grandes conjuntos.
    """
    puntos_base = calcular_puntos(combinacion_base)
    cartas_restantes = list(set(todas_las_cartas) - set(combinacion_base))
    total_posibles = math.comb(len(cartas_restantes), 9)  # 31C9
    
    # Si hay demasiadas combinaciones posibles, usar muestreo aleatorio
    if total_posibles > max_muestras:
        print(f"Usando muestreo aleatorio ({max_muestras:,} muestras de {total_posibles:,} posibles)...")
        combinaciones_superiores = 0
        muestras_procesadas = 0
        
        for _ in range(max_muestras):
            comb = tuple(random.sample(cartas_restantes, 9))
            if calcular_puntos(comb) > puntos_base:
                combinaciones_superiores += 1
            
            muestras_procesadas += 1
            if muestras_procesadas % 1000 == 0:
                porcentaje = (muestras_procesadas / max_muestras) * 100
                print(f"\rProcesando: {muestras_procesadas:,}/{max_muestras:,} ({porcentaje:.1f}%) - Superiores encontradas: {combinaciones_superiores:,}", end="")
        
        probabilidad = combinaciones_superiores / max_muestras
    else:
        print(f"Analizando todas las {total_posibles:,} combinaciones posibles...")
        combinaciones_superiores = 0
        procesadas = 0
        
        for comb in combinations(cartas_restantes, 9):
            if calcular_puntos(comb) > puntos_base:
                combinaciones_superiores += 1
            
            procesadas += 1
            if procesadas % 1000 == 0:
                porcentaje = (procesadas / total_posibles) * 100
                print(f"\rProcesando: {procesadas:,}/{total_posibles:,} ({porcentaje:.1f}%) - Superiores encontradas: {combinaciones_superiores:,}", end="")
        
        probabilidad = combinaciones_superiores / total_posibles
    
    print(f"\nCombinaciones superiores encontradas: {combinaciones_superiores:,}")
    return probabilidad

def analizar_probabilidades(num_combinaciones):
    print("Iniciando análisis de probabilidades...")
    inicio_total = time.time()
    
    # Primero calculamos todas las combinaciones posibles y las agrupamos por PG
    combinaciones_por_pg = calcular_probabilidades_por_pg(num_combinaciones)
    todas_las_cartas = list(cartas.keys())
    
    # Ahora procesamos cada PG
    resultados = defaultdict(dict)
    combinaciones_analizadas = {}  # Guardamos las combinaciones analizadas
    
    for pg in sorted(combinaciones_por_pg.keys()):
        inicio_pg = time.time()
        combinaciones = combinaciones_por_pg[pg]
        print(f"\nProcesando PG {pg} ({len(combinaciones)} combinaciones)...")
        
        # Para cada combinación de este PG
        probabilidades_individuales = []
        combinaciones_analizadas[pg] = []  # Lista para guardar las combinaciones de este PG
        
        for idx, combinacion in enumerate(combinaciones, 1):
            letra = obtener_letra_combinacion(idx)
            print(f"\nProcesando PG {pg} {letra}:")
            print(f"Cartas: {formatear_combinacion(combinacion)}")
            
            prob = calcular_probabilidad_condicional(combinacion, todas_las_cartas)
            probabilidades_individuales.append(prob)
            combinaciones_analizadas[pg].append(combinacion)  # Guardamos la combinación
            print(f"Probabilidad para esta combinación: {prob:.4f}")
        
        # Calcular estadísticas para este PG
        resultados[pg] = {
            'probabilidades': probabilidades_individuales,
            'promedio': np.mean(probabilidades_individuales),
            'minimo': np.min(probabilidades_individuales),
            'maximo': np.max(probabilidades_individuales),
            'desviacion_std': np.std(probabilidades_individuales)
        }
        
        tiempo_pg = time.time() - inicio_pg
        print(f"\nCompletado PG {pg}:")
        print(f"  Combinaciones analizadas: {len(combinaciones)}")
        print(f"  Tiempo procesamiento: {tiempo_pg:.2f}s")
        print(f"  Probabilidad promedio: {resultados[pg]['promedio']:.4f}")
        print(f"  Rango de probabilidades: {resultados[pg]['minimo']:.4f} - {resultados[pg]['maximo']:.4f}")
        print(f"  Desviación estándar: {resultados[pg]['desviacion_std']:.4f}")
    
    tiempo_total = time.time() - inicio_total
    print(f"\nTiempo total de cálculo: {tiempo_total:.2f} segundos")
    return resultados, combinaciones_analizadas

def verificar_espacio_disponible(ruta_guardado='.'):
    """
    Verifica si hay suficiente espacio en disco para guardar los resultados.
    Retorna True si hay suficiente espacio, False en caso contrario.
    """
    try:
        # Calcular espacio libre en GB
        espacio_libre = shutil.disk_usage(ruta_guardado).free / (1024 * 1024 * 1024)
        # Necesitamos al menos 1GB libre para estar seguros
        if espacio_libre < 1:
            print(f"\n¡ADVERTENCIA! Poco espacio en disco: {espacio_libre:.2f}GB disponibles")
            print("Se recomienda al menos 1GB de espacio libre para guardar los resultados.")
            continuar = input("¿Desea continuar de todos modos? (s/n): ").lower()
            return continuar == 's'
        return True
    except Exception as e:
        print(f"Error al verificar espacio en disco: {e}")
        return False

def guardar_resultados_excel(resultados, num_combinaciones, combinaciones_analizadas):
    # Definir la ruta de guardado
    ruta_guardado = 'E:\\TRUCO'
    
    # Verificar si el directorio existe, si no, crearlo
    if not os.path.exists(ruta_guardado):
        try:
            os.makedirs(ruta_guardado)
            print(f"\nSe creó el directorio {ruta_guardado}")
        except Exception as e:
            print(f"\nError al crear el directorio {ruta_guardado}: {e}")
            return False
    
    # Verificar espacio en disco
    if not verificar_espacio_disponible(ruta_guardado):
        print("Operación cancelada por falta de espacio en disco.")
        return False

    try:
        # Crear datos para el resumen
        resumen_data = []
        
        for puntos in sorted(resultados.keys()):
            stats = resultados[puntos]
            resumen_data.append({
                'Puntos': puntos,
                'Cantidad_Combinaciones': len(stats['probabilidades']),
                'Probabilidad_Promedio': stats['promedio'],
                'Probabilidad_Min': stats['minimo'],
                'Probabilidad_Max': stats['maximo'],
                'Desviacion_Estandar': stats['desviacion_std']
            })
        
        # Crear DataFrame
        df_resumen = pd.DataFrame(resumen_data)
        
        # Agregar estadísticas globales
        stats_globales = pd.DataFrame({
            'Puntos': ['Estadísticas Globales'],
            'Cantidad_Combinaciones': [df_resumen['Cantidad_Combinaciones'].sum()],
            'Probabilidad_Promedio': [df_resumen['Probabilidad_Promedio'].mean()],
            'Probabilidad_Min': [df_resumen['Probabilidad_Min'].min()],
            'Probabilidad_Max': [df_resumen['Probabilidad_Max'].max()],
            'Desviacion_Estandar': [df_resumen['Desviacion_Estandar'].mean()]
        })
        
        df_final = pd.concat([df_resumen, stats_globales], ignore_index=True)
        
        # Preparar datos de detalles
        detalles_data = []
        for pg, stats in resultados.items():
            for idx, prob in enumerate(stats['probabilidades']):
                combinacion = combinaciones_analizadas[pg][idx]
                detalles_data.append({
                    'PG': pg,
                    'Combinación': formatear_combinacion(combinacion),
                    'Probabilidad': prob
                })
        
        df_detalles = pd.DataFrame(detalles_data) if detalles_data else None
        
        # Guardar en Excel con manejo de errores
        nombre_archivo = os.path.join(ruta_guardado, f'probabilidades_resumen_{num_combinaciones}.xlsx')
        temp_archivo = None
        
        try:
            # Primero guardar en un archivo temporal en la misma unidad
            temp_dir = os.path.dirname(nombre_archivo)
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx', dir=temp_dir) as tmp:
                temp_archivo = tmp.name
                with pd.ExcelWriter(temp_archivo, engine='openpyxl') as writer:
                    # Hoja de resumen
                    df_final.to_excel(writer, sheet_name='Resumen', index=False)
                    
                    # Hoja de detalles
                    if df_detalles is not None:
                        df_detalles.to_excel(writer, sheet_name='Probabilidades_Individuales', index=False)
                    
                    # Ajustar columnas en ambas hojas
                    for sheet_name in writer.sheets:
                        sheet = writer.sheets[sheet_name]
                        for column in sheet.columns:
                            max_length = 0
                            column = [cell for cell in column]
                            for cell in column:
                                try:
                                    if len(str(cell.value)) > max_length:
                                        max_length = len(str(cell.value))
                                except:
                                    pass
                            adjusted_width = (max_length + 2)
                            sheet.column_dimensions[column[0].column_letter].width = adjusted_width
            
            # Si se guardó correctamente el temporal, moverlo al archivo final
            if os.path.exists(nombre_archivo):
                os.remove(nombre_archivo)
            shutil.move(temp_archivo, nombre_archivo)
            
            print(f"\nResultados guardados en '{nombre_archivo}'")
            print("Se incluyeron dos hojas:")
            print("1. 'Resumen': Estadísticas agregadas por PG")
            print("2. 'Probabilidades_Individuales': Todas las probabilidades individuales por PG y sus combinaciones")
            return True
            
        except Exception as e:
            print(f"\nError al guardar el archivo Excel: {e}")
            if temp_archivo and os.path.exists(temp_archivo):
                try:
                    os.remove(temp_archivo)
                except:
                    pass
            return False
            
    except Exception as e:
        print(f"\nError al procesar los datos: {e}")
        return False

def main():
    print("Iniciando análisis...")
    num_combinaciones = obtener_numero_combinaciones()
    resultados, combinaciones_analizadas = analizar_probabilidades(num_combinaciones)
    guardar_resultados_excel(resultados, num_combinaciones, combinaciones_analizadas)
    print("Análisis completado!")

if __name__ == "__main__":
    main()
