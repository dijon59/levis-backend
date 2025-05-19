from rest_framework import serializers
from src.accounts.enums import Role
from src.accounts.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'name',
            'contact_number',
            'address',
            'role',
            'is_active',
            'is_customer',
            'is_employee',
        )

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        repr['role'] = instance.role.value
        return repr

    def validate(self, data):
        is_customer = data.get('is_customer', False)
        contact_number = data.get('contact_number')

        if not is_customer and contact_number:
            qs = User.objects.filter(contact_number=contact_number)
            if self.instance:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    'contact_number': 'This contact number is already used by another employee.'
                })

        return data


class RegistrationSerializer(UserSerializer):
    def validate_email(self, email):
        """
            Check if email exist and setting it to lower case 
        """
        if User.objects.filter(email__iexact=email.lower()).exists():
            raise serializers.ValidationError('This email address already exists')
        return email

    def create(self, validated_data):
        # create user
        user = User(**validated_data)
        user.save()
        return user


class LoginSerializer(TokenObtainPairSerializer):
    platform = serializers.CharField(required=True)

    def validate(self, attrs):
        # Extract platform information
        platform = attrs.pop('platform', None)

        # Regular token validation
        data = super().validate(attrs)

        # Get the user
        user = self.user

        # Check if user is an employee trying to access web platform
        if platform == 'web' and user.is_employee and not user.is_superuser:
            raise serializers.ValidationError({"detail": "You do not have the permission to perform this action"})

        data['user_id'] = self.user.id
        data['username'] = self.user.name
        # data['phone_number'] = self.user.contact_number
        # data['user_email'] = self.user.email
        data['user'] = UserSerializer(self.user).data

        return data


class RegisterDeviceSerializer(serializers.Serializer):
    token = serializers.CharField()
