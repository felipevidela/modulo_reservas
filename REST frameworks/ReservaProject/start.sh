#!/bin/bash
set -e  # Detener si hay error crítico

echo "🚀 Iniciando deployment en Railway..."

# 1. Ejecutar migraciones
echo "📦 Ejecutando migraciones..."
python manage.py migrate --noinput

# 2. Crear mesas (no detener si falla)
echo "🪑 Creando mesas iniciales..."
python crear_mesas.py || echo "⚠️  Advertencia: No se pudieron crear mesas (posiblemente ya existen)"

# 3. Crear superuser (no detener si falla)
echo "👤 Creando superusuario..."
python crear_superuser.py || echo "⚠️  Advertencia: No se pudo crear superusuario (posiblemente ya existe)"

# 4. Recolectar archivos estáticos
echo "📁 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput --clear

# 5. Iniciar Gunicorn
echo "🌐 Iniciando servidor Gunicorn..."
exec gunicorn ReservaProject.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 4 \
    --log-file - \
    --log-level info \
    --access-logfile - \
    --error-logfile -
