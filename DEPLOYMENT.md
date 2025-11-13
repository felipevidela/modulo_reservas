# 🚀 Guía de Deployment - Sistema de Reservas

Esta guía te ayudará a desplegar tu sistema de reservas en **Railway** (backend + base de datos) y **Vercel** (frontend).

## 📋 Índice

1. [Pre-requisitos](#pre-requisitos)
2. [Desplegar Backend en Railway](#1-desplegar-backend-en-railway)
3. [Desplegar Frontend en Vercel](#2-desplegar-frontend-en-vercel)
4. [Verificación Final](#3-verificación-final)
5. [Solución de Problemas](#solución-de-problemas)

---

## Pre-requisitos

Antes de comenzar, asegúrate de tener:

- ✅ Cuenta en [GitHub](https://github.com) (gratuita)
- ✅ Cuenta en [Railway](https://railway.com) (gratuita, incluye $5 USD de crédito)
- ✅ Cuenta en [Vercel](https://vercel.com) (gratuita)
- ✅ Tu código subido a un repositorio de GitHub
- ✅ Git instalado en tu computadora

---

## 1. Desplegar Backend en Railway

Railway hospedará tu backend Django y la base de datos PostgreSQL.

### Paso 1.1: Preparar el Repositorio

Primero, asegúrate de que todos los cambios estén guardados y subidos a GitHub:

```bash
# Navega a la carpeta del proyecto
cd "modulo_reservas"

# Verifica el estado de git
git status

# Agrega todos los cambios
git add .

# Crea un commit
git commit -m "Preparar proyecto para deployment en Railway y Vercel"

# Sube los cambios a GitHub
git push origin main
```

### Paso 1.2: Crear Proyecto en Railway

1. Ve a [railway.app](https://railway.app) y haz clic en **"Start a New Project"**
2. Selecciona **"Deploy from GitHub repo"**
3. Si es la primera vez, Railway te pedirá autorización para acceder a tu GitHub
4. Busca y selecciona tu repositorio `modulo_reservas`
5. Railway detectará automáticamente que es un proyecto Django

### Paso 1.3: Agregar Base de Datos PostgreSQL

1. En tu proyecto de Railway, haz clic en **"+ New"**
2. Selecciona **"Database"** → **"Add PostgreSQL"**
3. Railway creará automáticamente la base de datos y la variable `DATABASE_URL`

### Paso 1.4: Configurar Variables de Entorno

En Railway, haz clic en tu servicio backend y ve a la pestaña **"Variables"**.

Agrega las siguientes variables:

```bash
# Django Configuration
DJANGO_SECRET_KEY=tu-clave-super-secreta-generada-aqui
DEBUG=False
ALLOWED_HOSTS=tu-app-name.up.railway.app

# Encryption Key (generar una nueva)
FIELD_ENCRYPTION_KEY=tu-clave-de-encriptacion-fernet

# CORS (agregar después de desplegar en Vercel)
CORS_ALLOWED_ORIGINS=https://tu-frontend.vercel.app
```

#### Cómo generar las claves:

**DJANGO_SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

**FIELD_ENCRYPTION_KEY:**
```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

### Paso 1.5: Configurar el Root Directory

⚠️ **MUY IMPORTANTE**: Tu backend está en `REST frameworks/ReservaProject`, no en la raíz.

1. En Railway, ve a **"Settings"**
2. Busca **"Root Directory"**
3. Escribe: `REST frameworks/ReservaProject`
4. Guarda los cambios

### Paso 1.6: Deploy

1. Railway comenzará a hacer el deploy automáticamente
2. Espera a que aparezca ✅ **"Success"** (puede tomar 2-5 minutos)
3. Haz clic en **"Settings"** → **"Networking"** → **"Generate Domain"**
4. Railway te dará una URL como: `https://tu-app-name.up.railway.app`

### Paso 1.7: Verificar el Backend

1. Abre tu navegador y ve a: `https://tu-app-name.up.railway.app/api/`
2. Deberías ver la interfaz de Django REST Framework
3. Si ves un error 404, verifica que hayas configurado el Root Directory correctamente

### Paso 1.8: Crear Superusuario (Opcional)

Para acceder al panel de administración de Django:

1. En Railway, ve a tu servicio backend
2. Haz clic en la pestaña **"Deployments"**
3. Haz clic en los tres puntos (...) del último deployment exitoso
4. Selecciona **"View Logs"** para abrir la terminal
5. En la terminal, ejecuta:
```bash
python manage.py createsuperuser
```
6. Sigue las instrucciones para crear el usuario admin

---

## 2. Desplegar Frontend en Vercel

Vercel hospedará tu aplicación React.

### Paso 2.1: Preparar Variables de Entorno

Antes de desplegar, necesitas la URL de tu backend de Railway. Cópiala, la necesitarás en el siguiente paso.

Ejemplo: `https://tu-app-name.up.railway.app`

### Paso 2.2: Crear Proyecto en Vercel

1. Ve a [vercel.com](https://vercel.com) y haz clic en **"Add New"** → **"Project"**
2. Importa tu repositorio de GitHub `modulo_reservas`
3. En **"Configure Project"**:
   - **Framework Preset**: Vite
   - **Root Directory**: Haz clic en **"Edit"** y escribe `Reservas`
   - **Build Command**: `npm run build` (por defecto)
   - **Output Directory**: `dist` (por defecto)

### Paso 2.3: Configurar Variables de Entorno

Antes de hacer deploy, agrega las variables de entorno:

1. En Vercel, expande **"Environment Variables"**
2. Agrega la siguiente variable:

```bash
VITE_API_URL=https://tu-app-name.up.railway.app
```

⚠️ **Importante**: Reemplaza `https://tu-app-name.up.railway.app` con la URL real de tu backend en Railway.

⚠️ **NO** incluyas `/api` al final de la URL.

### Paso 2.4: Deploy

1. Haz clic en **"Deploy"**
2. Vercel comenzará a construir y desplegar tu frontend (2-3 minutos)
3. Una vez completado, verás ✅ **"Your project has been successfully deployed"**
4. Vercel te dará una URL como: `https://tu-frontend.vercel.app`

### Paso 2.5: Actualizar CORS en Railway

Ahora que tienes la URL de tu frontend, debes agregarla al CORS del backend:

1. Ve a Railway → Tu servicio backend → **"Variables"**
2. Edita la variable `CORS_ALLOWED_ORIGINS`:
```bash
CORS_ALLOWED_ORIGINS=https://tu-frontend.vercel.app
```
3. Guarda y espera a que Railway redesplegue automáticamente (1-2 minutos)

**Nota**: Si tienes un dominio personalizado en Vercel, agrégalo también:
```bash
CORS_ALLOWED_ORIGINS=https://tu-frontend.vercel.app,https://www.tu-dominio.com
```

### Paso 2.6: Actualizar ALLOWED_HOSTS en Railway (si es necesario)

Si configuraste un dominio personalizado en Vercel, también debes actualizar `ALLOWED_HOSTS`:

1. Ve a Railway → Tu servicio backend → **"Variables"**
2. Edita la variable `ALLOWED_HOSTS`:
```bash
ALLOWED_HOSTS=tu-app-name.up.railway.app,www.tu-dominio.com
```

---

## 3. Verificación Final

### 3.1: Probar el Frontend

1. Abre tu frontend en: `https://tu-frontend.vercel.app`
2. Deberías ver la página de login del sistema de reservas
3. Intenta registrarte o hacer login
4. Si todo funciona, ¡felicidades! 🎉

### 3.2: Probar el Backend

1. Abre tu backend en: `https://tu-app-name.up.railway.app/api/`
2. Deberías ver la interfaz de Django REST Framework
3. Intenta hacer login con el superusuario (si lo creaste)

### 3.3: Verificar la Conexión

Si el frontend no puede conectarse al backend:

1. Abre las **DevTools** del navegador (F12)
2. Ve a la pestaña **"Console"**
3. Busca errores de CORS o de red
4. Verifica que la URL del backend esté correcta

---

## Solución de Problemas

### Error: "Cross-Origin Request Blocked" (CORS)

**Problema**: El frontend no puede conectarse al backend por CORS.

**Solución**:
1. Verifica que `CORS_ALLOWED_ORIGINS` en Railway incluya la URL exacta de tu frontend en Vercel
2. Asegúrate de que no haya espacios en la variable
3. Verifica que uses HTTPS en la URL (no HTTP)

### Error: "DisallowedHost at /"

**Problema**: Railway rechaza las peticiones porque el dominio no está en `ALLOWED_HOSTS`.

**Solución**:
1. Ve a Railway → Variables
2. Verifica que `ALLOWED_HOSTS` incluya tu dominio de Railway
3. Ejemplo: `tu-app-name.up.railway.app`

### Error: "Application failed to respond"

**Problema**: El backend no está respondiendo.

**Solución**:
1. Ve a Railway → Deployments → View Logs
2. Busca errores en los logs
3. Verifica que todas las variables de entorno estén configuradas
4. Verifica que el Root Directory esté bien configurado: `REST frameworks/ReservaProject`

### Error: "Static files not loading"

**Problema**: Los archivos estáticos no cargan en el backend.

**Solución**:
1. Verifica que el Procfile incluya: `release: python manage.py migrate && python manage.py collectstatic --noinput`
2. Redespliega en Railway

### Error: "Cannot connect to database"

**Problema**: El backend no puede conectarse a PostgreSQL.

**Solución**:
1. Verifica que agregaste la base de datos PostgreSQL en Railway
2. Railway debe crear automáticamente la variable `DATABASE_URL`
3. Ve a Variables y verifica que existe `DATABASE_URL`

### El frontend muestra "API URL not configured"

**Problema**: La variable de entorno no está configurada en Vercel.

**Solución**:
1. Ve a Vercel → Tu proyecto → Settings → Environment Variables
2. Verifica que `VITE_API_URL` esté configurada
3. Si la agregaste después del primer deploy, redespliega el proyecto

---

## 🎉 ¡Listo!

Tu sistema de reservas ahora está desplegado en producción:

- **Backend**: https://tu-app-name.up.railway.app
- **Frontend**: https://tu-frontend.vercel.app

### Próximos Pasos

- 🌐 Configura un dominio personalizado (opcional)
- 📧 Configura notificaciones por email (opcional)
- 📊 Agrega monitoreo y analytics (opcional)
- 🔒 Configura HTTPS (ya viene por defecto)

### Actualizaciones Futuras

Cada vez que hagas cambios en tu código:

1. Haz commit y push a GitHub:
```bash
git add .
git commit -m "Descripción de los cambios"
git push origin main
```

2. Railway y Vercel detectarán los cambios automáticamente y redesplegarán tu aplicación

---

## 📞 Soporte

Si tienes problemas:

1. Revisa los logs en Railway (Deployments → View Logs)
2. Revisa los logs en Vercel (Deployments → Function Logs)
3. Verifica las variables de entorno en ambas plataformas
4. Consulta la documentación oficial:
   - [Railway Docs](https://docs.railway.app)
   - [Vercel Docs](https://vercel.com/docs)
   - [Django Deployment](https://docs.djangoproject.com/en/5.2/howto/deployment/)

---

**Última actualización**: Noviembre 2025
