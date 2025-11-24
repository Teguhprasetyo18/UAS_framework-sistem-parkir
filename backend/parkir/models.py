from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class JenisKendaraan(models.Model):
    nama = models.CharField(max_length=50)
    tarif_per_jam = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.nama

class Kendaraan(models.Model):
    nomor_plat = models.CharField(max_length=15, unique=True)
    merk = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    jenis = models.ForeignKey(JenisKendaraan, on_delete=models.CASCADE)
    pemilik = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.nomor_plat} - {self.merk} {self.model}"

class TransaksiParkir(models.Model):
    STATUS_CHOICES = [
        ('masuk', 'Masuk'),
        ('keluar', 'Keluar'),
    ]
    
    kendaraan = models.ForeignKey(Kendaraan, on_delete=models.CASCADE)
    waktu_masuk = models.DateTimeField(auto_now_add=True)
    waktu_keluar = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='masuk')
    biaya = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    def __str__(self):
        return f"{self.kendaraan.nomor_plat} - {self.status}"
    
    def hitung_biaya(self):
        if self.waktu_keluar and self.status == 'keluar':
            durasi = self.waktu_keluar - self.waktu_masuk
            jam = durasi.total_seconds() / 3600
            return round(float(self.kendaraan.jenis.tarif_per_jam) * jam, 2)
        return 0