
from rest_framework import serializers
from django.contrib.auth import authenticate
from rest_framework.validators import UniqueValidator


from .models import User

class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        # phone_number = attrs['phone_number']    # frondan phone_number ham password attrs ishinde keledi dic bolip
        # password = attrs['password']
        phone_number = attrs.get('phone_number')
        password = attrs.get('password')

        user = authenticate(username=phone_number, password=password)

        if user is None:
            raise serializers.ValidationError('Invalid username or password')
        
        if not user.is_active:
            raise serializers.ValidationError('User account is disabled')
        
        attrs['user'] = user    # bari jaqsi bolsa user degen field qosip View-ge jiberedi

        return attrs



class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = [
            'id',
            'first_name',
            'last_name',
            'phone_number',
            'address',
        ]
        read_only_fields = ['id', 'phone_number']


class CreateUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)   # paroldi qayta zaziw (override) 

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'phone_number',
            'password',
        ]
    
    def validate_phone_number(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("The phone number must contain only numeric characters.")
        if len(value) != 9:
            raise serializers.ValidationError("The phone number must consist of exactly 9 digits.")
        return value

    def create(self, validated_data):
        password = validated_data.pop('password')   # validatsiyadan otken password alindi
        user = User(**validated_data)
        user.set_password(password)     # sir boliwi ushin heshladi
        user.save()     # userdin password fieldin heshlangan password saqlandi
        return user


class UpdateProfileSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, max_length=150)
    last_name = serializers.CharField(required=False, max_length=150)
    phone_number = serializers.CharField(
        required=False,
        max_length=9,
        validators=[
            User.phone_validator,
            UniqueValidator(queryset=User.objects.all()),
        ]
    )
    address = serializers.CharField(required=False, max_length=1024, allow_null=True, allow_blank=True)
    old_password = serializers.CharField(required=False, write_only=True)
    new_password = serializers.CharField(required=False, write_only=True, min_length=8)

    def validate(self, attrs):
        old_password = attrs.get('old_password')
        new_password = attrs.get('new_password')

        if new_password or old_password:
            if not old_password:
                raise serializers.ValidationError({'old_password': 'Old password is required to set a new password.'})
            if not new_password:
                raise serializers.ValidationError({'new_password': 'New password is required.'})
            
            # self.instance - bul viewdan jiberilgen user obyekti
            if not self.instance.check_password(old_password):
                raise serializers.ValidationError({'old_password': 'Old password is incorrect.'})
            
            if old_password == new_password:
                raise serializers.ValidationError({'new_password': 'New password must be different from the old one.'})
        
        return attrs
        
    
    def update(self, instance, validated_data):

        """ instance - bazadagi o'zgertiw kerek bolgan bir obyekt. User - obyekti """
        # if 'first_name' in validated_data:
        #     instance.first_name = validated_data['first_name']

        # if 'last_name' in validated_data:
        #     instance.last_name = validated_data['last_name']

        # if 'phone_number' in validated_data:
        #     instance.phone_number = validated_data['phone_number']
        
        # if 'address' in validated_data:
        #     instance.address = validated_data['address']


        new_password = validated_data.get('new_password', None)
        validated_data.pop('old_password', None)    # pop suwirip aladi, old_password modelde joq sonin ushin tomengi kodlarga kerek emes
        if new_password:
            instance.set_password(new_password)
        
        for attr, value in validated_data.items(): 
            setattr(instance, attr, value)  # old ham new password joq. Sebebi user modelinge onday fieldlar joq.
        
        instance.save()

        return instance
    


