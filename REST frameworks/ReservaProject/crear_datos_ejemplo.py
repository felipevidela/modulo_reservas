#!/usr/bin/env python
"""
Script para crear datos de ejemplo en la base de datos
Simula un restaurante muy ocupado del 14 Nov al 30 Dic
Uso: python crear_datos_ejemplo.py
"""
import os
import sys
import django
from datetime import date, time, timedelta
import random

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ReservaProject.settings')
django.setup()

from django.contrib.auth.models import User
from mainApp.models import Perfil, Mesa, Reserva

# Nombres de ejemplo
NOMBRES = [
    'Juan', 'María', 'Pedro', 'Ana', 'Luis', 'Carmen', 'Carlos', 'Isabel',
    'Jorge', 'Patricia', 'Roberto', 'Laura', 'Miguel', 'Sofía', 'Diego',
    'Valentina', 'Andrés', 'Camila', 'Fernando', 'Daniela', 'Ricardo',
    'Gabriela', 'Sergio', 'Catalina', 'Javier', 'Natalia', 'Rodrigo',
    'Fernanda', 'Pablo', 'Carolina', 'Martín', 'Alejandra', 'Raúl',
    'Victoria', 'Álvaro', 'Francisca', 'Tomás', 'Antonia', 'Matías', 'Josefa'
]

APELLIDOS = [
    'González', 'Rodríguez', 'Fernández', 'López', 'Martínez', 'García',
    'Pérez', 'Sánchez', 'Ramírez', 'Torres', 'Flores', 'Rivera', 'Gómez',
    'Díaz', 'Muñoz', 'Rojas', 'Contreras', 'Silva', 'Sepúlveda', 'Morales'
]

# Horarios de reserva
HORARIOS_ALMUERZO = ['12:00', '12:30', '13:00', '13:30', '14:00', '14:30']
HORARIOS_CENA = ['19:00', '19:30', '20:00', '20:30', '21:00', '21:30']

def generar_rut():
    """Genera un RUT chileno válido de ejemplo"""
    numero = random.randint(10000000, 25000000)
    # Simplificado: solo formato, no validación real
    rut_str = f"{numero:,}".replace(',', '.')
    return f"{rut_str}-{random.randint(0, 9)}"

def generar_telefono():
    """Genera un teléfono chileno de ejemplo"""
    return f"+56 9 {random.randint(1000, 9999)} {random.randint(1000, 9999)}"

def crear_usuarios():
    """Crea usuarios de ejemplo si no existen"""
    print("Creando usuarios de ejemplo...")

    usuarios_creados = 0

    for i in range(40):
        nombre = random.choice(NOMBRES)
        apellido = random.choice(APELLIDOS)
        username = f"{nombre.lower()}.{apellido.lower()}{i}".replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
        email = f"{username}@email.com"

        # Verificar si ya existe
        if User.objects.filter(username=username).exists():
            continue

        # Crear usuario
        user = User.objects.create_user(
            username=username,
            email=email,
            password='password123',
            first_name=nombre,
            last_name=apellido
        )

        # Crear o actualizar perfil
        perfil, created = Perfil.objects.get_or_create(
            user=user,
            defaults={
                'rol': 'cliente',
                'nombre_completo': f"{nombre} {apellido}",
                'rut': generar_rut(),
                'telefono': generar_telefono(),
                'email': email
            }
        )

        usuarios_creados += 1

    print(f"✓ {usuarios_creados} usuarios creados")
    print(f"  Total usuarios en sistema: {User.objects.count()}")

def crear_reservas():
    """Crea reservas de ejemplo del 14 Nov al 30 Dic"""
    print("\nCreando reservas de ejemplo (14 Nov - 30 Dic)...")

    # Obtener todas las mesas
    mesas = list(Mesa.objects.all())
    if not mesas:
        print("❌ No hay mesas en la base de datos. Ejecuta crear_mesas.py primero.")
        return

    # Obtener todos los clientes
    clientes = list(User.objects.filter(perfil__rol='cliente'))
    if not clientes:
        print("❌ No hay clientes en la base de datos.")
        return

    # Período de reservas
    fecha_inicio = date(2025, 11, 14)
    fecha_fin = date(2025, 12, 30)
    fecha_actual = date.today()

    reservas_creadas = 0

    # Iterar por cada día
    fecha = fecha_inicio
    while fecha <= fecha_fin:
        # Determinar cuántas reservas crear para este día
        # Más reservas en fines de semana
        if fecha.weekday() in [4, 5, 6]:  # Viernes, Sábado, Domingo
            num_reservas_almuerzo = random.randint(9, 11)
            num_reservas_cena = random.randint(11, 13)
        else:
            num_reservas_almuerzo = random.randint(7, 9)
            num_reservas_cena = random.randint(9, 11)

        # Crear reservas de almuerzo
        for _ in range(num_reservas_almuerzo):
            hora_str = random.choice(HORARIOS_ALMUERZO)
            mesa = random.choice(mesas)
            cliente = random.choice(clientes)

            # Determinar estado según la fecha
            if fecha < fecha_actual:
                # Reservas pasadas: mayoría completadas, algunas canceladas
                estado = 'completada' if random.random() < 0.92 else 'cancelada'
            elif fecha == fecha_actual:
                estado = 'activa'
            else:
                # Reservas futuras: mayoría pendientes, algunas canceladas
                estado = 'pendiente' if random.random() < 0.95 else 'cancelada'

            # Número de personas apropiado para la mesa
            max_personas = min(mesa.capacidad, 8)
            min_personas = max(1, mesa.capacidad - 2)
            num_personas = random.randint(min_personas, max_personas)

            # Verificar si ya existe una reserva similar
            hora_obj = time(*map(int, hora_str.split(':')))
            if Reserva.objects.filter(
                mesa=mesa,
                fecha_reserva=fecha,
                hora_inicio=hora_obj,
                estado__in=['pendiente', 'activa']
            ).exists():
                continue

            try:
                Reserva.objects.create(
                    cliente=cliente,
                    mesa=mesa,
                    fecha_reserva=fecha,
                    hora_inicio=hora_obj,
                    num_personas=num_personas,
                    estado=estado,
                    notas=f"Reserva de {estado}"
                )
                reservas_creadas += 1
            except Exception as e:
                # Saltar si hay conflicto de horario
                pass

        # Crear reservas de cena
        for _ in range(num_reservas_cena):
            hora_str = random.choice(HORARIOS_CENA)
            mesa = random.choice(mesas)
            cliente = random.choice(clientes)

            if fecha < fecha_actual:
                estado = 'completada' if random.random() < 0.92 else 'cancelada'
            elif fecha == fecha_actual:
                estado = 'activa'
            else:
                estado = 'pendiente' if random.random() < 0.95 else 'cancelada'

            max_personas = min(mesa.capacidad, 8)
            min_personas = max(1, mesa.capacidad - 2)
            num_personas = random.randint(min_personas, max_personas)

            hora_obj = time(*map(int, hora_str.split(':')))
            if Reserva.objects.filter(
                mesa=mesa,
                fecha_reserva=fecha,
                hora_inicio=hora_obj,
                estado__in=['pendiente', 'activa']
            ).exists():
                continue

            try:
                Reserva.objects.create(
                    cliente=cliente,
                    mesa=mesa,
                    fecha_reserva=fecha,
                    hora_inicio=hora_obj,
                    num_personas=num_personas,
                    estado=estado,
                    notas=f"Reserva de {estado}"
                )
                reservas_creadas += 1
            except Exception as e:
                pass

        fecha += timedelta(days=1)

    print(f"✓ {reservas_creadas} reservas creadas")
    print(f"  Total reservas en sistema: {Reserva.objects.count()}")

    # Estadísticas
    print("\n--- Estadísticas de Reservas ---")
    for estado_key, estado_label in Reserva.ESTADO_CHOICES:
        count = Reserva.objects.filter(estado=estado_key).count()
        print(f"  {estado_label}: {count}")

def main():
    print("=" * 60)
    print("CREANDO DATOS DE EJEMPLO - RESTAURANTE OCUPADO")
    print("Período: 14 Noviembre - 30 Diciembre 2025")
    print("=" * 60)

    # Verificar que existan mesas
    if not Mesa.objects.exists():
        print("\n⚠️  No hay mesas en la base de datos.")
        print("   Ejecuta primero: python crear_mesas.py")
        return

    crear_usuarios()
    crear_reservas()

    print("\n" + "=" * 60)
    print("✓ DATOS DE EJEMPLO CREADOS EXITOSAMENTE")
    print("=" * 60)

if __name__ == '__main__':
    main()
