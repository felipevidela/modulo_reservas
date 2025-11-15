import { useState, useEffect, useCallback } from 'react';
import { getReservas, updateEstadoReserva } from '../services/reservasApi';
import { ConfirmModal } from './ui/Modal';
import { useToast } from '../contexts/ToastContext';
import { formatErrorMessage } from '../utils/errorMessages';
import { ReservaSkeleton } from './ui/Skeleton';

export default function MisReservas() {
  const toast = useToast();
  const [reservas, setReservas] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filtroEstado, setFiltroEstado] = useState('TODOS');
  const [cancelModal, setCancelModal] = useState({ isOpen: false, reservaId: null, isLoading: false });

  const cargarReservas = useCallback(async () => {
    try {
      setLoading(true);
      const data = await getReservas({
        estado: filtroEstado !== 'TODOS' ? filtroEstado : undefined
      });
      setReservas(data);
      setError('');
    } catch (err) {
      setError('Error al cargar reservas');
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [filtroEstado]);

  useEffect(() => {
    cargarReservas();
    // Auto-actualizar cada 30 segundos
    const interval = setInterval(cargarReservas, 30000);
    return () => clearInterval(interval);
  }, [cargarReservas]);

  const handleCancelarReserva = (reservaId) => {
    setCancelModal({ isOpen: true, reservaId, isLoading: false });
  };

  const confirmCancelarReserva = async () => {
    try {
      setCancelModal(prev => ({ ...prev, isLoading: true }));
      await updateEstadoReserva({ id: cancelModal.reservaId, nuevoEstado: 'cancelada' });
      await cargarReservas();
      toast.success('Reserva cancelada exitosamente');
      setCancelModal({ isOpen: false, reservaId: null, isLoading: false });
    } catch (err) {
      const errorMsg = formatErrorMessage(err);
      toast.error(errorMsg);
      setCancelModal(prev => ({ ...prev, isLoading: false }));
    }
  };

  const estadoTag = (estado) => {
    const base = (estado || '').toLowerCase();
    return `estado-chip estado-chip--${base}`;
  };
  const estadoIconos = {
    PENDIENTE: 'bi-clock-history',
    ACTIVA: 'bi-lightning-charge-fill',
    COMPLETADA: 'bi-check2-circle',
    CANCELADA: 'bi-x-octagon-fill'
  };

  const formatearFecha = (fecha) => {
    const [year, month, day] = fecha.split('-');
    return `${day}/${month}/${year}`;
  };

  const formatearHora = (hora) => {
    // Asegurar formato 24 horas HH:MM (quitar segundos si los hay)
    if (!hora) return '';
    return hora.substring(0, 5);
  };

  if (loading && reservas.length === 0) {
    return (
      <div className="container-fluid">
        <div className="d-flex justify-content-between align-items-center mb-4">
          <h2 className="mb-0">Mis Reservas</h2>
        </div>
        <div className="mb-4">
          <div className="btn-group" role="group">
            {['TODOS', 'PENDIENTE', 'ACTIVA', 'COMPLETADA', 'CANCELADA'].map(estado => (
              <button
                key={estado}
                type="button"
                className="btn btn-outline-primary"
                disabled
              >
                {estado}
              </button>
            ))}
          </div>
        </div>
        <div className="row">
          {[1, 2, 3].map(i => (
            <ReservaSkeleton key={i} />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="container-fluid">
      <div className="d-flex justify-content-between align-items-center mb-4">
        <h2 className="mb-0">Mis Reservas</h2>
        <button
          className="btn btn-outline-primary btn-sm"
          onClick={cargarReservas}
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

      {/* Filtros */}
      <div className="mb-4">
        <div className="btn-group" role="group">
          {['TODOS', 'PENDIENTE', 'ACTIVA', 'COMPLETADA', 'CANCELADA'].map(estado => (
            <button
              key={estado}
              type="button"
              className={`btn ${filtroEstado === estado ? 'btn-primary' : 'btn-outline-primary'}`}
              onClick={() => setFiltroEstado(estado)}
            >
              {estado}
            </button>
          ))}
        </div>
      </div>

      {/* Lista de Reservas */}
      {reservas.length === 0 ? (
        <div className="alert alert-info">
          <i className="bi bi-info-circle me-2"></i>
          No tiene reservas {filtroEstado !== 'TODOS' ? `en estado ${filtroEstado.toLowerCase()}` : ''}.
        </div>
      ) : (
        <div className="row">
          {reservas.map(reserva => (
            <div key={reserva.id} className="col-md-6 col-lg-4 mb-3">
              <div className="card h-100 shadow-sm reserva-card">
                <div className="card-body d-flex flex-column h-100">
                  <div className="d-flex justify-content-between align-items-start mb-3">
                    <div>
                      <p className="text-muted small mb-1">Mesa</p>
                      <h5 className="mb-0">{reserva.mesa}</h5>
                    </div>
                    <span className={estadoTag(reserva.estado)}>
                      <i className={`bi ${estadoIconos[reserva.estado] || 'bi-info-circle'} me-2`}></i>
                      {reserva.estado}
                    </span>
                  </div>

                  <div className="reserva-card__timeline">
                    <div className="reserva-card__timeline-icon">
                      <i className="bi bi-calendar3"></i>
                    </div>
                    <div>
                      <p className="mb-0 fw-semibold">{formatearFecha(reserva.fecha)}</p>
                      <small className="text-muted">Fecha reservada</small>
                    </div>
                  </div>

                  <div className="reserva-card__timeline">
                    <div className="reserva-card__timeline-icon text-primary">
                      <i className="bi bi-clock-history"></i>
                    </div>
                    <div>
                      <p className="mb-0 fw-semibold">{formatearHora(reserva.hora)} hrs</p>
                      <small className="text-muted">Horario estimado</small>
                    </div>
                  </div>

                  <div className="d-flex align-items-center gap-2 mt-3">
                    <span className="badge rounded-pill badge-soft-primary">
                      <i className="bi bi-people-fill me-1"></i>
                      {reserva.personas} {reserva.personas === 1 ? 'persona' : 'personas'}
                    </span>
                    <span className="badge rounded-pill bg-light text-muted">
                      ID #{reserva.id}
                    </span>
                  </div>

                  {reserva.estado === 'PENDIENTE' ? (
                    <div className="mt-auto pt-3">
                      <button
                        className="btn btn-soft-danger w-100"
                        onClick={() => handleCancelarReserva(reserva.id)}
                      >
                        <i className="bi bi-x-circle me-2"></i>
                        Cancelar Reserva
                      </button>
                    </div>
                  ) : (
                    <div className="mt-auto pt-3 text-muted small">
                      Última actualización: {formatearFecha(reserva.fecha)}
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
          <div className="d-flex flex-wrap gap-3">
            <div>
              <span className="badge bg-warning me-2">PENDIENTE</span>
              <small>Reserva confirmada, esperando llegada</small>
            </div>
            <div>
              <span className="badge bg-success me-2">ACTIVA</span>
              <small>Mesa ocupada actualmente</small>
            </div>
            <div>
              <span className="badge bg-secondary me-2">COMPLETADA</span>
              <small>Reserva finalizada</small>
            </div>
            <div>
              <span className="badge bg-danger me-2">CANCELADA</span>
              <small>Reserva cancelada</small>
            </div>
          </div>
        </div>
      </div>

      {/* Modal de confirmación para cancelar reserva */}
      <ConfirmModal
        isOpen={cancelModal.isOpen}
        onClose={() => setCancelModal({ isOpen: false, reservaId: null, isLoading: false })}
        onConfirm={confirmCancelarReserva}
        title="Cancelar Reserva"
        message="¿Está seguro que desea cancelar esta reserva? Esta acción no se puede deshacer."
        confirmText="Sí, cancelar"
        cancelText="No, mantener"
        confirmVariant="danger"
        isLoading={cancelModal.isLoading}
      />
    </div>
  );
}
