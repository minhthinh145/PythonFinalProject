# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class ChiTietHocPhi(models.Model):
    id = models.UUIDField(primary_key=True)
    hoc_phi = models.ForeignKey('HocPhi', models.DO_NOTHING)
    lop_hoc_phan = models.ForeignKey('LopHocPhan', models.DO_NOTHING)
    so_tin_chi = models.IntegerField()
    phi_tin_chi = models.DecimalField(max_digits=10, decimal_places=2)
    thanh_tien = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'chi_tiet_hoc_phi'
        unique_together = (('hoc_phi', 'lop_hoc_phan'),)


class ChiTietLichSuDangKy(models.Model):
    id = models.UUIDField(primary_key=True)
    lich_su_dang_ky = models.ForeignKey('LichSuDangKy', models.DO_NOTHING)
    dang_ky_hoc_phan = models.ForeignKey('DangKyHocPhan', models.DO_NOTHING)
    hanh_dong = models.CharField(max_length=20)
    thoi_gian = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'chi_tiet_lich_su_dang_ky'


class ChinhSachTinChi(models.Model):
    id = models.UUIDField(primary_key=True)
    hoc_ky = models.ForeignKey('HocKy', models.DO_NOTHING, blank=True, null=True)
    khoa = models.ForeignKey('Khoa', models.DO_NOTHING, blank=True, null=True)
    nganh = models.ForeignKey('NganhHoc', models.DO_NOTHING, blank=True, null=True)
    phi_moi_tin_chi = models.DecimalField(max_digits=12, decimal_places=2)
    ngay_hieu_luc = models.DateField()
    ngay_het_hieu_luc = models.DateField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'chinh_sach_tin_chi'


class CoSo(models.Model):
    id = models.UUIDField(primary_key=True)
    ten_co_so = models.TextField()
    dia_chi = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'co_so'


class DangKyHocPhan(models.Model):
    id = models.UUIDField(primary_key=True)
    sinh_vien = models.ForeignKey('SinhVien', models.DO_NOTHING)
    lop_hoc_phan = models.ForeignKey('LopHocPhan', models.DO_NOTHING)
    ngay_dang_ky = models.DateTimeField(blank=True, null=True)
    trang_thai = models.CharField(max_length=20, blank=True, null=True)
    co_xung_dot = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dang_ky_hoc_phan'
        unique_together = (('sinh_vien', 'lop_hoc_phan'),)


class DangKyTkb(models.Model):
    id = models.UUIDField(primary_key=True)
    dang_ky = models.ForeignKey(DangKyHocPhan, models.DO_NOTHING)
    sinh_vien = models.ForeignKey('SinhVien', models.DO_NOTHING)
    lop_hoc_phan = models.ForeignKey('LopHocPhan', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'dang_ky_tkb'


class DeXuatHocPhan(models.Model):
    id = models.UUIDField(primary_key=True)
    khoa = models.ForeignKey('Khoa', models.DO_NOTHING)
    nguoi_tao = models.ForeignKey('Users', models.DO_NOTHING)
    hoc_ky = models.ForeignKey('HocKy', models.DO_NOTHING)
    mon_hoc = models.ForeignKey('MonHoc', models.DO_NOTHING)
    so_lop_du_kien = models.IntegerField()
    giang_vien_de_xuat = models.ForeignKey('GiangVien', models.DO_NOTHING, db_column='giang_vien_de_xuat', blank=True, null=True)
    trang_thai = models.CharField(max_length=30, blank=True, null=True)
    cap_duyet_hien_tai = models.CharField(max_length=20, blank=True, null=True)
    ghi_chu = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'de_xuat_hoc_phan'


class DeXuatHocPhanGv(models.Model):
    id = models.UUIDField(primary_key=True)
    de_xuat = models.ForeignKey(DeXuatHocPhan, models.DO_NOTHING)
    giang_vien = models.ForeignKey('GiangVien', models.DO_NOTHING, blank=True, null=True)
    so_lop_du_kien = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'de_xuat_hoc_phan_gv'


class DeXuatHocPhanLog(models.Model):
    id = models.UUIDField(primary_key=True)
    de_xuat = models.ForeignKey(DeXuatHocPhan, models.DO_NOTHING)
    thoi_gian = models.DateTimeField(blank=True, null=True)
    hanh_dong = models.CharField(max_length=30)
    nguoi_thuc_hien = models.ForeignKey('Users', models.DO_NOTHING, db_column='nguoi_thuc_hien', blank=True, null=True)
    ghi_chu = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'de_xuat_hoc_phan_log'


class DotDangKy(models.Model):
    id = models.UUIDField(primary_key=True)
    hoc_ky = models.ForeignKey('HocKy', models.DO_NOTHING)
    loai_dot = models.CharField(max_length=20)
    gioi_han_tin_chi = models.IntegerField(blank=True, null=True)
    thoi_gian_bat_dau = models.DateTimeField()
    thoi_gian_ket_thuc = models.DateTimeField()
    han_huy_den = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    is_check_toan_truong = models.BooleanField()
    khoa = models.ForeignKey('Khoa', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'dot_dang_ky'


class GhiDanhHocPhan(models.Model):
    id = models.UUIDField(primary_key=True)
    sinh_vien = models.ForeignKey('SinhVien', models.DO_NOTHING)
    hoc_phan = models.ForeignKey('HocPhan', models.DO_NOTHING)
    ngay_ghi_danh = models.DateTimeField(blank=True, null=True)
    trang_thai = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ghi_danh_hoc_phan'
        unique_together = (('sinh_vien', 'hoc_phan'),)


class GiangVien(models.Model):
    id = models.OneToOneField('Users', models.DO_NOTHING, db_column='id', primary_key=True)
    khoa = models.ForeignKey('Khoa', models.DO_NOTHING)
    chuyen_mon = models.TextField(blank=True, null=True)
    trinh_do = models.CharField(max_length=50, blank=True, null=True)
    kinh_nghiem_giang_day = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'giang_vien'


class HocKy(models.Model):
    id = models.UUIDField(primary_key=True)
    ten_hoc_ky = models.CharField(max_length=50)
    ma_hoc_ky = models.CharField(max_length=10)
    id_nien_khoa = models.ForeignKey('NienKhoa', models.DO_NOTHING, db_column='id_nien_khoa')
    ngay_bat_dau = models.DateField(blank=True, null=True)
    ngay_ket_thuc = models.DateField(blank=True, null=True)
    trang_thai_hien_tai = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hoc_ky'
        unique_together = (('ma_hoc_ky', 'id_nien_khoa'),)


class HocPhan(models.Model):
    id = models.UUIDField(primary_key=True)
    mon_hoc = models.ForeignKey('MonHoc', models.DO_NOTHING)
    ten_hoc_phan = models.CharField(max_length=255)
    so_lop = models.IntegerField(blank=True, null=True)
    trang_thai_mo = models.BooleanField(blank=True, null=True)
    id_hoc_ky = models.ForeignKey(HocKy, models.DO_NOTHING, db_column='id_hoc_ky')
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hoc_phan'


class HocPhi(models.Model):
    id = models.UUIDField(primary_key=True)
    sinh_vien = models.ForeignKey('SinhVien', models.DO_NOTHING)
    hoc_ky = models.ForeignKey(HocKy, models.DO_NOTHING)
    tong_hoc_phi = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    trang_thai_thanh_toan = models.CharField(max_length=20, blank=True, null=True)
    ngay_tinh_toan = models.DateTimeField(blank=True, null=True)
    ngay_thanh_toan = models.DateTimeField(blank=True, null=True)
    chinh_sach = models.ForeignKey(ChinhSachTinChi, models.DO_NOTHING, blank=True, null=True)
    ghi_chu = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'hoc_phi'
        unique_together = (('sinh_vien', 'hoc_ky'),)


class KetQuaHocPhan(models.Model):
    id = models.UUIDField(primary_key=True)
    sinh_vien = models.ForeignKey('SinhVien', models.DO_NOTHING)
    mon_hoc = models.ForeignKey('MonHoc', models.DO_NOTHING)
    hoc_ky = models.ForeignKey(HocKy, models.DO_NOTHING, blank=True, null=True)
    lop_hoc_phan = models.ForeignKey('LopHocPhan', models.DO_NOTHING, blank=True, null=True)
    diem_so = models.DecimalField(max_digits=4, decimal_places=2, blank=True, null=True)
    trang_thai = models.CharField(max_length=20, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ket_qua_hoc_phan'
        unique_together = (('sinh_vien', 'mon_hoc', 'hoc_ky'),)


class Khoa(models.Model):
    id = models.UUIDField(primary_key=True)
    ma_khoa = models.CharField(unique=True, max_length=10)
    ten_khoa = models.CharField(max_length=255)
    ngay_thanh_lap = models.DateField(blank=True, null=True)
    trang_thai_hoat_dong = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'khoa'


class KyPhase(models.Model):
    id = models.UUIDField(primary_key=True)
    hoc_ky = models.ForeignKey(HocKy, models.DO_NOTHING)
    phase = models.CharField(max_length=30)
    start_at = models.DateTimeField()
    end_at = models.DateTimeField()
    is_enabled = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'ky_phase'
        unique_together = (('hoc_ky', 'phase'),)


class LichDayLopHocPhan(models.Model):
    id = models.UUIDField(primary_key=True)
    lop_hoc_phan = models.ForeignKey('LopHocPhan', models.DO_NOTHING)
    ngay_hoc = models.DateField()
    thu = models.IntegerField(blank=True, null=True)
    tiet_bat_dau = models.IntegerField(blank=True, null=True)
    tiet_ket_thuc = models.IntegerField(blank=True, null=True)
    phong = models.ForeignKey('Phong', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lich_day_lop_hoc_phan'
        unique_together = (('lop_hoc_phan', 'ngay_hoc'),)


class LichHocDinhKy(models.Model):
    id = models.UUIDField(primary_key=True)
    lop_hoc_phan = models.ForeignKey('LopHocPhan', models.DO_NOTHING)
    thu = models.IntegerField()
    tiet_bat_dau = models.IntegerField()
    tiet_ket_thuc = models.IntegerField()
    phong = models.ForeignKey('Phong', models.DO_NOTHING, blank=True, null=True)
    tuan_bat_dau = models.IntegerField(blank=True, null=True)
    tuan_ket_thuc = models.IntegerField(blank=True, null=True)
    gio_bat_dau = models.TimeField(blank=True, null=True)
    gio_ket_thuc = models.TimeField(blank=True, null=True)
    # tiet_range is a PostgreSQL GENERATED column - DO NOT include in model to prevent Django from trying to set it

    class Meta:
        managed = False
        db_table = 'lich_hoc_dinh_ky'
        unique_together = (('lop_hoc_phan', 'thu', 'tiet_bat_dau', 'tiet_ket_thuc'),)


class LichSuDangKy(models.Model):
    id = models.UUIDField(primary_key=True)
    sinh_vien = models.ForeignKey('SinhVien', models.DO_NOTHING)
    hoc_ky = models.ForeignKey(HocKy, models.DO_NOTHING, blank=True, null=True)
    ngay_tao = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lich_su_dang_ky'
        unique_together = (('sinh_vien', 'hoc_ky'),)


class LichSuXoaLopHocPhan(models.Model):
    id = models.UUIDField(primary_key=True)
    lop_hoc_phan_id = models.UUIDField()
    ma_lop = models.CharField(max_length=50, blank=True, null=True)
    ten_hoc_phan = models.TextField(blank=True, null=True)
    ten_giang_vien = models.TextField(blank=True, null=True)
    so_luong_toi_da = models.IntegerField(blank=True, null=True)
    so_luong_hien_tai = models.IntegerField(blank=True, null=True)
    phong_hoc = models.TextField(blank=True, null=True)
    ngay_hoc = models.TextField(blank=True, null=True)  # This field type is a guess.
    gio_hoc = models.TextField(blank=True, null=True)
    ngay_bat_dau = models.DateField(blank=True, null=True)
    ngay_ket_thuc = models.DateField(blank=True, null=True)
    tong_so_tiet = models.IntegerField(blank=True, null=True)
    dia_diem = models.TextField(blank=True, null=True)
    nguoi_xoa = models.UUIDField(blank=True, null=True)
    thoi_gian_xoa = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lich_su_xoa_lop_hoc_phan'


class LopHocPhan(models.Model):
    id = models.UUIDField(primary_key=True)
    hoc_phan = models.ForeignKey(HocPhan, models.DO_NOTHING)
    ma_lop = models.CharField(max_length=20)
    giang_vien = models.ForeignKey(GiangVien, models.DO_NOTHING, blank=True, null=True)
    so_luong_toi_da = models.IntegerField(blank=True, null=True)
    so_luong_hien_tai = models.IntegerField(blank=True, null=True)
    phong_mac_dinh = models.ForeignKey('Phong', models.DO_NOTHING, blank=True, null=True)
    trang_thai_lop = models.CharField(max_length=20, blank=True, null=True)
    ngay_bat_dau = models.DateField(blank=True, null=True)
    ngay_ket_thuc = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lop_hoc_phan'
        unique_together = (('hoc_phan', 'ma_lop'),)


class MienGiamHocPhi(models.Model):
    id = models.UUIDField(primary_key=True)
    sinh_vien = models.ForeignKey('SinhVien', models.DO_NOTHING)
    hoc_ky = models.ForeignKey(HocKy, models.DO_NOTHING)
    loai = models.CharField(max_length=50)
    ti_le_giam = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    mien_phi = models.BooleanField(blank=True, null=True)
    ghi_chu = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mien_giam_hoc_phi'
        unique_together = (('sinh_vien', 'hoc_ky', 'loai'),)


class MonDieuKien(models.Model):
    id = models.UUIDField(primary_key=True)
    mon_hoc = models.ForeignKey('MonHoc', models.DO_NOTHING)
    mon_lien_quan = models.ForeignKey('MonHoc', models.DO_NOTHING, related_name='mondieukien_mon_lien_quan_set')
    loai = models.CharField(max_length=20)
    bat_buoc = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mon_dieu_kien'
        unique_together = (('mon_hoc', 'mon_lien_quan', 'loai'),)


class MonHoc(models.Model):
    id = models.UUIDField(primary_key=True)
    ma_mon = models.CharField(unique=True, max_length=20)
    ten_mon = models.CharField(max_length=255)
    so_tin_chi = models.IntegerField()
    khoa = models.ForeignKey(Khoa, models.DO_NOTHING)
    loai_mon = models.CharField(max_length=50, blank=True, null=True)
    la_mon_chung = models.BooleanField(blank=True, null=True)
    thu_tu_hoc = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'mon_hoc'


class MonHocNganh(models.Model):
    id = models.UUIDField(primary_key=True)
    mon_hoc = models.ForeignKey(MonHoc, models.DO_NOTHING)
    nganh = models.ForeignKey('NganhHoc', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'mon_hoc_nganh'
        unique_together = (('mon_hoc', 'nganh'),)


class NganhHoc(models.Model):
    id = models.UUIDField(primary_key=True)
    ma_nganh = models.CharField(unique=True, max_length=20)
    ten_nganh = models.CharField(max_length=255)
    khoa = models.ForeignKey(Khoa, models.DO_NOTHING)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nganh_hoc'


class NienKhoa(models.Model):
    id = models.UUIDField(primary_key=True)
    ten_nien_khoa = models.CharField(unique=True, max_length=20)
    ngay_bat_dau = models.DateField(blank=True, null=True)
    ngay_ket_thuc = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'nien_khoa'


class PaymentIpnLogs(models.Model):
    id = models.UUIDField(primary_key=True)
    transaction = models.ForeignKey('PaymentTransactions', models.DO_NOTHING, blank=True, null=True)
    received_at = models.DateTimeField(blank=True, null=True)
    payload = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payment_ipn_logs'


class PaymentTransactions(models.Model):
    id = models.UUIDField(primary_key=True)
    provider = models.CharField(max_length=20, blank=True, null=True)
    order_id = models.TextField(unique=True)
    sinh_vien = models.ForeignKey('SinhVien', models.DO_NOTHING)
    hoc_ky = models.ForeignKey(HocKy, models.DO_NOTHING)
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    currency = models.CharField(max_length=10, blank=True, null=True)
    status = models.CharField(max_length=20)
    payment_method = models.CharField(max_length=30, blank=True, null=True)
    pay_url = models.TextField(blank=True, null=True)
    result_code = models.TextField(blank=True, null=True)
    message = models.TextField(blank=True, null=True)
    callback_raw = models.JSONField(blank=True, null=True)
    signature_valid = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'payment_transactions'


class Phong(models.Model):
    id = models.UUIDField(primary_key=True)
    ma_phong = models.CharField(max_length=20)
    co_so = models.ForeignKey(CoSo, models.DO_NOTHING, blank=True, null=True)
    suc_chua = models.IntegerField(blank=True, null=True)
    da_dc_su_dung = models.BooleanField(blank=True, null=True)
    khoa = models.ForeignKey(Khoa, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'phong'
        unique_together = (('ma_phong', 'co_so'),)


class PhongDaoTao(models.Model):
    id = models.OneToOneField('Users', models.DO_NOTHING, db_column='id', primary_key=True)
    chuc_vu = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'phong_dao_tao'


class PlayingWithNeon(models.Model):
    name = models.TextField()
    value = models.FloatField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'playing_with_neon'


class ResetToken(models.Model):
    id = models.UUIDField(primary_key=True)
    tai_khoan = models.ForeignKey('TaiKhoan', models.DO_NOTHING)
    token = models.TextField(unique=True)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'reset_token'


class Session(models.Model):
    id = models.UUIDField(primary_key=True)
    tai_khoan = models.ForeignKey('TaiKhoan', models.DO_NOTHING)
    sid = models.CharField(unique=True, max_length=128)
    created_at = models.DateTimeField()
    expires_at = models.DateTimeField(blank=True, null=True)
    revoked = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'session'


class SinhVien(models.Model):
    id = models.OneToOneField('Users', models.DO_NOTHING, db_column='id', primary_key=True)
    ma_so_sinh_vien = models.CharField(unique=True, max_length=20)
    lop = models.CharField(max_length=50, blank=True, null=True)
    khoa = models.ForeignKey(Khoa, models.DO_NOTHING)
    khoa_hoc = models.CharField(max_length=10, blank=True, null=True)
    ngay_nhap_hoc = models.DateField(blank=True, null=True)
    nganh = models.ForeignKey(NganhHoc, models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'sinh_vien'


class TaiKhoan(models.Model):
    id = models.UUIDField(primary_key=True)
    ten_dang_nhap = models.CharField(unique=True, max_length=50)
    mat_khau = models.CharField(max_length=255)
    loai_tai_khoan = models.CharField(max_length=20)
    trang_thai_hoat_dong = models.BooleanField(blank=True, null=True)
    ngay_tao = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tai_khoan'


class TaiLieu(models.Model):
    id = models.UUIDField(primary_key=True)
    lop_hoc_phan = models.ForeignKey(LopHocPhan, models.DO_NOTHING)
    ten_tai_lieu = models.TextField()
    file_path = models.TextField()
    file_type = models.TextField(blank=True, null=True)
    uploaded_by = models.ForeignKey('Users', models.DO_NOTHING, db_column='uploaded_by', blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'tai_lieu'


class ThongBao(models.Model):
    id = models.UUIDField(primary_key=True)
    tieu_de = models.TextField()
    noi_dung = models.TextField()
    nguoi_gui = models.ForeignKey('Users', models.DO_NOTHING, blank=True, null=True)
    lop_hoc_phan = models.ForeignKey(LopHocPhan, models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'thong_bao'


class ThongBaoNguoiNhan(models.Model):
    id = models.UUIDField(primary_key=True)
    thong_bao = models.ForeignKey(ThongBao, models.DO_NOTHING)
    sinh_vien = models.ForeignKey(SinhVien, models.DO_NOTHING, blank=True, null=True)
    da_doc = models.BooleanField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'thong_bao_nguoi_nhan'


class TroLyKhoa(models.Model):
    id = models.OneToOneField('Users', models.DO_NOTHING, db_column='id', primary_key=True)
    khoa = models.ForeignKey(Khoa, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'tro_ly_khoa'


class TruongKhoa(models.Model):
    id = models.OneToOneField('Users', models.DO_NOTHING, db_column='id', primary_key=True)
    khoa = models.OneToOneField(Khoa, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'truong_khoa'


class Users(models.Model):
    id = models.UUIDField(primary_key=True)
    ma_nhan_vien = models.CharField(max_length=20, blank=True, null=True)
    ho_ten = models.CharField(max_length=255)
    tai_khoan = models.ForeignKey(TaiKhoan, models.DO_NOTHING, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)
    updated_at = models.DateTimeField(blank=True, null=True)
    email = models.TextField(unique=True)  # This field type is a guess.

    class Meta:
        managed = False
        db_table = 'users'
