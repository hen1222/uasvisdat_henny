# 🩺 Peta Kesehatan Indonesia: Siapa yang Tertinggal?

Web story interaktif tentang ketimpangan kesehatan di Indonesia, dibangun dengan data Badan Pusat Statistik (BPS). Cerita bergerak dari peta 514 kabupaten/kota, ke pola 38 provinsi pada 10 indikator kesehatan dan sosial, sampai ke arus impor produk terkait kesehatan.

**🔗 Aplikasi (tanpa login, tanpa instalasi): [GANTI-DENGAN-LINK-APLIKASI.streamlit.app](https://GANTI-DENGAN-LINK-APLIKASI.streamlit.app)**

![alt text](tampilanawal.png)


## Isi cerita

| Bab | Pertanyaan | Visualisasi |
|---|---|---|
| **1. Geospasial** | Tinggal di mana, hidup berapa lama? | Choropleth dan peta simbol proporsional (UHH, kemiskinan, sanitasi layak) dengan klasifikasi kuantil atau natural breaks; tabel kelas; grafik rentang di dalam provinsi |
| **2. Data berdimensi tinggi** | Provinsi mana yang mirip, dan mana yang menyimpang? | Biplot PCA dengan klaster K-Means dan penanda pencilan; parallel coordinates; heatmap terklaster (Ward); radar perbandingan. Seleksi di biplot menyorot provinsi yang sama di semua tampilan (*brushing & linking*) |
| **3. Hierarki** | Ke mana uang impor kesehatan pergi? | Treemap, sunburst, dan icicle struktur SITC (kelompok → sub-kelompok → komoditas); ukuran = nilai impor, warna = pertumbuhan 2025 vs 2024 |

## Metode singkat

- **Klasifikasi peta:** kuantil, atau natural breaks lewat K-Means 1-D (setara Jenks), 5 kelas. Choropleth memakai rasio (persen/tahun), bukan angka absolut.
- **Indeks gabungan provinsi:** rata-rata z-score 10 indikator dengan arah dikoreksi (penduduk miskin, angka kesakitan, dan merokok dibalik agar nilai tinggi selalu berarti lebih baik).
- **PCA dan klaster:** PCA 2 komponen pada data terstandarisasi; K-Means dengan K = 2–5 (dapat diatur pengguna); klaster diurutkan menurut indeks gabungan.
- **Pencilan:** jarak Mahalanobis² di atas kuantil χ² 97,5% (derajat bebas = jumlah indikator).
- **Heatmap:** urutan baris dan kolom dari klaster hierarkis (linkage Ward).
- **Teks insight** (nama daerah, angka, korelasi) dihitung langsung dari data, bukan ditulis manual, sehingga ikut berubah jika data diperbarui. Korelasi yang ditampilkan adalah asosiasi, bukan bukti sebab-akibat.

## Struktur repositori

```
.
├── app.py                      # aplikasi Streamlit
├── requirements.txt
├── .streamlit/config.toml
└── data/
    ├── data_multivariate.xlsx  # 38 provinsi × 10 indikator
    ├── data_geospasial.xlsx    # indikator kab/kota (UHH, kemiskinan, sanitasi, penduduk)
    ├── data_hirarki.xlsx       # impor per kode SITC 3 digit, 2024 dan 2025
    └── indonesia_kabupaten.geojson  # batas wilayah kab/kota
```

## Menjalankan di komputer sendiri

```bash
git clone https://github.com/USERNAME/NAMA-REPO.git
cd NAMA-REPO
pip install -r requirements.txt
streamlit run app.py
```

Butuh Python 3.10 atau lebih baru. Aplikasi terbuka di `http://localhost:8501`.

## Sumber data

Seluruh data statistik bersumber dari **BPS** (https://www.bps.go.id), diakses 2 Oktober 2026.

| Kode | Judul tabel/publikasi | Tahun | URL |
|---|---|---|---|
| `uhh_p` | Usia Harapan Hidup Saat Lahir (UHH) menurut Provinsi | 2024 | https://www.bps.go.id/id/statistics-table/2/NDE0IzI=/-metode-baru--umur-harapan-hidup-saat-lahir--uhh-.html |
| `miskin_p` | Persentase Penduduk Miskin (P0) menurut Provinsi | 2024 | https://www.bps.go.id/id/statistics-table/2/NjIxIzI=/persentase-penduduk-miskin-menurut-kabupaten-kota.html |
| `rls_p` | Rata-rata Lama Sekolah menurut Provinsi (IPM) | 2024 | https://www.bps.go.id/id/statistics-table/2/NDE1IzI=/-metode-baru--rata-rata-lama-sekolah.html |
| `peng_p` | Pengeluaran per Kapita Disesuaikan menurut Provinsi (IPM) | 2024 | https://www.bps.go.id/id/statistics-table/2/NDE2IzI=/-metode-baru--pengeluaran-per-kapita-disesuaikan.html |
| `san_p` | Persentase Rumah Tangga dengan Akses Sanitasi Layak menurut Provinsi | 2024 | https://www.bps.go.id/id/statistics-table/2/ODM0IzI=/persentase-rumah-tangga-menurut-provinsi--tipe-daerah-dan-sanitasi-layak.html |
| `air_p` | Persentase Rumah Tangga dengan Akses Sumber Air Minum Layak menurut Provinsi dan Klasifikasi Desa | 2024 | https://www.bps.go.id/id/statistics-table/2/ODU0IzI=/persentase-rumah-tangga-yang-memiliki-akses-terhadap-sumber-air-minum-layak-menurut-provinsi-dan-klasifikasi-desa--persen-.html |
| `morb_p` | Persentase Penduduk yang Mempunyai Keluhan Kesehatan dalam Sebulan Terakhir menurut Provinsi | 2024 | https://www.bps.go.id/id/statistics-table/2/MjIyIzI=/persentase-penduduk-yang-mempunyai-keluhan-kesehatan-dalam-sebulan-terakhir-menurut-provinsi.html |
| `imun_p` | Persentase Anak Umur 12–23 Bulan yang Menerima Imunisasi Dasar Lengkap menurut Provinsi | 2024 | https://www.bps.go.id/id/statistics-table/2/MjI4MCMy/percentage-of-children-12-23-months-who-have-received-complete-basic-immunization-by-province.html |
| `jkn_p` | Persentase Penduduk yang Memiliki Jaminan Kesehatan Nasional (JKN) menurut Provinsi | 2024 | https://www.bps.go.id/id/statistics-table/2/MjI3OSMy/persentase-penduduk-yang-memiliki-jaminan-kesehatan-nasional--jkn--menurut-provinsi.html |
| `rokok_p` | Persentase Penduduk Berumur 15 Tahun ke Atas yang Merokok Tembakau selama Sebulan Terakhir menurut Provinsi | 2024 | https://www.bps.go.id/id/statistics-table/2/MTQzNSMy/persentase-merokok-pada-penbangun-umur-15-tahun-menrut-provinsi.html |
| `miskin_k` | Persentase Penduduk Miskin menurut Kabupaten/Kota | 2024 | https://www.bps.go.id/id/statistics-table/2/NjIxIzI=/persentase-penduduk-miskin--p0--menurut-kabupaten-kota.html |
| `uhh_k` | [Metode Baru] Umur Harapan Hidup Saat Lahir (UHH) menurut Kabupaten/Kota | 2024 | https://www.bps.go.id/id/statistics-table/2/NDE0IzI=/-metode-baru--umur-harapan-hidup-saat-lahir--uhh-.html |
| `san_k` | Persentase Rumah Tangga dengan Akses Sanitasi Layak menurut Kabupaten/Kota | 2024 | https://www.bps.go.id/id/statistics-table/2/Mjc0OCMy/6-2-1-persentase-rumah-tangga-yang-memiliki-akses-terhadap-sanitasi-layak-menurut-kabupaten-kota-persen.html |
| `pend_k` | Jumlah Penduduk menurut Kabupaten/Kota | 2024 | https://www.bps.go.id/id/statistics-table/2/Mjc9MCMy/jumlah-penduduk-menurut-kabupaten-kota-dan-kelompok-umur.html |
| `hir` | Statistik Perdagangan Luar Negeri Indonesia Menurut Kode SITC | 2024/2025 | https://www.bps.go.id/id/publication/2026/08/31/e15722f0d16e51d9c64536a2/statistik-perdagangan-luar-negeri-indonesia-menurut-kode-sitc-2004-dan-2025.html |
| `batas` | Batas wilayah administrasi kab/kota (GeoJSON) | – | **Bukan dari BPS.** [ISI: nama pembuat/penyedia dan URL file GeoJSON] |

## Pengolahan data dan keterbatasan

- **Kode wilayah Papua.** GeoJSON memakai kode Papua dan Papua Barat sebelum pemekaran 2022, sedangkan data BPS memakai kode baru. 26 poligon dicocokkan lewat nama kab/kota (tabel konversi `KODE_LAMA_KE_BARU` di `app.py`); file GeoJSON tidak diubah.
- **Kab/kota tanpa poligon.** Daerah yang belum ada poligonnya di file batas wilayah (saat ini Muna Barat, Buton Tengah, dan Buton Selatan, pemekaran Sulawesi Tenggara) tidak tergambar di peta, tetapi tetap dihitung di tabel dan statistik. Jumlahnya ditampilkan di keterangan peta.
- **Data kosong.** Beberapa daerah tidak memiliki data sanitasi; jumlahnya ditampilkan di keterangan peta.
- **Cakupan komoditas impor.** Bab 3 memakai tujuh kode SITC 3 digit. Sebagian kode (misalnya instrumen optik, meter, dan instrumen ukur/kontrol) mencakup alat yang tidak khusus kesehatan, sehingga total nilainya tidak boleh dibaca sebagai impor produk kesehatan murni.
- **Asosiasi bukan kausalitas.** Korelasi antarindikator pada data agregat provinsi tidak membuktikan hubungan sebab-akibat.

## Deklarasi penggunaan alat bantu AI

Alat bantu AI peninjauan error pada aplikasi. Seluruh data, sumber, dan interpretasi menjadi tanggung jawab penulis.

## Lisensi

Kode dilisensikan di bawah **MIT** (tambahkan berkas `LICENSE`). Data statistik tetap mengikuti ketentuan penggunaan BPS, dan batas wilayah mengikuti lisensi penyedia GeoJSON.

## Penulis

**Penyusun:**
* **Nama:** Henny Merry Astutik
* **NIM:** 222313120
* **Kelas:** 3SD2#   u a s v i s d a t _ h e n n y  
 