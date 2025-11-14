#!/usr/bin/env python
"""
Script para crear mesas iniciales en la base de datos
Uso: python crear_mesas.py
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ReservaProject.settings')
django.setup()

from mainApp.models import Mesa

def crear_mesas():
    """Crear mesas iniciales si no existen"""

    # Configuración de mesas
    # Formato: (numero, capacidad)
    configuracion_mesas = [
        # Mesas para 2 personas
        (1, 2), (2, 2), (3, 2), (4, 2),
        # Mesas para 4 personas
        (5, 4), (6, 4), (7, 4), (8, 4), (9, 4), (10, 4),
        # Mesas para 6 personas
        (11, 6), (12, 6), (13, 6),
        # Mesas para 8 personas
        (14, 8), (15, 8),
    ]

    mesas_creadas = 0
    mesas_existentes = 0

    for numero, capacidad in configuracion_mesas:
        mesa, created = Mesa.objects.get_or_create(
            numero=numero,
            defaults={'capacidad': capacidad, 'estado': 'disponible'}
        )

        if created:
            print(f'✓ Mesa {numero} creada (capacidad: {capacidad} personas)')
            mesas_creadas += 1
        else:
            print(f'○ Mesa {numero} ya existe (capacidad: {mesa.capacidad} personas)')
            mesas_existentes += 1

    print(f'\n--- Resumen ---')
    print(f'Mesas creadas: {mesas_creadas}')
    print(f'Mesas existentes: {mesas_existentes}')
    print(f'Total de mesas: {Mesa.objects.count()}')

if __name__ == '__main__':
    print('Creando mesas iniciales...\n')
    crear_mesas()
