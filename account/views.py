from django.contrib.auth import login, logout
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.db import transaction
from django.utils import timezone
from rest_framework import views, response, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, ModelViewSet
from django.db.transaction import atomic
from account.models import Wallet, CategoryWallet, Token, ExitSession
from money.models import MoneyItem, Money
from money.serializers import MoneyItemSerializer
from .authentication import CsrfExemptSessionAuthentication
from .serializers import LoginSerializer, UserSerializer, RegisterationSerializer, WalletSerializer, \
    CategoryWalletSerializer, ResetSerializer, UserSerializerNew, DeleteUserSerializer, WalletExchangeMoneySerializer, \
    ExitSessionSerializer
from .utils import toke_gen_uniqe


class UserDeleteViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = DeleteUserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        serializer = DeleteUserSerializer(data=request.data)
        if serializer.is_valid():
            password = serializer.validated_data['password']
            username = serializer.validated_data['username']
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                return Response({'message': 'user not found'})
            if user.check_password(password) and user.id == self.request.user.id:
                user.delete()
                return Response({'message': 'user deleted'}, status=200)
            return Response({'message': 'password is incorrect'}, status=400)
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
        time_now = timezone.now()
        try:
            exit_session = ExitSession.objects.get(user=user)
        except ExitSession.DoesNotExist:
            return response.Response(data=UserSerializer(user).data, status=200)
        deltatime = int(time_now.timestamp())-int(exit_session.exit_time)
        if deltatime < 5:
            return Response(data=UserSerializer(user).data, status=200)
        logout(request)
        return Response(data={'detail': 'Exit Session'}, status=403)


class RegistrationView(views.APIView):
    permission_classes = (permissions.AllowAny,)

    @transaction.atomic
    def post(self, request):
        serializer = RegisterationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.is_active = False
            user.save()
            token = toke_gen_uniqe()
            send_mail(
                subject='Activation link',
                message=None,
                html_message=f'Activation link: <a href="https://money-management-liart.vercel.app/auth/register/verify/{token}">tap here</a>',
                from_email='moneymanage433@gmail.com',
                recipient_list=[user.username],
                fail_silently=False, )
            token = Token(token=token, user=user)
            token.save()
            return response.Response({'detail': 'Email sent'}, status=201)
        return response.Response(serializer.errors, status=400)

    def get(self, request):
        token = request.GET.get('token')
        if token:
            try:
                token = Token.objects.get(token=token)
            except Token.DoesNotExist:
                return response.Response({'detail': 'Token not found'}, status=404)
            user = token.user
            user.is_active = True
            user.save()
            token.delete()
            return response.Response(data=UserSerializer(user).data, status=200)
        return response.Response({'detail': 'Token not found'}, status=404)


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
                    message=None,
                    html_message=f'Activation link: <a href="https://money-management-liart.vercel.app/auth/verify/{token}">tap here</a>',
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


class WalletExchangeMoneyViewSet(ModelViewSet):
    serializer_class = WalletExchangeMoneySerializer
    permission_classes = (permissions.IsAuthenticated,)

    @atomic
    def create(self, request, *args, **kwargs):
        serializer = WalletExchangeMoneySerializer(data=request.data)
        if serializer.is_valid():
            dict1 = {}
            wallet_from_id = serializer.validated_data['wallet_id_from']
            wallet_to_id = serializer.validated_data['wallet_id_to']
            amount = serializer.validated_data['amount']
            rate = serializer.validated_data['rate']
            wallet_from = Wallet.objects.get(id=wallet_from_id)
            wallet_to = Wallet.objects.get(id=wallet_to_id)

            if wallet_from.currency == wallet_to.currency:
                income_transaction = MoneyItem.objects.create(
                    wallet=wallet_to,
                    amount=amount,
                    description='Exchange money from another wallet',
                    money=Money.objects.create(
                        user=request.user,
                        name='Exchange money from another wallet',
                        is_income=True,
                        target_money=amount,
                        currency=wallet_to.currency,
                        is_deleted=True

                    ))
                outcome_transaction = MoneyItem.objects.create(
                    wallet=wallet_from,
                    amount=amount,
                    description='Exchange money to another wallet',
                    money=Money.objects.create(
                        user=request.user,
                        name='Exchange money to another wallet',
                        is_income=False,
                        target_money=amount,
                        currency=wallet_from.currency,
                        is_deleted=True
                    ))

                serializer_income = MoneyItemSerializer(income_transaction)
                serializer_outcome = MoneyItemSerializer(outcome_transaction)
                serializer_wallet_from = WalletSerializer(wallet_from)
                serializer_wallet_to = WalletSerializer(wallet_to)
                dict1['wallet_from'] = serializer_wallet_from.data
                dict1['wallet_to'] = serializer_wallet_to.data
                dict1['income_transaction'] = serializer_income.data
                dict1['outcome_transaction'] = serializer_outcome.data
                return Response(data=dict1, status=200)

            else:
                if wallet_from.currency == 'USD':
                    income_transaction = MoneyItem.objects.create(
                        wallet=wallet_to,
                        amount=float(amount) * float(rate),
                        description='Exchange money from another wallet',
                        money=Money.objects.create(
                            user=request.user,
                            name='Exchange money from another wallet',
                            is_income=True,
                            target_money=amount,
                            currency=wallet_to.currency,
                            is_deleted=True
                        )
                    )
                    outcome_transaction = MoneyItem.objects.create(
                        wallet=wallet_from,
                        amount=amount,
                        description='Exchange money to another wallet',
                        money=Money.objects.create(
                            user=request.user,
                            name='Exchange money to another wallet',
                            is_income=False,
                            target_money=amount,
                            currency=wallet_from.currency,
                            is_deleted=True
                        )
                    )

                    serializer_income = MoneyItemSerializer(income_transaction)
                    serializer_outcome = MoneyItemSerializer(outcome_transaction)
                    serializer_wallet_from = WalletSerializer(wallet_from)
                    serializer_wallet_to = WalletSerializer(wallet_to)
                    dict1['wallet_from'] = serializer_wallet_from.data
                    dict1['wallet_to'] = serializer_wallet_to.data
                    dict1['income_transaction'] = serializer_income.data
                    dict1['outcome_transaction'] = serializer_outcome.data
                    return Response(data=dict1, status=200)
                elif wallet_from.currency == 'UZS':
                    income_transaction = MoneyItem.objects.create(
                        wallet=wallet_to,
                        amount=float(amount) / float(rate),
                        description='Exchange money from another wallet',
                        money=Money.objects.create(
                            user=request.user,
                            name='Exchange money to another wallet',
                            is_income=True,
                            target_money=amount,
                            currency=wallet_to.currency,
                            is_deleted=True
                        )
                    )
                    outcome_transaction = MoneyItem.objects.create(
                        wallet=wallet_from,
                        amount=amount,
                        description='Exchange money to another wallet',
                        money=Money.objects.create(
                            user=request.user,
                            name='Exchange money to another wallet',
                            is_income=False,
                            target_money=amount,
                            currency=wallet_from.currency,
                            is_deleted=True
                        )
                    )

                    serializer_income = MoneyItemSerializer(income_transaction)
                    serializer_outcome = MoneyItemSerializer(outcome_transaction)
                    serializer_wallet_from = WalletSerializer(wallet_from)
                    serializer_wallet_to = WalletSerializer(wallet_to)
                    dict1['income_transaction'] = serializer_income.data
                    dict1['outcome_transaction'] = serializer_outcome.data
                    dict1['wallet_from'] = serializer_wallet_from.data
                    dict1['wallet_to'] = serializer_wallet_to.data
                    return Response(data=dict1, status=200)

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


class ExitSessionViewSet(ModelViewSet):
    serializer_class = ExitSessionSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        return Response({'detail': 'Method Not Allowed'}, status=405)

    def create(self, request, *args, **kwargs):
        serializer = ExitSessionSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            try:
                user = User.objects.get(id=user)
                print(user)
            except User.DoesNotExist:
                return Response(data={"detail": "not found"})
            exit_time = serializer.validated_data['exit_time']
            if ExitSession.objects.filter(user=user).exists():
                ExitSession.objects.get(user=user)
                ExitSession.objects.filter(user=user).update(exit_time=exit_time)
            else:
                e = ExitSession.objects.create(user=user, exit_time=exit_time)
                serializer = ExitSessionSerializer(e)
                return Response(data=serializer.data, status=200)
        return Response(data=serializer.errors, status=400)

    def list(self, request, *args, **kwargs):
        return Response({'detail': 'Method Not Allowed'}, status=405)

    def partial_update(self, request, *args, **kwargs):
        return Response({'detail': 'Method Not Allowed'}, status=405)

    def destroy(self, request, *args, **kwargs):
        return Response({'detail': 'Method Not Allowed'}, status=405)

    @action(detail=True, methods=['post', 'put', 'patch', 'delete'])
    def custom_action(self, request, pk=None):
        return Response({'detail': 'Method Not Allowed'}, status=405)
