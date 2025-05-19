from rest_framework import viewsets, mixins, filters
from src.accounts.api.filters import customerFilter
from src.accounts.models import FCMDeviceToken, User
from src.accounts.api.serializers import RegisterDeviceSerializer, RegistrationSerializer, LoginSerializer, UserSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.response import Response
from rest_framework import status


class RegisterViewset(viewsets.GenericViewSet, mixins.CreateModelMixin):
    serializer_class = RegistrationSerializer
    permission_classes = ()
    authentication_classes = ()


class LoginAPIView(TokenObtainPairView):
    permission_classes = ()
    authentication_classes = ()
    serializer_class = LoginSerializer


class TeamViewset(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_employee=True)
    pagination_class = None


class CustomerViewset(viewsets.ModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_customer=True)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = customerFilter

    pagination_class = None

    # def paginate_queryset(self, queryset):
    #     if self.request.query_params.get('no_pagination', '').lower() == 'true':
    #         return None  # Disables pagination
    #     return super().paginate_queryset(queryset)


class RegisterDeviceViewset(viewsets.GenericViewSet):
    """
        Create view for registering FCM Devices     
    """

    serializer_class = RegisterDeviceSerializer

    def create(self, request, **kwargs):
        device_token = request.data.get('token')

        if not device_token :
            return Response(
                {'error': 'Device token is required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # get or Create new device
        FCMDeviceToken.objects.update_or_create(
            device_token=device_token,
            user=request.user,
        )

        return Response({'message': 'Device registered successfully'})
