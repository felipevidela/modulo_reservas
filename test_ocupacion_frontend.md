# 🧪 Prueba de Ocupación en el Frontend

## ✅ Estado Actual

**Configuración:**
- 6 mesas (4 de capacidad 2, 2 de capacidad 4)
- 351 reservas activas
- 83.6% ocupación promedio
- **SIN solapamientos**

## 📋 Pruebas a Realizar

### TEST 1: Horario con Pocas Mesas (12:00)

**Pasos:**
1. Abre http://localhost:5173
2. Selecciona:
   - Fecha: **Jueves 21 de noviembre**
   - Número de personas: **2**
3. Observa el campo de hora

**Resultado Esperado:**
- Hora 12:00: Debería mostrar "1 mesa disponible" o similar
- Algunas horas deberían mostrar "No disponible"

---

### TEST 2: Horario Completo (18:00-20:00)

**Pasos:**
1. En el mismo formulario
2. Selecciona:
   - Fecha: **Jueves 20 de noviembre**
   - Hora: **18:00** o **20:00**

**Resultado Esperado:**
- 🔴 Debería mostrar "0 mesas disponibles" o "No disponible"
- NO debería permitir seleccionar mesas

---

### TEST 3: Horario con Disponibilidad Media

**Pasos:**
1. Selecciona:
   - Fecha: **Sábado 22 de noviembre**
   - Hora: **14:00**

**Resultado Esperado:**
- 🟢 Debería mostrar "3 mesas disponibles"
- Al seleccionar el horario, debería mostrar las mesas 1, 4, 5 disponibles
- Mesas 2, 3, 6 NO deberían aparecer (están ocupadas)

---

### TEST 4: Crear Reserva en Horario Disponible

**Pasos:**
1. Selecciona:
   - Fecha: **Miércoles 19 de noviembre**
   - Hora: **12:00**
   - Personas: **2**
2. Debería mostrar mesas disponibles (1, 4, 6)
3. Completa el formulario:
   - Email: test@example.com
   - Nombre: Juan
   - Apellido: Prueba
   - RUT: 11.111.111-1
   - Teléfono: +56 9 1111 1111
   - Mesa: Selecciona una disponible
   - **NO marcar** checkbox "Crear cuenta"
4. Envía la reserva

**Resultado Esperado:**
- ✅ Reserva creada exitosamente
- Email enviado a consola de Django
- Mensaje de éxito en el frontend

---

### TEST 5: Intentar Reservar en Horario Lleno

**Pasos:**
1. Selecciona:
   - Fecha: **Jueves 20 de noviembre**
   - Hora: **18:00**

**Resultado Esperado:**
- 🔴 NO debería haber mesas disponibles para seleccionar
- El formulario debería indicar que no hay disponibilidad

---

## 📊 Ocupación por Día y Turno

### Jueves 20/11 (Día muy ocupado)
```
12:00-14:00: 🟡 5/6 mesas (83%) - Mesa 6 disponible
14:00-16:00: 🔴 6/6 mesas (100%) - COMPLETO
16:00-18:00: 🔴 6/6 mesas (100%) - COMPLETO
18:00-20:00: 🔴 6/6 mesas (100%) - COMPLETO
20:00-22:00: 🔴 6/6 mesas (100%) - COMPLETO
```

### Miércoles 19/11 (Ocupación moderada)
```
12:00-14:00: 🟢 3/6 mesas (50%) - Mesas 1,4,6 disponibles
14:00-16:00: 🟢 3/6 mesas (50%) - Mesas 2,3,6 disponibles
16:00-18:00: 🟢 4/6 mesas (67%) - Mesas 1,2,5,6 disponibles
18:00-20:00: 🔴 6/6 mesas (100%) - COMPLETO
20:00-22:00: 🟡 5/6 mesas (83%) - Mesa 3 disponible
```

### Sábado 22/11 (Fin de semana)
```
12:00-14:00: 🟢 4/6 mesas (67%) - Mesas 1,2,5,6 disponibles
14:00-16:00: 🟢 3/6 mesas (50%) - Mesas 1,4,5 disponibles
16:00-18:00: 🔴 6/6 mesas (100%) - COMPLETO
18:00-20:00: 🔴 6/6 mesas (100%) - COMPLETO
20:00-22:00: 🔴 6/6 mesas (100%) - COMPLETO
```

---

## ✅ Verificación Final

- [ ] Las horas muestran cantidad correcta de mesas disponibles
- [ ] Los horarios llenos (100%) NO permiten hacer reservas
- [ ] Los horarios con disponibilidad muestran solo las mesas libres
- [ ] Se puede crear una reserva exitosamente en horario disponible
- [ ] Los horarios prime (18:00-22:00) están mayormente llenos
- [ ] Los horarios de almuerzo (12:00-16:00) tienen más disponibilidad

---

## 🚀 Instrucciones de Uso

1. **Abrir el frontend**: http://localhost:5173
2. **Probar diferentes fechas y horarios** según la tabla de ocupación
3. **Verificar que el sistema responde correctamente** a la disponibilidad
4. **Intentar crear reservas** en horarios disponibles y llenos

---

## 📝 Notas

- Todos los turnos son de 2 horas (12-14, 14-16, 16-18, 18-20, 20-22)
- NO hay solapamientos - cada mesa puede tener máximo 1 reserva por turno
- La ocupación es mayor en horarios nocturnos (18:00-22:00)
- Los fines de semana tienen alta ocupación en la tarde/noche

---

**Última actualización**: Estado con 351 reservas, 83.6% ocupación global
