
from rest_framework.views import exception_handler as drf_exception_handler


def custom_exception_handler(exc, context):
    response = drf_exception_handler(exc, context)

    if response is None:
        return None

    status_code = response.status_code
    errors = response.data

    if isinstance(errors, list):    # errors list bolip kelgende isleydi ham nolinshi elementin shigarip beredi
        first_error = str(errors[0]) if errors else 'An error occurred.'
        response.data = {
            'success': False,
            'data': None,
            'error': {
                'message': first_error,
                'fields': None,
            },
        }
        return response

    if not isinstance(errors, dict):    # dick emes listta emes. Misali: (string, int .. ) belgisiz formatta bolip qalsa qulap qalmay juwap qaytar
        response.data = {
            'success': False,
            'data': None,
            'error': {
                'message': str(errors),     # ne bolsada string qilip jiberedi
                'fields': None,
            },
        }
        return response

        # eger errors bul jerge deyin jetip kelse demes aniq dic
    if 'detail' in errors:      # dic kelgende ham ishinde standart 'detail' degen field ishinen xabardi oqip aladi
        """
        misali: Avtorizatpadan o'tpedi, Permission joq degen 
        standart error messagelar ushin 
        """
        response.data = {
            'success': False,
            'data': None,
            'error': {
                'message': str(errors['detail']),
                'fields': None,
            },
        }
        return response

    message = 'Validation error.'   # qaytiwi kerek bolgan standart xabar ozim jaratqan. Eger tomendegiler orinlanbasa

        # eger errors bul jerge deyin jetip kelse demes aniq dic
    if 'non_field_errors' in errors:
        """
            DRF ozine baylanispagan fieldlardi 'non_field_errors' degen key menen qaytaradi
            Misali: login yamasa parol qate bolgan waqitta
        """
        non_field_errors = errors.pop('non_field_errors')
        if isinstance(non_field_errors, list) and non_field_errors:
            """ non_field_errors bar bolsa ham list bolsa = True """
            message = str(non_field_errors[0])
        else:
            message = str(non_field_errors)

    fields = {}
    for field_name, field_errors in errors.items():
        """ errors degen dic ishindegi key=field_name, value=field_errors (list) bolip alinip atir """
        if isinstance(field_errors, list) and field_errors:
            fields[field_name] = str(field_errors[0])
        else:
            fields[field_name] = str(field_errors)

    response.data = {
        'success': False,
        'data': None,
        'error': {
            'message': message,
            'fields': fields if fields else None,   # fields joq bolsa None boladi
        },
    }
    return response
