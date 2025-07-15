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

def obtener_letra_combinacion(indice):
    """Convierte un índice en una letra o serie de letras (A, B, C, ..., Z, AA, AB, ...)"""
    if indice <= 26:
        return string.ascii_uppercase[indice - 1]
    else:
        q, r = divmod(indice - 1, 26)
        return string.ascii_uppercase[q - 1] + string.ascii_uppercase[r]

def obtener_numero_combinaciones():
    """
    Solicita al usuario el número de combinaciones a analizar por PG.
    Devuelve un número válido entre 1 y 1000.
    """
    while True:
        try:
            numero = int(input("\nIngrese el número de combinaciones a analizar por PG (1-1000): "))
            if 1 <= numero <= 1000:
                return numero
            else:
                print("Por favor, ingrese un número entre 1 y 1000.")
        except ValueError:
            print("Por favor, ingrese un número válido.")

def encontrar_combinaciones_representativas(combinaciones, maximo_representantes):
    """
    Selecciona aleatoriamente combinaciones hasta maximo_representantes.
    Si hay menos combinaciones que maximo_representantes, devuelve todas.
    """
    if len(combinaciones) <= maximo_representantes:
        return combinaciones
    return random.sample(combinaciones, maximo_representantes)

def calcular_combinaciones_por_pg(max_combinaciones):
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
    for combinacion in combinations(todas_las_cartas, 9):
        pg = calcular_puntos(combinacion)
        combinaciones_por_pg[pg].append(combinacion)
        
        procesadas += 1
        if procesadas % 10000 == 0:
            porcentaje = (procesadas / total_combinaciones) * 100
            print(f"\rAgrupando combinaciones: {porcentaje:.1f}% - Combinaciones procesadas: {procesadas:,}", end="")
    
    print("\nSeleccionando combinaciones para análisis...")
    
    # Segunda pasada: seleccionar las combinaciones para análisis
    representativas_por_pg = {}
    for pg, combinaciones in combinaciones_por_pg.items():
        total_combinaciones_pg = len(combinaciones)
        if total_combinaciones_pg <= max_combinaciones:
            print(f"\rPG {pg}: Analizando todas las {total_combinaciones_pg} combinaciones...", end="")
            representativas_por_pg[pg] = combinaciones
        else:
            print(f"\rPG {pg}: Seleccionando {max_combinaciones} combinaciones representativas de {total_combinaciones_pg}...", end="")
            representativas = encontrar_combinaciones_representativas(combinaciones, maximo_representantes=max_combinaciones)
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
            combinacion = tuple(random.sample(cartas_restantes, 9))
            if calcular_puntos(combinacion) > puntos_base:
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
        
        for combinacion in combinations(cartas_restantes, 9):
            if calcular_puntos(combinacion) > puntos_base:
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
    combinaciones_por_pg = calcular_combinaciones_por_pg(num_combinaciones)
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
        
        for indice, combinacion in enumerate(combinaciones, 1):
            letra = obtener_letra_combinacion(indice)
            print(f"\nProcesando PG {pg} {letra}:")
            print(f"Cartas: {formatear_combinacion(combinacion)}")
            
            probabilidad = calcular_probabilidad_condicional(combinacion, todas_las_cartas)
            probabilidades_individuales.append(probabilidad)
            combinaciones_analizadas[pg].append(combinacion)  # Guardamos la combinación
            print(f"Probabilidad para esta combinación: {probabilidad:.4f}")
        
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
        resumen_datos = []
        
        for puntos in sorted(resultados.keys()):
            estadisticas = resultados[puntos]
            resumen_datos.append({
                'Puntos': puntos,
                'Cantidad_Combinaciones': len(estadisticas['probabilidades']),
                'Probabilidad_Promedio': estadisticas['promedio'],
                'Probabilidad_Min': estadisticas['minimo'],
                'Probabilidad_Max': estadisticas['maximo'],
                'Desviacion_Estandar': estadisticas['desviacion_std']
            })
        
        # Crear DataFrame
        df_resumen = pd.DataFrame(resumen_datos)
        
        # Agregar estadísticas globales
        estadisticas_globales = pd.DataFrame({
            'Puntos': ['Estadísticas Globales'],
            'Cantidad_Combinaciones': [df_resumen['Cantidad_Combinaciones'].sum()],
            'Probabilidad_Promedio': [df_resumen['Probabilidad_Promedio'].mean()],
            'Probabilidad_Min': [df_resumen['Probabilidad_Min'].min()],
            'Probabilidad_Max': [df_resumen['Probabilidad_Max'].max()],
            'Desviacion_Estandar': [df_resumen['Desviacion_Estandar'].mean()]
        })
        
        df_final = pd.concat([df_resumen, estadisticas_globales], ignore_index=True)
        
        # Preparar datos de detalles
        detalles_datos = []
        for pg, estadisticas in resultados.items():
            for indice, probabilidad in enumerate(estadisticas['probabilidades']):
                combinacion = combinaciones_analizadas[pg][indice]
                detalles_datos.append({
                    'PG': pg,
                    'Combinación': formatear_combinacion(combinacion),
                    'Probabilidad': probabilidad
                })
        
        df_detalles = pd.DataFrame(detalles_datos) if detalles_datos else None
        
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
                    for nombre_hoja in writer.sheets:
                        hoja = writer.sheets[nombre_hoja]
                        for columna in hoja.columns:
                            max_longitud = 0
                            columna = [celda for celda in columna]
                            for celda in columna:
                                try:
                                    if len(str(celda.value)) > max_longitud:
                                        max_longitud = len(str(celda.value))
                                except:
                                    pass
                            ancho_ajustado = (max_longitud + 2)
                            hoja.column_dimensions[columna[0].column_letter].width = ancho_ajustado
            
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

def principal():
    print("Iniciando análisis...")
    num_combinaciones = obtener_numero_combinaciones()
    resultados, combinaciones_analizadas = analizar_probabilidades(num_combinaciones)
    guardar_resultados_excel(resultados, num_combinaciones, combinaciones_analizadas)
    print("¡Análisis completado!")

if __name__ == "__main__":
    principal()
