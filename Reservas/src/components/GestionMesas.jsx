import { useState, useEffect } from 'react';
import { getMesas, updateEstadoMesa, getReservas } from '../services/reservasApi';
import { handleError } from '../utils/errorHandler';

export default function GestionMesas() {
  const [mesas, setMesas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filtroEstado, setFiltroEstado] = useState('TODOS');
  const [mesaEditando, setMesaEditando] = useState(null);
  const [success, setSuccess] = useState('');

  // Nuevos estados para filtro de fecha
  const [fechaFiltro, setFechaFiltro] = useState(() => new Date().toISOString().slice(0, 10));
  const [horaFiltro, setHoraFiltro] = useState('');
  const [reservasPorFecha, setReservasPorFecha] = useState([]);
  const [mostrarDisponibilidad, setMostrarDisponibilidad] = useState(true);

  useEffect(() => {
    cargarMesas();
    // Auto-actualizar cada 30 segundos
    const interval = setInterval(cargarMesas, 30000);
    return () => clearInterval(interval);
  }, []);

  // Cargar reservas cuando cambia la fecha
  useEffect(() => {
    if (mostrarDisponibilidad) {
      cargarReservasPorFecha();
    }
  }, [fechaFiltro, mostrarDisponibilidad]);

  const cargarMesas = async () => {
    try {
      setLoading(true);
      const data = await getMesas({ fecha: mostrarDisponibilidad ? fechaFiltro : undefined, hora: mostrarDisponibilidad ? horaFiltro : undefined });
      setMesas(data);
      setError('');
    } catch (err) {
      setError('Error al cargar mesas');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const cargarReservasPorFecha = async () => {
    try {
      const reservas = await getReservas({ fecha: fechaFiltro });
      const filtradasPorHora = horaFiltro
        ? reservas.filter(r => r.hora && r.hora.startsWith(horaFiltro))
        : reservas;
      setReservasPorFecha(filtradasPorHora);
    } catch (err) {
      console.error('Error al cargar reservas:', err);
      setReservasPorFecha([]);
    }
  };

  const handleCambiarEstado = async (mesaId, nuevoEstado) => {
    // FIX #34 (MENOR): Transacciones atómicas en frontend
    // Guardar estado anterior en caso de fallo
    const estadoAnteriorMesas = [...mesas];
    const mesaAnterior = mesas.find(m => m.id === mesaId);

    // Si hay reservas en la fecha/hora seleccionada, advertir antes de liberar/ocupar
    if (mostrarDisponibilidad && (nuevoEstado === 'disponible' || nuevoEstado === 'ocupada')) {
      const reservasMesa = getReservasMesa(mesaAnterior?.numero || mesaId);
      if (reservasMesa.length > 0) {
        const hayChoqueHora = horaFiltro
          ? reservasMesa.some(r => r.hora && r.hora.startsWith(horaFiltro))
          : true;
        if (hayChoqueHora) {
          const continuar = window.confirm(
            `Esta mesa tiene reservas para ${fechaFiltro}${horaFiltro ? ` a las ${horaFiltro}` : ''}. ¿Seguro desea marcarla como ${nuevoEstado}?`
          );
          if (!continuar) return;
        }
      }
    }

    try {
      // Paso 1: Actualizar estado en el backend (operación crítica)
      await updateEstadoMesa({ id: mesaId, nuevoEstado });

      // Paso 2: Solo si el paso 1 fue exitoso, recargar mesas
      try {
        await cargarMesas();
      } catch (reloadErr) {
        // Si falla la recarga, restaurar estado anterior visualmente
        console.error('Error al recargar mesas, restaurando vista anterior:', reloadErr);
        setMesas(estadoAnteriorMesas);
        // Mostrar warning pero considerar la operación exitosa
        setSuccess('Estado actualizado, pero hubo un error al recargar. Actualice la página manualmente.');
        setTimeout(() => setSuccess(''), 5000);
      }

      // Paso 3: Solo si todo fue exitoso, limpiar UI
      setMesaEditando(null);

      // FIX #26 (MODERADO): Manejo de errores consistente - usar setSuccess en lugar de alert
      if (!success) { // Solo mostrar si no se mostró el warning anterior
        setSuccess('Estado de la mesa actualizado correctamente');
        // Limpiar mensaje después de 3 segundos
        setTimeout(() => setSuccess(''), 3000);
      }
    } catch (err) {
      // Si falla la actualización principal, restaurar estado visual anterior
      setMesas(estadoAnteriorMesas);
      // FIX #26 (MODERADO): Manejo de errores consistente
      await handleError(err, 'actualizar estado de la mesa', setError);
    }
  };

  const getEstadoColor = (estado) => {
    const colores = {
      disponible: 'success',
      reservada: 'warning',
      ocupada: 'danger',
      limpieza: 'info'
    };
    return colores[estado] || 'secondary';
  };

  const getEstadoIcon = (estado) => {
    const iconos = {
      disponible: 'bi-check-circle',
      reservada: 'bi-clock',
      ocupada: 'bi-people-fill',
      limpieza: 'bi-droplet'
    };
    return iconos[estado] || 'bi-question-circle';
  };

  // Función para obtener reservas de una mesa en la fecha seleccionada
  const getReservasMesa = (numeroMesa) => {
    if (!mostrarDisponibilidad) return [];
    const mesaFormatted = `M${String(numeroMesa).padStart(2, '0')}`;
    return reservasPorFecha.filter(r => r.mesa === mesaFormatted);
  };

  // Función para verificar si una mesa tiene reservas en la fecha
  const tieneReservas = (numeroMesa) => {
    return getReservasMesa(numeroMesa).length > 0;
  };

  const mesasFiltradas = filtroEstado === 'TODOS'
    ? mesas
    : mesas.filter(m => m.estado === filtroEstado.toLowerCase());

  if (loading && mesas.length === 0) {
    return (
      <div className="text-center py-5">
        <div className="spinner-border text-primary" role="status">
          <span className="visually-hidden">Cargando...</span>
        </div>
        <p className="mt-2">Cargando mesas...</p>
      </div>
    );
  }

  return (
    <div className="container-fluid">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 className="mb-0">Gestión de Mesas</h2>
        <button
          className="btn btn-outline-primary btn-sm"
          onClick={cargarMesas}
          disabled={loading}
        >
          {loading ? (
            <>
              <span className="spinner-border spinner-border-sm me-1"></span>
              Actualizando...
            </>
          ) : (
            <>
              <i className="bi bi-arrow-clockwise me-1"></i>
              Actualizar
            </>
          )}
        </button>
      </div>

      {error && (
        <div className="alert alert-danger alert-dismissible fade show" role="alert">
          {error}
          <button type="button" className="btn-close" onClick={() => setError('')}></button>
        </div>
      )}

      {success && (
        <div className="alert alert-success alert-dismissible fade show" role="alert">
          {success}
          <button type="button" className="btn-close" onClick={() => setSuccess('')}></button>
        </div>
      )}

      {/* Filtros */}
      <div className="card border-0 shadow-sm mb-4">
        <div className="card-body">
          <div className="row g-3">
            {/* Filtro de Estado */}
            <div className="col-12">
              <label className="form-label small fw-bold">Filtrar por Estado Actual:</label>
              <div className="btn-group d-flex flex-wrap" role="group">
                <button
                  type="button"
                  className={`btn ${filtroEstado === 'TODOS' ? 'btn-primary' : 'btn-outline-primary'}`}
                  onClick={() => setFiltroEstado('TODOS')}
                >
                  TODOS
                </button>
                <button
                  type="button"
                  className={`btn ${filtroEstado === 'DISPONIBLE' ? 'btn-success' : 'btn-outline-success'}`}
                  onClick={() => setFiltroEstado('DISPONIBLE')}
                >
                  DISPONIBLE
                </button>
                <button
                  type="button"
                  className={`btn ${filtroEstado === 'RESERVADA' ? 'btn-warning' : 'btn-outline-warning'}`}
                  onClick={() => setFiltroEstado('RESERVADA')}
                >
                  RESERVADA
                </button>
                <button
                  type="button"
                  className={`btn ${filtroEstado === 'OCUPADA' ? 'btn-danger' : 'btn-outline-danger'}`}
                  onClick={() => setFiltroEstado('OCUPADA')}
                >
                  OCUPADA
                </button>
                <button
                  type="button"
                  className={`btn ${filtroEstado === 'LIMPIEZA' ? 'btn-info' : 'btn-outline-info'}`}
                  onClick={() => setFiltroEstado('LIMPIEZA')}
                >
                  EN LIMPIEZA
                </button>
              </div>
            </div>

            {/* Toggle para mostrar disponibilidad */}
            <div className="col-12 border-top pt-3">
              <div className="d-flex flex-wrap align-items-center gap-3">
                <div className="form-check form-switch mb-0">
                  <input
                    className="form-check-input"
                    type="checkbox"
                    id="toggleDisponibilidad"
                    checked={mostrarDisponibilidad}
                    onChange={(e) => setMostrarDisponibilidad(e.target.checked)}
                  />
                  <label className="form-check-label fw-bold" htmlFor="toggleDisponibilidad">
                    <i className="bi bi-calendar3 me-2"></i>
                    Ver disponibilidad por fecha/hora
                  </label>
                </div>
                {mostrarDisponibilidad && (
                  <div className="d-flex flex-wrap align-items-center gap-2">
                    <span className="badge rounded-pill bg-light text-dark">
                      <i className="bi bi-calendar-check me-1"></i>
                      {new Date(fechaFiltro + 'T00:00:00').toLocaleDateString('es-ES', {
                        weekday: 'short',
                        day: 'numeric',
                        month: 'short'
                      })}
                    </span>
                    {horaFiltro && (
                      <span className="badge rounded-pill bg-info text-white">
                        <i className="bi bi-clock me-1"></i>
                        {horaFiltro}
                      </span>
                    )}
                    <button
                      className="btn btn-link btn-sm text-decoration-none"
                      onClick={() => {
                        setHoraFiltro('');
                        setFechaFiltro(new Date().toISOString().slice(0, 10));
                      }}
                    >
                      Limpiar filtros de tiempo
                    </button>
                  </div>
                )}
              </div>
            </div>

            {/* Filtro de Fecha y Hora */}
            {mostrarDisponibilidad && (
              <>
                <div className="col-md-6">
                  <label htmlFor="fechaFiltro" className="form-label small">
                    Fecha a consultar:
                  </label>
                  <input
                    type="date"
                    id="fechaFiltro"
                    className="form-control"
                    value={fechaFiltro}
                    onChange={(e) => setFechaFiltro(e.target.value)}
                  />
                </div>
                <div className="col-md-6">
                  <label htmlFor="horaFiltro" className="form-label small">
                    Hora (opcional):
                  </label>
                  <input
                    type="time"
                    id="horaFiltro"
                    className="form-control"
                    value={horaFiltro}
                    onChange={(e) => setHoraFiltro(e.target.value)}
                  />
                  <small className="text-muted">
                    Filtra reservas y disponibilidad en una hora específica
                  </small>
                </div>
              </>
            )}
          </div>
        </div>
      </div>

      {/* Estadísticas Rápidas */}
      <div className="row mb-4">
        <div className="col-md-3">
          <div className="card border-success">
            <div className="card-body text-center">
              <h5 className="text-success">{mesas.filter(m => m.estado === 'disponible').length}</h5>
              <small className="text-muted">Disponibles</small>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card border-warning">
            <div className="card-body text-center">
              <h5 className="text-warning">{mesas.filter(m => m.estado === 'reservada').length}</h5>
              <small className="text-muted">Reservadas</small>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card border-danger">
            <div className="card-body text-center">
              <h5 className="text-danger">{mesas.filter(m => m.estado === 'ocupada').length}</h5>
              <small className="text-muted">Ocupadas</small>
            </div>
          </div>
        </div>
        <div className="col-md-3">
          <div className="card border-info">
            <div className="card-body text-center">
              <h5 className="text-info">{mesas.filter(m => m.estado === 'limpieza').length}</h5>
              <small className="text-muted">En Limpieza</small>
            </div>
          </div>
        </div>
      </div>

      {/* Grid de Mesas */}
      {mesasFiltradas.length === 0 ? (
        <div className="alert alert-info">
          <i className="bi bi-info-circle me-2"></i>
          No hay mesas {filtroEstado !== 'TODOS' ? `en estado ${filtroEstado.toLowerCase()}` : ''}.
        </div>
      ) : (
        <div className="row">
          {mesasFiltradas.map(mesa => (
            <div key={mesa.id} className="col-md-6 col-lg-4 col-xl-3 mb-3">
              <div className={`card h-100 shadow-sm border-${getEstadoColor(mesa.estado)}`}>
                <div className={`card-header bg-${getEstadoColor(mesa.estado)} text-white d-flex justify-content-between align-items-center`}>
                  <h5 className="mb-0">
                    <i className={`bi ${getEstadoIcon(mesa.estado)} me-2`}></i>
                    Mesa {mesa.numero}
                  </h5>
                </div>
                <div className="card-body">
                  <div className="mb-2">
                    <i className="bi bi-people me-2 text-primary"></i>
                    <strong>Capacidad:</strong> {mesa.capacidad} personas
                  </div>
                  <div className="mb-3 d-flex align-items-center gap-2 flex-wrap">
                    <span className={`badge bg-${getEstadoColor(mesa.estado)}`}>
                      {mesa.estado.toUpperCase()}
                    </span>
                    {mostrarDisponibilidad && (
                      <span className="badge bg-light text-muted border">
                        <i className="bi bi-calendar3 me-1"></i>
                        {new Date(fechaFiltro + 'T00:00:00').toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })}
                        {horaFiltro && <> · {horaFiltro}</>}
                      </span>
                    )}
                  </div>

                  {/* Mostrar reservas si está activo el modo de disponibilidad */}
                  {mostrarDisponibilidad && (
                    <div className="mb-3 border-top pt-2">
                      {(() => {
                        const reservas = getReservasMesa(mesa.numero);
                        const hayReservaEnHora = horaFiltro
                          ? reservas.some(r => r.hora && r.hora.startsWith(horaFiltro))
                          : reservas.length > 0;
                        return reservas.length > 0 ? (
                          <>
                            <div className="d-flex align-items-center mb-2">
                              <i className="bi bi-calendar-event me-2 text-warning"></i>
                              <strong className="small">
                                Reservas para {new Date(fechaFiltro + 'T00:00:00').toLocaleDateString('es-ES', { day: 'numeric', month: 'short' })}
                                {horaFiltro && ` a las ${horaFiltro}`}
                              </strong>
                            </div>
                            <div className="list-group list-group-flush small">
                              {reservas.map((reserva, idx) => (
                                <div key={idx} className="list-group-item px-0 py-1 border-0">
                                  <i className="bi bi-clock text-muted me-1"></i>
                                  <strong>{reserva.hora}</strong> - {reserva.personas} pers.
                                  <span className={`badge bg-${
                                    reserva.estado === 'ACTIVA' ? 'success' :
                                    reserva.estado === 'PENDIENTE' ? 'warning' :
                                    reserva.estado === 'COMPLETADA' ? 'info' : 'secondary'
                                  } ms-1 small`}>
                                    {reserva.estado}
                                  </span>
                                </div>
                              ))}
                            </div>
                          </>
                        ) : (
                          <div className={`alert ${hayReservaEnHora ? 'alert-warning' : 'alert-success'} py-2 mb-0 small`}>
                            <i className="bi bi-check-circle me-1"></i>
                            {hayReservaEnHora ? 'Reservas fuera de la hora seleccionada' : 'Sin reservas para esta fecha'}
                          </div>
                        );
                      })()}
                    </div>
                  )}

                  {mesaEditando === mesa.id ? (
                    <div>
                      <p className="mb-2"><strong>Cambiar estado a:</strong></p>
                      <div className="d-grid gap-2">
                        <button
                          className="btn btn-sm btn-success"
                          onClick={() => handleCambiarEstado(mesa.id, 'disponible')}
                          disabled={mesa.estado === 'disponible'}
                        >
                          Disponible
                        </button>
                        <button
                          className="btn btn-sm btn-warning"
                          onClick={() => handleCambiarEstado(mesa.id, 'reservada')}
                          disabled={mesa.estado === 'reservada'}
                        >
                          Reservada
                        </button>
                        <button
                          className="btn btn-sm btn-danger"
                          onClick={() => handleCambiarEstado(mesa.id, 'ocupada')}
                          disabled={mesa.estado === 'ocupada'}
                        >
                          Ocupada
                        </button>
                        <button
                          className="btn btn-sm btn-info"
                          onClick={() => handleCambiarEstado(mesa.id, 'limpieza')}
                          disabled={mesa.estado === 'limpieza'}
                        >
                          En Limpieza
                        </button>
                        <button
                          className="btn btn-sm btn-secondary"
                          onClick={() => setMesaEditando(null)}
                        >
                          Cancelar
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="d-grid">
                      <button
                        className="btn btn-primary btn-sm"
                        onClick={() => setMesaEditando(mesa.id)}
                      >
                        <i className="bi bi-pencil me-1"></i>
                        Cambiar Estado
                      </button>
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Leyenda de Estados */}
      <div className="card mt-4">
        <div className="card-body">
          <h6 className="card-title">Leyenda de Estados:</h6>
          <div className="row">
            <div className="col-md-3">
              <span className="badge bg-success me-2">DISPONIBLE</span>
              <small className="text-muted">Mesa lista para uso</small>
            </div>
            <div className="col-md-3">
              <span className="badge bg-warning me-2">RESERVADA</span>
              <small className="text-muted">Mesa con reserva confirmada</small>
            </div>
            <div className="col-md-3">
              <span className="badge bg-danger me-2">OCUPADA</span>
              <small className="text-muted">Mesa ocupada actualmente</small>
            </div>
            <div className="col-md-3">
              <span className="badge bg-info me-2">EN LIMPIEZA</span>
              <small className="text-muted">Mesa siendo limpiada</small>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
