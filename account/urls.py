from django.urls import path
from . import views
from money_manage.routers import CustomRouter

router = CustomRouter(root_view_name='account-wallet-root')

router.register(r'wallet', views.WalletViewSet, basename='wallet')
router.register(r'category-wallet', views.CategoryWalletViewSet, basename='category-wallet')
router.register(r'reset-password', views.ResetPasswordViewSet, basename='reset-password')
router.register(r'verify', views.VerifyViewSet, basename='verify')
router.register(r'new-password', views.NewPasswordViewSet, basename='new-password')
router.register(r'delete-account', views.UserDeleteViewSet, basename='delete-account')

urlpatterns = [
                  path('login/', views.LoginView.as_view(), name='login'),
                  path('logout/', views.LogoutView.as_view(), name='user-logout'),
                  path('session/', views.SessionUserView.as_view(), name='session'),
                  path('register/', views.RegistrationView.as_view(), name='register'),
              ] + router.urls
