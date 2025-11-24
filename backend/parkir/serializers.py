from rest_framework import serializers
from django.contrib.auth.models import User
from .models import JenisKendaraan, Kendaraan, TransaksiParkir

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class JenisKendaraanSerializer(serializers.ModelSerializer):
    class Meta:
        model = JenisKendaraan
        fields = '__all__'

class KendaraanSerializer(serializers.ModelSerializer):
    jenis_nama = serializers.CharField(source='jenis.nama', read_only=True)
    
    class Meta:
        model = Kendaraan
        fields = '__all__'

class TransaksiParkirSerializer(serializers.ModelSerializer):
    kendaraan_detail = KendaraanSerializer(source='kendaraan', read_only=True)
    nomor_plat = serializers.CharField(source='kendaraan.nomor_plat', read_only=True)
    
    class Meta:
        model = TransaksiParkir
        fields = '__all__'