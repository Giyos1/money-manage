from money_manage.routers import CustomRouter
from django.urls import path
from . import views

router = CustomRouter(root_view_name='money-root')
router.register(r'money', views.MoneyViewSet, basename='money')
router.register(r'money-item', views.MoneyItemViewSet, basename='money-item')
router.register(r'dashboard', views.StatusViewSet, basename='dashboard')
urlpatterns = router.urls
