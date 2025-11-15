# 🔍 Cómo Ver los Logs de BUILD en Railway (NO los de Runtime)

## ⚠️ Problema Actual

Los logs que me compartiste son **RUNTIME logs** - muestran gunicorn intentando iniciar y fallando.

Necesitamos ver los **BUILD logs** - que muestran Docker construyendo la imagen.

---

## 📋 Paso a Paso para Ver BUILD Logs

### 1. Ve a Railway Dashboard
https://railway.app

### 2. Abre tu Proyecto y Servicio

### 3. Ve a la Pestaña "Deployments"
- Verás una lista de todos los deployments
- El más reciente debería estar arriba

### 4. Haz Clic en el Deployment Más Reciente

### 5. Busca la Pestaña "Build Logs" o "Deploy Logs"
- NO "Runtime Logs" (esos son los que me enviaste)
- Deberías ver algo como:

```
#1 [internal] load build definition from Dockerfile
#2 [internal] load .dockerignore
#3 [frontend-builder 1/7] FROM docker.io/library/node:20-alpine
...
```

---

## 🔄 FORZAR UN REBUILD COMPLETO

**Lo más probable es que Railway esté usando una imagen cacheada antigua.**

### Opción 1: Redeploy desde Railway (MÁS RÁPIDO)

1. En la pestaña **"Deployments"**
2. Encuentra el deployment más reciente
3. Haz clic en **los tres puntos (...) al lado derecho**
4. Selecciona **"Redeploy"**
5. **IMPORTANTE**: Marca la opción **"Clear cache"** si aparece

### Opción 2: Clear Build Cache + Redeploy

1. Ve a **Settings** del servicio
2. Busca **"Danger Zone"** o **"Build Settings"**
3. Haz clic en **"Clear Build Cache"**
4. Confirma
5. Railway automáticamente iniciará un nuevo build

### Opción 3: Forzar con Commit Vacío (desde tu Mac)

Ejecuta el script que creé:

```bash
cd "/Users/felipevidela/Desktop/modulo_reservas"
./redeploy.sh
```

O manualmente:

```bash
cd "/Users/felipevidela/Desktop/modulo_reservas"

# Crear commit vacío para forzar rebuild
git commit --allow-empty -m "Force Railway rebuild with latest fixes"

# Push a GitHub
git push origin main
```

Esto forzará a Railway a hacer un build completamente nuevo.

---

## ✅ Qué Buscar en los BUILD Logs

Una vez que fuerces el rebuild, los BUILD logs deberían mostrar:

### ✅ Build Correcto:

```
#1 [internal] load build definition from Dockerfile
#2 [internal] load .dockerignore
#3 [frontend-builder 1/7] FROM docker.io/library/node:20-alpine
✓ USING NODE 20 (NO 18)

#5 [frontend-builder 4/7] RUN npm ci
✓ Installing ALL dependencies (including devDependencies)

#8 [frontend-builder 7/7] RUN npm run build
  vite v7.2.2 building for production...
  ✓ 42 modules transformed.
  ✓ built in 4.21s
✓ VITE BUILD EXITOSO

#12 [stage-1 6/9] COPY ["REST frameworks/ReservaProject/", "./ReservaProject/"]
✓ COPIA EXITOSA (sintaxis JSON correcta)

#13 [stage-1 7/9] COPY --from=frontend-builder /app/frontend/dist ./Reservas/dist/
✓ FRONTEND COPIADO CORRECTAMENTE

Running migrations:
  No migrations to apply.

Collecting static files...
42 static files copied to 'staticfiles'.

[INFO] Starting gunicorn 23.0.0
[INFO] Listening at: http://0.0.0.0:8000
[INFO] Booting worker with pid: 8
✓ Deployment successful!
```

### ❌ Si Sigue Fallando:

Si después de forzar el rebuild SIGUE mostrando "ModuleNotFoundError: No module named 'Reservas'", entonces:

1. **Comparte los BUILD logs completos** (desde `#1 [internal] load...` hasta el final)
2. **Verifica el commit hash** - en los logs de Railway debería decir qué commit está usando
3. **Verifica que sea commit `eda8444`** - el que tiene nuestro fix

---

## 🎯 Resumen

**Lo que pasó**:
- Railway construyó la imagen Docker ANTES de que subiéramos el fix del FRONTEND_DIR
- Esa imagen quedó cacheada
- Cada vez que Railway reinicia, usa la imagen antigua
- Por eso sigue fallando con el mismo error

**Lo que necesitas hacer**:
1. **Forzar un rebuild completo** (Opción 1, 2 o 3 de arriba)
2. **Esperar 5-10 minutos** mientras Railway construye la nueva imagen
3. **Compartir los BUILD logs** (no los runtime logs)
4. Si el build es exitoso, la app debería iniciar sin errores

---

**Última actualización**: 2025-11-13 18:00
