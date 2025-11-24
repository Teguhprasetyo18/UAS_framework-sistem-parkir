from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'jenis-kendaraan', views.JenisKendaraanViewSet)
router.register(r'kendaraan', views.KendaraanViewSet)
router.register(r'transaksi-parkir', views.TransaksiParkirViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login/', views.login, name='login'),
    #path('auth/register/', views.register, name='register'),
    path('dashboard/stats/', views.dashboard_stats, name='dashboard-stats'),
    path('check-kendaraan/', views.check_kendaraan, name='check-kendaraan'),
    path('quick-parkir/', views.quick_parkir, name='quick-parkir'),
]