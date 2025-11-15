#!/usr/bin/env python3
"""
Script para llenar reservas de diciembre con distribución decreciente
y actualizar estados según las fechas.

Estrategia:
- Reservas hasta 15 nov → COMPLETADAS (100%)
- Reservas 11-31 dic → ACTIVAS (80%), PENDIENTES (10%), CANCELADAS (10%)
- Cantidad decreciente: más cercanas = más reservas
"""

import os
import sys
import django
from datetime import datetime, timedelta, time
import random

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ReservaProject.settings')
django.setup()

from django.contrib.auth.models import User
from mainApp.models import Mesa, Reserva, Perfil
from django.utils import timezone

def actualizar_estados_pasados():
    """Actualizar todas las reservas hasta el 15 de noviembre a estado COMPLETADA"""
    fecha_limite = datetime(2025, 11, 15).date()

    # objects ya filtra automáticamente deleted_at=NULL (no eliminadas)
    reservas_pasadas = Reserva.objects.filter(
        fecha_reserva__lte=fecha_limite
    ).exclude(estado='completada')

    count = reservas_pasadas.count()
    reservas_pasadas.update(estado='completada')

    print(f'✓ {count} reservas anteriores al 15/11 actualizadas a COMPLETADA')
    return count

def calcular_num_reservas_por_dia(dia, dias_desde_hoy):
    """
    Calcular cantidad de reservas por día con distribución decreciente.

    Días más cercanos (11-15 dic): 15-20 reservas
    Días medios (16-23 dic): 10-15 reservas
    Días lejanos (24-31 dic): 5-10 reservas
    """
    if dias_desde_hoy < 30:  # 11-15 diciembre
        return random.randint(15, 20)
    elif dias_desde_hoy < 38:  # 16-23 diciembre
        return random.randint(10, 15)
    else:  # 24-31 diciembre
        return random.randint(5, 10)

def generar_estado_aleatorio():
    """
    Generar estado según distribución:
    - 80% activa
    - 10% pendiente
    - 10% cancelada
    """
    rand = random.random()
    if rand < 0.80:
        return 'activa'
    elif rand < 0.90:
        return 'pendiente'
    else:
        return 'cancelada'

def crear_reservas_diciembre():
    """Crear reservas del 11 al 31 de diciembre con distribución decreciente"""

    print('\n=== GENERANDO RESERVAS DE DICIEMBRE ===\n')

    # Obtener todos los clientes y mesas
    clientes = list(User.objects.all())
    mesas = list(Mesa.objects.all())

    if not clientes:
        print('❌ No hay usuarios en el sistema')
        return 0

    if not mesas:
        print('❌ No hay mesas en el sistema')
        return 0

    print(f'📊 Clientes disponibles: {len(clientes)}')
    print(f'🪑 Mesas disponibles: {len(mesas)}')

    # Fecha de inicio: 11 de diciembre 2025
    fecha_inicio = datetime(2025, 12, 11).date()
    fecha_fin = datetime(2025, 12, 31).date()
    hoy = datetime(2025, 11, 15).date()

    # Horarios de atención: 12:00 - 21:00 (última reserva a las 21:00)
    horas_disponibles = []
    for hora in range(12, 22):  # 12:00 a 21:00
        for minuto in [0, 30]:
            horas_disponibles.append(time(hora, minuto))

    reservas_creadas = 0
    fecha_actual = fecha_inicio

    while fecha_actual <= fecha_fin:
        dias_desde_hoy = (fecha_actual - hoy).days
        num_reservas_dia = calcular_num_reservas_por_dia(fecha_actual.day, dias_desde_hoy)

        print(f'\n📅 {fecha_actual.strftime("%d/%m/%Y")} (en {dias_desde_hoy} días) - Generando {num_reservas_dia} reservas')

        reservas_dia = 0
        intentos = 0
        max_intentos = num_reservas_dia * 3  # Intentar hasta 3 veces por cada reserva deseada

        while reservas_dia < num_reservas_dia and intentos < max_intentos:
            intentos += 1

            # Seleccionar aleatoriamente
            cliente = random.choice(clientes)
            mesa = random.choice(mesas)
            hora_inicio = random.choice(horas_disponibles)

            # Calcular hora_fin (2 horas después)
            hora_inicio_dt = datetime.combine(fecha_actual, hora_inicio)
            hora_fin_dt = hora_inicio_dt + timedelta(hours=2)
            hora_fin = hora_fin_dt.time()

            # Verificar si ya existe una reserva con solapamiento
            # objects ya filtra automáticamente deleted_at=NULL
            reservas_existentes = Reserva.objects.filter(
                mesa=mesa,
                fecha_reserva=fecha_actual
            )

            solapamiento = False
            for reserva_existente in reservas_existentes:
                inicio_existente = datetime.combine(fecha_actual, reserva_existente.hora_inicio)
                fin_existente = datetime.combine(fecha_actual, reserva_existente.hora_fin)

                if not (hora_fin_dt <= inicio_existente or hora_inicio_dt >= fin_existente):
                    solapamiento = True
                    break

            if solapamiento:
                continue  # Intentar otra combinación

            # Crear reserva
            num_personas = random.randint(1, min(mesa.capacidad, 8))
            estado = generar_estado_aleatorio()

            try:
                reserva = Reserva.objects.create(
                    cliente=cliente,
                    mesa=mesa,
                    fecha_reserva=fecha_actual,
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin,
                    num_personas=num_personas,
                    estado=estado,
                    notas=f'Reserva automática - {estado}'
                )
                reservas_creadas += 1
                reservas_dia += 1

            except Exception as e:
                # Si falla, continuar con la siguiente
                continue

        print(f'   ✓ {reservas_dia} reservas creadas')

        # Avanzar al siguiente día
        fecha_actual += timedelta(days=1)

    return reservas_creadas

def mostrar_estadisticas():
    """Mostrar estadísticas de las reservas creadas"""
    print('\n' + '='*60)
    print('📊 ESTADÍSTICAS FINALES')
    print('='*60)

    # objects ya filtra automáticamente deleted_at=NULL
    total_reservas = Reserva.objects.count()
    print(f'\n📈 Total de reservas en sistema: {total_reservas}')

    # Por estado
    print('\n🏷️  Reservas por estado:')
    for estado_code, estado_nombre in Reserva.ESTADO_CHOICES:
        count = Reserva.objects.filter(estado=estado_code).count()
        porcentaje = (count / total_reservas * 100) if total_reservas > 0 else 0
        print(f'   - {estado_nombre}: {count} ({porcentaje:.1f}%)')

    # Por mes
    print('\n📅 Reservas por mes:')
    noviembre = Reserva.objects.filter(
        fecha_reserva__year=2025,
        fecha_reserva__month=11
    ).count()
    diciembre = Reserva.objects.filter(
        fecha_reserva__year=2025,
        fecha_reserva__month=12
    ).count()
    print(f'   - Noviembre 2025: {noviembre}')
    print(f'   - Diciembre 2025: {diciembre}')

    # Reservas pasadas vs futuras
    hoy = datetime(2025, 11, 15).date()
    pasadas = Reserva.objects.filter(fecha_reserva__lt=hoy).count()
    futuras = Reserva.objects.filter(fecha_reserva__gte=hoy).count()
    print(f'\n⏰ Distribución temporal:')
    print(f'   - Pasadas (antes del 15/11): {pasadas}')
    print(f'   - Futuras (desde el 15/11): {futuras}')

    # Verificar que pasadas estén completadas
    pasadas_completadas = Reserva.objects.filter(
        fecha_reserva__lt=hoy,
        estado='completada'
    ).count()
    print(f'\n✅ Verificación:')
    print(f'   - Pasadas COMPLETADAS: {pasadas_completadas}/{pasadas}')
    if pasadas == pasadas_completadas:
        print('   ✓ Todas las reservas pasadas están completadas')
    else:
        print(f'   ⚠️  {pasadas - pasadas_completadas} reservas pasadas no están completadas')

def main():
    print('='*60)
    print('🎄 SCRIPT DE RESERVAS DE DICIEMBRE 2025')
    print('='*60)
    print('\nEste script:')
    print('1. Actualiza reservas pasadas (hasta 15/11) → COMPLETADA')
    print('2. Crea reservas 11-31 dic con distribución decreciente')
    print('3. Estados: 80% activas, 10% pendientes, 10% canceladas')
    print('\n' + '='*60 + '\n')

    # Paso 1: Actualizar estados pasados
    print('\n📝 PASO 1: Actualizando estados de reservas pasadas...')
    actualizadas = actualizar_estados_pasados()

    # Paso 2: Crear reservas de diciembre
    print('\n📝 PASO 2: Creando reservas de diciembre...')
    creadas = crear_reservas_diciembre()

    # Paso 3: Mostrar estadísticas
    mostrar_estadisticas()

    print('\n' + '='*60)
    print('✅ SCRIPT COMPLETADO')
    print('='*60)
    print(f'\n📊 Resumen:')
    print(f'   - Reservas actualizadas a COMPLETADA: {actualizadas}')
    print(f'   - Nuevas reservas de diciembre: {creadas}')
    print('\n🎉 ¡Datos generados exitosamente!\n')

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('\n\n⚠️  Script interrumpido por el usuario')
        sys.exit(1)
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
