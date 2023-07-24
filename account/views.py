from django.contrib.auth.models import User
from rest_framework import views, response, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, ModelViewSet

from .authentication import CsrfExemptSessionAuthentication
from .serializers import LoginSerializer, UserSerializer, RegisterationSerializer, WalletSerializer, \
    CategoryWalletSerializer
from django.contrib.auth import login, logout
from account.models import Wallet, CategoryWallet


class LoginView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        login(request, user)
        return response.Response(UserSerializer(user).data)


class LogoutView(views.APIView):
    authentication_classes = [CsrfExemptSessionAuthentication, ]
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        logout(request)
        return response.Response(data={'message': 'logout success'}, status=200)


class SessionUserView(views.APIView):

    def get(self, request):
        user = User.objects.get(pk=self.request.user.id)
        serializer = UserSerializer(user)
        return response.Response(data=serializer.data)


class RegistrationView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = RegisterationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return response.Response(data=serializer.data, status=201)


class WalletViewSet(ModelViewSet):
    queryset = Wallet.objects.filter(active=True)
    serializer_class = WalletSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        return Response({'detail': 'Method Not Allowed'}, status=405)

    @action(detail=True, methods=['delete'])
    def custom_action(self, request, pk=None):
        return Response({'detail': 'Method Not Allowed'}, status=405)


class CategoryWalletViewSet(ModelViewSet):
    queryset = CategoryWallet.objects.all()
    serializer_class = CategoryWalletSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request, *args, **kwargs):
        return Response({'detail': 'Method Not Allowed'}, status=405)

    def update(self, request, *args, **kwargs):
        return Response({'detail': 'Method Not Allowed'}, status=405)

    def partial_update(self, request, *args, **kwargs):
        return Response({'detail': 'Method Not Allowed'}, status=405)

    def destroy(self, request, *args, **kwargs):
        return Response({'detail': 'Method Not Allowed'}, status=405)

    @action(detail=True, methods=['post', 'put', 'patch', 'delete'])
    def custom_action(self, request, pk=None):
        return Response({'detail': 'Method Not Allowed'}, status=405)
