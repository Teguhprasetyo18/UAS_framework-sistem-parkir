from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import datetime, timedelta
from .models import JenisKendaraan, Kendaraan, TransaksiParkir
from .serializers import (JenisKendaraanSerializer, KendaraanSerializer, 
                         TransaksiParkirSerializer, UserSerializer)
from django.contrib.auth import authenticate, login as auth_login
from django.shortcuts import render, redirect

# ... kode sebelumnya ...

from rest_framework.response import Response
from .models import TransaksiParkir
from django.utils import timezone

class ParkingView(APIView):

    def get(self, request):
        data = TransaksiParkir.objects.filter(exit_time=None)
        serializer = TransaksiParkirSerializer(data, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TransaksiParkirSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


class ExitParking(APIView):
    def post(self, request, id):
        try:
            parking = TransaksiParkir.objects.get(id=id)
        except TransaksiParkir.DoesNotExist:
            return Response({"error": "Data tidak ditemukan"}, status=404)

        parking.exit_time = timezone.now()

        # Hitung Biaya Parkir (contoh: Rp2000/Jam)
        hours = (parking.exit_time - parking.entry_time).total_seconds() / 3600
        parking.payment = int(hours * 2000)
        parking.save()

        return Response({"message": "Kendaraan Keluar", "payment": parking.payment})
def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user:
            auth_login(request, user)
            return redirect('/')
        else:
            return render(request, "login.html", {"error": "Login gagal"})
    
    return render(request, "login.html")
class JenisKendaraanViewSet(viewsets.ModelViewSet):
    queryset = JenisKendaraan.objects.all()
    serializer_class = JenisKendaraanSerializer

    @action(detail=False, methods=['get'])
    def stats(self, request):
        total_jenis = JenisKendaraan.objects.count()
        jenis_with_kendaraan = JenisKendaraan.objects.annotate(
            total_kendaraan=Count('kendaraan')
        )
        
        stats_data = {
            'total_jenis': total_jenis,
            'jenis_kendaraan': JenisKendaraanSerializer(jenis_with_kendaraan, many=True).data
        }
        return Response(stats_data)

class KendaraanViewSet(viewsets.ModelViewSet):
    queryset = Kendaraan.objects.all()
    serializer_class = KendaraanSerializer
    
    def get_queryset(self):
        queryset = Kendaraan.objects.all()
        nomor_plat = self.request.query_params.get('nomor_plat', None)
        if nomor_plat:
            queryset = queryset.filter(nomor_plat__icontains=nomor_plat)
        return queryset

    @action(detail=False, methods=['get'])
    def search(self, request):
        query = request.query_params.get('q', '')
        kendaraan = Kendaraan.objects.filter(
            Q(nomor_plat__icontains=query) |
            Q(merk__icontains=query) |
            Q(model__icontains=query) |
            Q(pemilik__icontains=query)
        )
        serializer = self.get_serializer(kendaraan, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        total_kendaraan = Kendaraan.objects.count()
        kendaraan_per_jenis = Kendaraan.objects.values(
            'jenis__nama'
        ).annotate(
            total=Count('id')
        )
        
        stats_data = {
            'total_kendaraan': total_kendaraan,
            'kendaraan_per_jenis': list(kendaraan_per_jenis)
        }
        return Response(stats_data)

class TransaksiParkirViewSet(viewsets.ModelViewSet):
    queryset = TransaksiParkir.objects.all()
    serializer_class = TransaksiParkirSerializer
    
    @action(detail=True, methods=['post'])
    def keluar(self, request, pk=None):
        transaksi = self.get_object()
        if transaksi.status == 'keluar':
            return Response(
                {'error': 'Kendaraan sudah keluar'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        transaksi.waktu_keluar = timezone.now()
        transaksi.status = 'keluar'
        transaksi.biaya = transaksi.hitung_biaya()
        transaksi.save()
        
        serializer = self.get_serializer(transaksi)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def masuk(self, request):
        nomor_plat = request.data.get('nomor_plat')
        
        try:
            kendaraan = Kendaraan.objects.get(nomor_plat=nomor_plat)
            
            # Cek apakah kendaraan masih parkir
            transaksi_aktif = TransaksiParkir.objects.filter(
                kendaraan=kendaraan,
                status='masuk'
            ).exists()
            
            if transaksi_aktif:
                return Response(
                    {'error': 'Kendaraan masih dalam area parkir'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            transaksi = TransaksiParkir.objects.create(
                kendaraan=kendaraan,
                status='masuk'
            )
            
            serializer = self.get_serializer(transaksi)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
            
        except Kendaraan.DoesNotExist:
            return Response(
                {'error': 'Kendaraan tidak ditemukan'},
                status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=False, methods=['get'])
    def aktif(self, request):
        transaksi_aktif = TransaksiParkir.objects.filter(status='masuk')
        serializer = self.get_serializer(transaksi_aktif, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def hari_ini(self, request):
        hari_ini = timezone.now().date()
        transaksi_hari_ini = TransaksiParkir.objects.filter(
            waktu_masuk__date=hari_ini
        )
        serializer = self.get_serializer(transaksi_hari_ini, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        # Stats harian
        hari_ini = timezone.now().date()
        transaksi_hari_ini = TransaksiParkir.objects.filter(
            waktu_masuk__date=hari_ini
        )
        
        # Stats mingguan
        seminggu_lalu = hari_ini - timedelta(days=7)
        transaksi_mingguan = TransaksiParkir.objects.filter(
            waktu_masuk__date__gte=seminggu_lalu
        )
        
        # Stats bulanan
        bulan_ini = hari_ini.replace(day=1)
        transaksi_bulanan = TransaksiParkir.objects.filter(
            waktu_masuk__date__gte=bulan_ini
        )
        
        stats_data = {
            'harian': {
                'total': transaksi_hari_ini.count(),
                'masuk': transaksi_hari_ini.filter(status='masuk').count(),
                'keluar': transaksi_hari_ini.filter(status='keluar').count(),
                'pendapatan': transaksi_hari_ini.aggregate(
                    total=Sum('biaya')
                )['total'] or 0
            },
            'mingguan': {
                'total': transaksi_mingguan.count(),
                'pendapatan': transaksi_mingguan.aggregate(
                    total=Sum('biaya')
                )['total'] or 0
            },
            'bulanan': {
                'total': transaksi_bulanan.count(),
                'pendapatan': transaksi_bulanan.aggregate(
                    total=Sum('biaya')
                )['total'] or 0
            }
        }
        
        return Response(stats_data)

    @action(detail=False, methods=['get'])
    def laporan(self, request):
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        queryset = TransaksiParkir.objects.all()
        
        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            queryset = queryset.filter(waktu_masuk__date__gte=start_date)
            
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
            queryset = queryset.filter(waktu_masuk__date__lte=end_date)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def get_queryset(self):
        queryset = TransaksiParkir.objects.all()
        status = self.request.query_params.get('status', None)
        if status:
            queryset = queryset.filter(status=status)
        return queryset

# API Dashboard
@api_view(['GET'])
def dashboard_stats(request):
    # Total kendaraan
    total_kendaraan = Kendaraan.objects.count()
    
    # Kendaraan parkir aktif
    kendaraan_aktif = TransaksiParkir.objects.filter(status='masuk').count()
    
    # Pendapatan hari ini
    hari_ini = timezone.now().date()
    pendapatan_hari_ini = TransaksiParkir.objects.filter(
        waktu_masuk__date=hari_ini,
        status='keluar'
    ).aggregate(total=Sum('biaya'))['total'] or 0
    
    # Transaksi hari ini
    transaksi_hari_ini = TransaksiParkir.objects.filter(
        waktu_masuk__date=hari_ini
    ).count()
    
    # Jenis kendaraan stats
    jenis_stats = JenisKendaraan.objects.annotate(
        total_kendaraan=Count('kendaraan'),
        sedang_parkir=Count('kendaraan__transaksiparkir', 
                          filter=Q(kendaraan__transaksiparkir__status='masuk'))
    )
    
    stats_data = {
        'total_kendaraan': total_kendaraan,
        'kendaraan_aktif': kendaraan_aktif,
        'pendapatan_hari_ini': float(pendapatan_hari_ini),
        'transaksi_hari_ini': transaksi_hari_ini,
        'jenis_kendaraan': [
            {
                'nama': jenis.nama,
                'total_kendaraan': jenis.total_kendaraan,
                'sedang_parkir': jenis.sedang_parkir,
                'tarif': float(jenis.tarif_per_jam)
            }
            for jenis in jenis_stats
        ]
    }
    
    return Response(stats_data)

# API untuk check kendaraan
@api_view(['POST'])
@permission_classes([AllowAny])
def check_kendaraan(request):
    nomor_plat = request.data.get('nomor_plat')
    
    if not nomor_plat:
        return Response(
            {'error': 'Nomor plat diperlukan'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        kendaraan = Kendaraan.objects.get(nomor_plat=nomor_plat)
        transaksi_aktif = TransaksiParkir.objects.filter(
            kendaraan=kendaraan,
            status='masuk'
        ).first()
        
        response_data = {
            'kendaraan': KendaraanSerializer(kendaraan).data,
            'sedang_parkir': transaksi_aktif is not None,
            'transaksi_aktif': TransaksiParkirSerializer(transaksi_aktif).data if transaksi_aktif else None
        }
        
        return Response(response_data)
        
    except Kendaraan.DoesNotExist:
        return Response(
            {'error': 'Kendaraan tidak ditemukan'}, 
            status=status.HTTP_404_NOT_FOUND
        )

# API untuk quick parkir
@api_view(['POST'])
def quick_parkir(request):
    nomor_plat = request.data.get('nomor_plat')
    merk = request.data.get('merk')
    model = request.data.get('model')
    jenis_id = request.data.get('jenis_id')
    pemilik = request.data.get('pemilik', 'Tidak Diketahui')
    
    try:
        # Cek apakah kendaraan sudah ada
        kendaraan, created = Kendaraan.objects.get_or_create(
            nomor_plat=nomor_plat,
            defaults={
                'merk': merk,
                'model': model,
                'jenis_id': jenis_id,
                'pemilik': pemilik
            }
        )
        
        # Buat transaksi parkir
        transaksi = TransaksiParkir.objects.create(
            kendaraan=kendaraan,
            status='masuk'
        )
        
        response_data = {
            'kendaraan': KendaraanSerializer(kendaraan).data,
            'transaksi': TransaksiParkirSerializer(transaksi).data,
            'kendaraan_baru': created
        }
        
        return Response(response_data, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_400_BAD_REQUEST
        )