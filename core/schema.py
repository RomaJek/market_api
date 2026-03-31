from drf_spectacular.utils import inline_serializer
from rest_framework import serializers


# Bul narse frontend ushun standart juwap qaytariwga qolay.
def wrapped_response(data_serializer, many=False):
    name = data_serializer.__name__.replace('Serializer', '')   # misali: UserSerializer -> User.  data_serializer ishinen Serializer degen sozdi oshiredi
    return inline_serializer(   # jana dinamik tarizde jana serializer jaratip jiberiw
        name=f'{name}SuccessResponse',  # Misali: UserSuccessResponse
        fields={
            'success': serializers.BooleanField(default=True),
            'data': data_serializer(many=many),     # many=False bolsa tek bir info qaytadi. UserSerializer din o'zi.
            'error': serializers.JSONField(allow_null=True, default=None),
        },
    )


class ErrorDetailSerializer(serializers.Serializer):
    message = serializers.CharField()   # error haqqinda text
    fields = serializers.DictField(     # error aniq qay jerde ekenin dic ko'rinisinde beredi
        child=serializers.CharField(),
        allow_null=True,
        default=None,
    )


class ErrorResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=False)
    data = serializers.JSONField(allow_null=True, default=None)
    error = ErrorDetailSerializer()


class MessageSerializer(serializers.Serializer):
    message = serializers.CharField()


class MessageResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField(default=True)
    data = MessageSerializer()
    error = serializers.JSONField(allow_null=True, default=True)

