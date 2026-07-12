from rest_framework.response import Response


def success_response(data=None, status_code=200):
    body = {
        'success': True,
        'data': data,
        'error': None,
    }
    return Response(body, status=status_code)


def error_response(message, status_code=400, fields=None):
    body = {
        'success': False,
        'data': None,
        'error': {
            'message': message,
            'fields': fields,
        },
    }
    return Response(body, status=status_code)