from rest_framework.permissions import BasePermission


class IsAdministrador(BasePermission):
    """
    Permite acceso solo a usuarios con rol 'Administrador'.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            return request.user.perfil.rol == 'admin'
        except AttributeError:
            # Si el usuario no tiene perfil, denegar acceso
            return False

    def has_object_permission(self, request, view, obj):
        """Admin tiene acceso a todos los objetos"""
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            return request.user.perfil.rol == 'admin'
        except AttributeError:
            return False


class IsCajero(BasePermission):
    """
    Permite acceso solo a usuarios con rol 'Cajero'.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            return request.user.perfil.rol == 'cajero'
        except AttributeError:
            return False

    def has_object_permission(self, request, view, obj):
        """Cajero tiene acceso a todos los objetos"""
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            return request.user.perfil.rol == 'cajero'
        except AttributeError:
            return False


class IsMesero(BasePermission):
    """
    Permite acceso solo a usuarios con rol 'Mesero'.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            return request.user.perfil.rol == 'mesero'
        except AttributeError:
            return False

    def has_object_permission(self, request, view, obj):
        """Mesero tiene acceso a todos los objetos"""
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            return request.user.perfil.rol == 'mesero'
        except AttributeError:
            return False


class IsCliente(BasePermission):
    """
    Permite acceso solo a usuarios con rol 'Cliente'.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            return request.user.perfil.rol == 'cliente'
        except AttributeError:
            return False

    def has_object_permission(self, request, view, obj):
        """
        Cliente solo puede acceder a sus propios objetos.
        IMPORTANTE: Verifica que el objeto (Reserva) pertenezca al cliente.
        """
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            # Verificar que sea cliente
            if request.user.perfil.rol != 'cliente':
                return False

            # Para objetos Reserva, verificar que sea del cliente
            if hasattr(obj, 'cliente'):
                return obj.cliente == request.user

            # Para objetos Perfil, verificar que sea el suyo
            if hasattr(obj, 'user'):
                return obj.user == request.user

            # Por defecto, denegar acceso
            return False
        except AttributeError:
            return False


class IsAdminOrCajero(BasePermission):
    """
    Permite acceso a usuarios con rol 'Administrador' o 'Cajero'.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            return request.user.perfil.rol in ['admin', 'cajero']
        except AttributeError:
            return False

    def has_object_permission(self, request, view, obj):
        """Admin o Cajero tienen acceso a todos los objetos"""
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            return request.user.perfil.rol in ['admin', 'cajero']
        except AttributeError:
            return False


class IsAdminOrCajeroOrMesero(BasePermission):
    """
    Permite acceso a usuarios con rol 'Administrador', 'Cajero' o 'Mesero'.
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            return request.user.perfil.rol in ['admin', 'cajero', 'mesero']
        except AttributeError:
            return False

    def has_object_permission(self, request, view, obj):
        """Admin, Cajero o Mesero tienen acceso a todos los objetos"""
        if not request.user or not request.user.is_authenticated:
            return False

        try:
            return request.user.perfil.rol in ['admin', 'cajero', 'mesero']
        except AttributeError:
            return False

