from django.contrib.auth.models import User
from django.core.mail import send_mail
from rest_framework import views, response, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, ModelViewSet

from .authentication import CsrfExemptSessionAuthentication
from .serializers import LoginSerializer, UserSerializer, RegisterationSerializer, WalletSerializer, \
    CategoryWalletSerializer, ResetSerializer, UserSerializerNew
from django.contrib.auth import login, logout
from account.models import Wallet, CategoryWallet, Token
from .utils import toke_gen_uniqe


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


class ResetPasswordViewSet(ViewSet):
    permission_classes = (permissions.AllowAny,)

    def create(self, request):
        serilizer = ResetSerializer(data=request.data)
        if serilizer.is_valid():
            username = serilizer.validated_data['gmail']
            user = User.objects.get(username=username)
            if user:
                token = toke_gen_uniqe()
                send_mail(
                    subject='Activation link',
                    message=f'Activation link: http://localhost:3000/auth/verify/{token}',
                    from_email='moneymanage433@gmail.com',
                    recipient_list=[username],
                    fail_silently=False
                )
                token = Token(token=token, user=user)
                token.save()
                return Response({'detail': 'Email sent'}, status=200)
            return Response({'detail': 'Email not found'}, status=404)
        return Response(data=serilizer.errors, status=400)


class VerifyViewSet(ViewSet):
    permission_classes = (permissions.AllowAny,)

    def list(self, request):
        token = request.GET.get('token')
        if token:
            try:
                token = Token.objects.get(token=token)
            except Token.DoesNotExist:
                token = None
            if token:
                user = token.user
                token.delete()
                serializer = UserSerializer(user)
                return Response(serializer.data, status=200)
            return Response({'detail': 'Token not found'}, status=404)
        return Response({'detail': 'Token not found'}, status=404)


class NewPasswordViewSet(ModelViewSet):
    permission_classes = (permissions.AllowAny,)
    serializer_class = UserSerializerNew

    def create(self, request, *args, **kwargs):
        serializer = UserSerializerNew(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['username']
            first_name = serializer.validated_data.get('first_name', None)
            last_name = serializer.validated_data.get('last_name', None)
            email = serializer.validated_data.get('email', None)

            try:
                user = User.objects.get(username=username, first_name=first_name, last_name=last_name, email=email)
            except User.DoesNotExist:
                user = None
            if user:
                password = serializer.validated_data['password']
                user.set_password(password)
                user.save()
                return Response(serializer.data, status=200)
            return Response({'detail': 'User not found'}, status=404)
        return Response(serializer.errors, status=400)

    def list(self, request, *args, **kwargs):
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
