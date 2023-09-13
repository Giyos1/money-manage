from money_manage.routers import CustomRouter
from django.urls import path
from . import views

router = CustomRouter(root_view_name='money-root')
router.register(r'money', views.MoneyViewSet, basename='money')
router.register(r'money-item', views.MoneyItemViewSet, basename='money-item')
router.register(r'dashboard', views.StatusViewSet, basename='dashboard')
router.register(r'auto-pay', views.AutoPayViewSet, basename='auto-pay')
router.register(r'update-order', views.MoneyOrderUpdateViewSet, basename='update-order')
router.register(r'debt', views.DebtViewSet, basename='debt')
urlpatterns = router.urls
