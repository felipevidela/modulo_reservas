"""
Vista temporal de debug para verificar desencriptación.
ELIMINAR DESPUÉS DE RESOLVER EL PROBLEMA.
"""
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from .models import Reserva
from .serializers import ReservaSerializer


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def debug_encryption(request):
    """
    Endpoint temporal para verificar si la desencriptación funciona.
    Acceso: GET /api/debug-encryption/
    """
    try:
        # Obtener primera reserva
        reserva = Reserva.objects.select_related('cliente', 'cliente__perfil').first()

        if not reserva:
            return JsonResponse({'error': 'No hay reservas en la base de datos'}, status=404)

        # Datos directos del modelo
        datos_directos = {
            'cliente_username': reserva.cliente.username,
            'cliente_nombre': reserva.cliente.perfil.nombre_completo if hasattr(reserva.cliente, 'perfil') else None,
            'cliente_telefono_directo': reserva.cliente.perfil.telefono if hasattr(reserva.cliente, 'perfil') else None,
            'cliente_rut_directo': reserva.cliente.perfil.rut if hasattr(reserva.cliente, 'perfil') else None,
            'cliente_email_directo': reserva.cliente.email,
        }

        # Datos serializados
        serializer = ReservaSerializer(reserva, context={'request': request})
        datos_serializados = {
            'cliente_nombre': serializer.data.get('cliente_nombre'),
            'cliente_telefono': serializer.data.get('cliente_telefono'),
            'cliente_rut': serializer.data.get('cliente_rut'),
            'cliente_email': serializer.data.get('cliente_email'),
        }

        # Información del usuario
        info_usuario = {
            'username': request.user.username,
            'es_admin': hasattr(request.user, 'perfil') and request.user.perfil.rol == 'admin',
            'rol': request.user.perfil.rol if hasattr(request.user, 'perfil') else None,
        }

        # Verificación
        telefono_serializado = datos_serializados.get('cliente_telefono')
        verificacion = {
            'telefono_esta_encriptado': telefono_serializado and len(str(telefono_serializado)) > 50,
            'telefono_longitud': len(str(telefono_serializado)) if telefono_serializado else 0,
            'telefono_comienza_con_plus56': str(telefono_serializado).startswith('+56') if telefono_serializado else False,
        }

        return JsonResponse({
            'success': True,
            'reserva_id': reserva.id,
            'datos_directos': datos_directos,
            'datos_serializados': datos_serializados,
            'info_usuario': info_usuario,
            'verificacion': verificacion,
            'mensaje': 'Si telefono_esta_encriptado es True, hay un problema con la desencriptación'
        })

    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'tipo_error': type(e).__name__
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def ejecutar_comandos_management(request):
    """
    Ejecutar comandos de management desde el navegador.
    SOLO PARA ADMIN.
    Acceso: POST /api/ejecutar-comandos/
    """
    # Verificar que sea admin
    if not (hasattr(request.user, 'perfil') and request.user.perfil.rol == 'admin'):
        return JsonResponse({'error': 'Solo administradores pueden ejecutar este comando'}, status=403)

    try:
        from django.core.management import call_command
        import io

        resultados = {}

        # Ejecutar actualizar_nombres_completos
        output = io.StringIO()
        call_command('actualizar_nombres_completos', stdout=output)
        resultados['actualizar_nombres'] = output.getvalue()

        # Ejecutar completar_datos_contacto
        output = io.StringIO()
        call_command('completar_datos_contacto', stdout=output)
        resultados['completar_datos'] = output.getvalue()

        return JsonResponse({
            'success': True,
            'mensaje': 'Comandos ejecutados exitosamente',
            'resultados': resultados
        })

    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'tipo_error': type(e).__name__
        }, status=500)
