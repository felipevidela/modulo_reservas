#!/usr/bin/env python3
"""
Script optimizado para llenar reservas de diciembre de forma rápida.

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

def actualizar_estados_pasados():
    """Actualizar todas las reservas hasta el 15 de noviembre a estado COMPLETADA"""
    fecha_limite = datetime(2025, 11, 15).date()

    # objects ya filtra automáticamente deleted_at=NULL
    reservas_pasadas = Reserva.objects.filter(
        fecha_reserva__lte=fecha_limite
    ).exclude(estado='completada')

    count = reservas_pasadas.count()
    reservas_pasadas.update(estado='completada')

    print(f'✓ {count} reservas anteriores al 15/11 actualizadas a COMPLETADA')
    return count

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

def crear_reservas_diciembre_optimizado():
    """Crear reservas de diciembre de forma optimizada usando bulk_create"""

    print('\n=== GENERANDO RESERVAS DE DICIEMBRE (OPTIMIZADO) ===\n')

    # Obtener todos los clientes y mesas
    clientes = list(User.objects.all())
    mesas = list(Mesa.objects.all())

    if not clientes:
        print('❌ No hay usuarios en el sistema')
        return 0

    if not mesas:
        print('❌ No hay mesas en el sistema')
        return 0

    print(f'📊 Clientes: {len(clientes)}')
    print(f'🪑 Mesas: {len(mesas)}')

    # Horarios disponibles (cada 30 min de 12:00 a 21:00)
    horas_disponibles = []
    for hora in range(12, 22):
        for minuto in [0, 30]:
            horas_disponibles.append(time(hora, minuto))

    # Fecha de inicio y fin
    fecha_inicio = datetime(2025, 12, 11).date()
    fecha_fin = datetime(2025, 12, 31).date()

    reservas_a_crear = []
    fecha_actual = fecha_inicio
    reservas_totales = 0

    while fecha_actual <= fecha_fin:
        # Calcular número de reservas por día (decreciente)
        dias_desde_inicio = (fecha_actual - fecha_inicio).days

        if dias_desde_inicio < 5:  # 11-15 dic
            num_reservas = random.randint(8, 12)
        elif dias_desde_inicio < 13:  # 16-23 dic
            num_reservas = random.randint(5, 8)
        else:  # 24-31 dic
            num_reservas = random.randint(3, 6)

        print(f'📅 {fecha_actual.strftime("%d/%m/%Y")} - Generando {num_reservas} reservas... ', end='', flush=True)

        # Generar reservas para este día
        reservas_dia = 0
        intentos_maximos = num_reservas * 5
        intentos = 0

        # Crear un set para rastrear combinaciones usadas en este día
        combinaciones_usadas = set()

        while reservas_dia < num_reservas and intentos < intentos_maximos:
            intentos += 1

            # Seleccionar aleatoriamente
            cliente = random.choice(clientes)
            mesa = random.choice(mesas)
            hora_inicio = random.choice(horas_disponibles)

            # Crear combinación única
            combinacion = (mesa.id, hora_inicio)

            # Verificar que no hayamos usado esta combinación
            if combinacion in combinaciones_usadas:
                continue

            combinaciones_usadas.add(combinacion)

            # Calcular hora_fin (2 horas después)
            hora_inicio_dt = datetime.combine(fecha_actual, hora_inicio)
            hora_fin_dt = hora_inicio_dt + timedelta(hours=2)
            hora_fin = hora_fin_dt.time()

            # Crear reserva
            num_personas = random.randint(1, min(mesa.capacidad, 8))
            estado = generar_estado_aleatorio()

            reserva = Reserva(
                cliente=cliente,
                mesa=mesa,
                fecha_reserva=fecha_actual,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                num_personas=num_personas,
                estado=estado,
                notas=f'Reserva {estado} - Generada automáticamente'
            )

            reservas_a_crear.append(reserva)
            reservas_dia += 1

        print(f'✓ {reservas_dia} reservas')
        reservas_totales += reservas_dia

        # Crear en batch cada 100 reservas para optimizar
        if len(reservas_a_crear) >= 100:
            Reserva.objects.bulk_create(reservas_a_crear, ignore_conflicts=True)
            reservas_a_crear = []

        # Avanzar al siguiente día
        fecha_actual += timedelta(days=1)

    # Crear las reservas restantes
    if reservas_a_crear:
        Reserva.objects.bulk_create(reservas_a_crear, ignore_conflicts=True)

    print(f'\n✅ Total de reservas creadas: {reservas_totales}')
    return reservas_totales

def mostrar_estadisticas():
    """Mostrar estadísticas de las reservas creadas"""
    print('\n' + '='*60)
    print('📊 ESTADÍSTICAS FINALES')
    print('='*60)

    # objects ya filtra automáticamente deleted_at=NULL
    total_reservas = Reserva.objects.count()
    print(f'\n📈 Total de reservas: {total_reservas}')

    # Por estado
    print('\n🏷️  Distribución por estado:')
    for estado_code, estado_nombre in Reserva.ESTADO_CHOICES:
        count = Reserva.objects.filter(estado=estado_code).count()
        porcentaje = (count / total_reservas * 100) if total_reservas > 0 else 0
        print(f'   - {estado_nombre}: {count} ({porcentaje:.1f}%)')

    # Por mes
    print('\n📅 Distribución por mes:')
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
    print('🎄 SCRIPT OPTIMIZADO - RESERVAS DICIEMBRE 2025')
    print('='*60)
    print('\nEste script:')
    print('1. Actualiza reservas pasadas (hasta 15/11) → COMPLETADA')
    print('2. Crea reservas 11-31 dic con distribución decreciente')
    print('3. Estados: 80% activas, 10% pendientes, 10% canceladas')
    print('4. Usa bulk_create para máximo rendimiento')
    print('\n' + '='*60 + '\n')

    # Paso 1: Actualizar estados pasados
    print('📝 PASO 1: Actualizando estados de reservas pasadas...')
    actualizadas = actualizar_estados_pasados()

    # Paso 2: Crear reservas de diciembre
    print('\n📝 PASO 2: Creando reservas de diciembre...')
    creadas = crear_reservas_diciembre_optimizado()

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
        print('\n\n⚠️  Script interrumpido')
        sys.exit(1)
    except Exception as e:
        print(f'\n❌ Error: {e}')
        import traceback
        traceback.print_exc()
        sys.exit(1)
