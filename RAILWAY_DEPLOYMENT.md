# 🚀 Guía de Deployment en Railway - Sistema de Reservas

Esta guía te ayudará a desplegar tu sistema de reservas completo (backend Django + frontend React + base de datos PostgreSQL) en **Railway** usando una sola plataforma.

## ✅ Ventajas de esta Configuración

- ✨ **Todo en un solo lugar**: Backend, frontend y base de datos
- 🔒 **No necesitas CORS**: Todo está en el mismo dominio
- 💰 **Gratis para empezar**: Railway incluye $5 USD de crédito
- 🚀 **Deploy automático**: Cada push a GitHub redespliega automáticamente
- 📦 **Simple**: Una sola URL para toda tu aplicación

---

## 📋 Pre-requisitos

Antes de comenzar, asegúrate de tener:

- ✅ Cuenta en [GitHub](https://github.com) (gratuita)
- ✅ Cuenta en [Railway](https://railway.com) (gratuita, incluye $5 USD de crédito)
- ✅ Tu código subido a GitHub (repositorio `modulo_reservas`)
- ✅ Node.js instalado en Railway (se instala automáticamente)

---

## 🚀 Desplegar en Railway

### Paso 1: Crear Proyecto en Railway desde GitHub

1. Ve a [railway.app](https://railway.app) y haz login
2. Haz clic en **"New Project"** o **"Start a New Project"**
3. Selecciona **"Deploy from GitHub repo"**
4. Si es la primera vez, Railway te pedirá autorización para acceder a tu GitHub
5. Busca y selecciona tu repositorio **"modulo_reservas"**
6. Railway detectará automáticamente que es un proyecto Python/Django

### Paso 2: ⚠️ Configurar Root Directory (MUY IMPORTANTE)

Tu código Django está en una subcarpeta, no en la raíz:

1. Una vez creado el servicio, haz clic en él
2. Ve a **"Settings"** (pestaña superior)
3. Busca la sección **"Root Directory"**
4. Haz clic en **"Edit"** o el ícono de lápiz
5. Escribe exactamente: `REST frameworks/ReservaProject`
6. Haz clic en **"Save"** o presiona Enter

⚠️ **Sin esto, el deployment NO funcionará.**

### Paso 3: Agregar Base de Datos PostgreSQL

1. En tu proyecto de Railway, haz clic en **"+ New"** (botón superior derecho)
2. Selecciona **"Database"**
3. Selecciona **"Add PostgreSQL"**
4. Railway creará automáticamente la base de datos y la variable `DATABASE_URL`

### Paso 4: Conectar la Base de Datos con Django

Railway necesita que el servicio Django tenga acceso a `DATABASE_URL`:

1. Haz clic en tu servicio **Django** (no en Postgres)
2. Ve a la pestaña **"Variables"**
3. Haz clic en **"+ New Variable"**
4. Selecciona **"Add Reference"** (o "Variable Reference")
5. Selecciona el servicio **Postgres**
6. Selecciona la variable **DATABASE_URL**
7. Esto creará automáticamente `${{Postgres.DATABASE_URL}}` en tu servicio Django

### Paso 5: Configurar Variables de Entorno

En la pestaña **"Variables"** del servicio Django, agrega estas variables (una por una):

#### DJANGO_SECRET_KEY
```bash
DJANGO_SECRET_KEY=3l1(l_*c_m(ml)e@zxf@1sg7i=tsj$g_s#nghlh(*=ldqkm1yy
```

#### FIELD_ENCRYPTION_KEY
```bash
FIELD_ENCRYPTION_KEY=okcgCpPIrFup7fdfanH-_wuUjZ0cnpMK-oXvFACdR0A=
```

#### DEBUG
```bash
DEBUG=False
```

**Nota**: Haz clic en **"+ New Variable"** para cada una.

### Paso 6: Generar Dominio Público

1. Ve a **"Settings"** de tu servicio Django
2. Busca la sección **"Networking"** o **"Domains"**
3. Haz clic en **"Generate Domain"**
4. Railway te dará una URL como: `https://modulo-reservas-production-XXXX.up.railway.app`
5. **Copia esta URL** (la necesitarás en el siguiente paso)

### Paso 7: Configurar ALLOWED_HOSTS

Ahora que tienes el dominio, agrégalo a las variables de entorno:

1. Ve a **"Variables"** del servicio Django
2. Haz clic en **"+ New Variable"**
3. Agrega:

```bash
ALLOWED_HOSTS=modulo-reservas-production-XXXX.up.railway.app
```

⚠️ **Importante**: Reemplaza con tu dominio real (sin `https://`)

### Paso 8: Esperar el Deployment

1. Railway comenzará a construir y desplegar automáticamente
2. Ve a la pestaña **"Deployments"**
3. Espera a que aparezca ✅ **"Success"** (puede tomar 3-7 minutos la primera vez)
4. Durante el build verás:
   - `📦 Construyendo frontend React...`
   - `Running migrations...`
   - `Collecting static files...`
   - `Starting gunicorn...`

### Paso 9: Crear Superusuario (Opcional)

Para acceder al panel de administración de Django:

1. En Railway, ve a tu servicio Django
2. Haz clic en la pestaña **"Deployments"**
3. Haz clic en el deployment exitoso más reciente
4. Haz clic en **"View Logs"**
5. En la parte superior, haz clic en el ícono de **terminal** (si está disponible)
6. O usa el comando CLI de Railway:

```bash
railway run python manage.py createsuperuser
```

7. Sigue las instrucciones para crear el usuario admin

---

## ✅ Verificación Final

### 1. Verificar que todo funciona

Abre tu navegador y visita tu URL de Railway:

```
https://tu-app.up.railway.app
```

Deberías ver:
- ✅ La página de login del sistema de reservas
- ✅ Sin errores en la consola del navegador
- ✅ Puedes registrarte o hacer login

### 2. Verificar la API

Visita la API directamente:

```
https://tu-app.up.railway.app/api/
```

Deberías ver:
- ✅ La interfaz de Django REST Framework
- ✅ Lista de endpoints disponibles

### 3. Verificar el Admin de Django

Visita el panel de administración:

```
https://tu-app.up.railway.app/admin/
```

Deberías ver:
- ✅ La página de login de Django Admin
- ✅ Puedes hacer login con el superusuario que creaste

---

## 🔧 Solución de Problemas

### Error: "Application failed to respond"

**Problema**: El servicio no está respondiendo.

**Solución**:
1. Ve a **Deployments** → **View Logs**
2. Busca errores en los logs
3. Verifica que el **Root Directory** esté configurado: `REST frameworks/ReservaProject`
4. Verifica que todas las variables de entorno estén configuradas

### Error: "DisallowedHost at /"

**Problema**: Django rechaza las peticiones porque el dominio no está en `ALLOWED_HOSTS`.

**Solución**:
1. Ve a **Variables**
2. Verifica que `ALLOWED_HOSTS` incluya tu dominio de Railway (sin `https://`)
3. Ejemplo correcto: `modulo-reservas-production-XXXX.up.railway.app`
4. Ejemplo incorrecto: `https://modulo-reservas-production-XXXX.up.railway.app`

### Error: "Build failed" o "npm not found"

**Problema**: El build del frontend falló.

**Solución**:
1. Verifica que el archivo `build.sh` existe en la raíz del repositorio
2. Verifica que el `Procfile` incluye: `release: bash ../../build.sh && python manage.py migrate && python manage.py collectstatic --noinput`
3. Railway debería instalar Node.js automáticamente, pero si no:
   - Ve a **Settings** → **Build Command**
   - Asegúrate de que Railway detecte que necesita Node.js

### Error: "Cannot connect to database"

**Problema**: Django no puede conectarse a PostgreSQL.

**Solución**:
1. Verifica que agregaste el servicio PostgreSQL en Railway
2. Ve a **Variables** del servicio Django
3. Verifica que existe la variable `DATABASE_URL`
4. Debería verse como: `${{Postgres.DATABASE_URL}}`
5. Si no existe, agrega una **Variable Reference** al servicio Postgres

### Frontend muestra página en blanco

**Problema**: El frontend no carga o muestra una página en blanco.

**Solución**:
1. Abre las **DevTools** del navegador (F12)
2. Ve a la pestaña **"Console"**
3. Busca errores de JavaScript
4. Si ves errores de "Failed to fetch" o "Network Error":
   - El frontend está intentando conectarse a `http://localhost:8000`
   - Verifica que el archivo `Reservas/src/services/reservasApi.js` use rutas relativas (sin `http://localhost`)

### Error: "Static files not found"

**Problema**: Los archivos CSS/JS no cargan.

**Solución**:
1. Verifica que el `Procfile` incluye `collectstatic`
2. Ve a **Deployments** → **View Logs**
3. Busca: `Collecting static files...`
4. Debería mostrar: `X static files copied to 'staticfiles'`

---

## 🔄 Actualizaciones Futuras

Cada vez que hagas cambios en tu código:

1. Haz commit y push a GitHub:
```bash
git add .
git commit -m "Descripción de los cambios"
git push origin main
```

2. Railway detectará los cambios automáticamente
3. Iniciará un nuevo deployment automáticamente
4. Espera 3-5 minutos
5. Verifica que el nuevo deployment tenga ✅ **"Success"**
6. Refresca tu navegador para ver los cambios

---

## 📊 Monitoreo y Logs

### Ver Logs en Tiempo Real

1. Ve a tu servicio Django en Railway
2. Haz clic en **"Deployments"**
3. Haz clic en el deployment activo
4. Haz clic en **"View Logs"**
5. Los logs se actualizarán en tiempo real

### Métricas de Uso

1. Ve a tu proyecto en Railway
2. Haz clic en **"Metrics"** (si está disponible)
3. Verás:
   - CPU usage
   - Memory usage
   - Network traffic
   - Request count

---

## 💰 Costos y Límites

### Plan Gratuito de Railway

- ✅ $5 USD de crédito mensual
- ✅ Suficiente para proyectos pequeños/pruebas
- ✅ ~500 horas de ejecución/mes
- ⚠️ Después de gastar el crédito, el servicio se pausa

### Actualizar a Plan de Pago

Si necesitas más recursos:
1. Ve a **Settings** de tu proyecto
2. Haz clic en **"Upgrade"**
3. Agrega una tarjeta de crédito
4. Plans desde $5/mes

---

## 🎉 ¡Listo!

Tu sistema de reservas ahora está desplegado en producción en Railway:

- **URL principal**: https://tu-app.up.railway.app
- **API**: https://tu-app.up.railway.app/api/
- **Admin**: https://tu-app.up.railway.app/admin/

### Próximos Pasos Opcionales

- 🌐 Configurar un dominio personalizado
- 📧 Configurar notificaciones por email
- 📊 Agregar monitoreo con Sentry
- 🔒 Configurar backups de la base de datos
- 📈 Agregar analytics con Google Analytics

---

## 📞 Recursos Adicionales

- [Railway Docs](https://docs.railway.app)
- [Django Deployment](https://docs.djangoproject.com/en/5.2/howto/deployment/)
- [Railway Community](https://help.railway.app)

---

**Última actualización**: Noviembre 2025
