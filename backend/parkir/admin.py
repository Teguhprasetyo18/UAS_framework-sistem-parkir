from django.contrib import admin
from .models import JenisKendaraan, Kendaraan, TransaksiParkir

# Register your models here.

@admin.register(JenisKendaraan)
class JenisKendaraanAdmin(admin.ModelAdmin):
    list_display = ('nama', 'tarif_per_jam')

@admin.register(Kendaraan)
class KendaraanAdmin(admin.ModelAdmin):
    list_display = ('nomor_plat', 'merk', 'model', 'jenis', 'pemilik')
    list_filter = ('jenis',)
    search_fields = ('nomor_plat', 'pemilik')

@admin.register(TransaksiParkir)
class TransaksiParkirAdmin(admin.ModelAdmin):
    list_display = ('kendaraan', 'waktu_masuk', 'waktu_keluar', 'status', 'biaya')
    list_filter = ('status', 'waktu_masuk')
    search_fields = ('kendaraan__nomor_plat',)