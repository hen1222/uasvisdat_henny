# 🩺 Peta Kesehatan Indonesia: Siapa yang Tertinggal?

Web story interaktif tentang ketimpangan kesehatan di Indonesia, dibangun dengan data Badan Pusat Statistik (BPS). Cerita bergerak dari angka nasional, ke peta 514 kabupaten/kota, ke pola 38 provinsi pada 10 indikator, ke arus impor produk terkait kesehatan, lalu berakhir pada profil daerah yang bisa dipilih pembaca sendiri. Seluruh teks penjelasan dan insight dihitung dari data dan ikut berubah mengikuti pilihan pengguna.

**🔗 Aplikasi : (https://uasvisdat-henny.streamlit.app)**

![alt text](tampilanawal.png)

## Isi cerita

| Bab | Pertanyaan | Isi |
|---|---|---|
| **0. Skala** | Seberapa sehat Indonesia, dan seberapa lebar jaraknya? | Kartu angka nasional (rata-rata tertimbang penduduk) dan batang peringkat 38 provinsi untuk 10 indikator pilihan |
| **1. Geospasial** | Tinggal di mana, hidup berapa lama? | Peta UHH, kemiskinan, dan sanitasi: choropleth, simbol proporsional, atau klaster LISA (Moran). Filter wilayah dan pencarian kab/kota. Tabel kelas, histogram kuantil vs natural breaks, dan rentang di dalam provinsi |
| **2. Data berdimensi tinggi** | Provinsi mana yang mirip, dan mana yang menyimpang? | Biplot PCA berklaster yang terhubung ke parallel coordinates (seleksi kotak/lasso menyorot provinsi yang sama), heatmap terklaster, dan radar |
| **3. Hierarki** | Ke mana uang impor kesehatan pergi? | Treemap, sunburst, dan icicle struktur SITC (kelompok → sub-kelompok → komoditas); ukuran = nilai impor, warna divergen = pertumbuhan 2025 vs 2024; navigasi dropdown dan breadcrumb |
| **4. Cek daerahmu** | Di mana posisi daerah saya? | Kartu profil satu kab/kota pada tiga indikator: peringkat nasional dan provinsi, selisih dari rata-rata, klaster LISA, dan histogram posisi |

## Fitur unduh

- **Gambar (PNG):** arahkan kursor ke grafik dan klik ikon kamera di pojok kanan atas. Hasilnya PNG beresolusi 3×. Pada peta dengan **Latar peta = “Tanpa latar”**, PNG-nya transparan dan legenda ikut di samping peta. Pada mode “Dengan peta dasar”, latar peta dasar ikut tersimpan. Legenda grafik lain (biplot, histogram, radar) juga berada di sisi kanan.
- **Data (CSV):** tombol unduh tersedia untuk peringkat provinsi, rentang di dalam provinsi, dan data multivariat provinsi.
- Unduhan gambar dibuat di peramban, sehingga tidak memerlukan paket tambahan di server.

## Metode singkat

- **Klasifikasi peta:** lima kelas, kuantil atau *natural breaks* (K-Means satu dimensi, setara Fisher–Jenks). Kelas dihitung dari seluruh Indonesia agar warna sebanding antarwilayah. Choropleth memakai rasio (persen/tahun), bukan angka absolut.
- **Rata-rata tertimbang penduduk:** x̄ = Σ(xᵢ·Pᵢ)/ΣPᵢ dengan Pᵢ jumlah penduduk kab/kota.
- **Autokorelasi spasial (Bab 1, 4):** nilai dibakukan; bobot spasial dari enam tetangga terdekat menurut jarak antartitik pusat poligon, distandardisasi per baris. Indeks Moran global dan klaster LISA lokal; signifikansi dari 499 permutasi acak (nilai *p* terkecil 0,002), α = 0,05. Klaster: tinggi-tinggi, rendah-rendah, tinggi-rendah, rendah-tinggi, tidak signifikan. Tanpa koreksi uji berganda.
- **Indeks gabungan provinsi (Bab 2):** rata-rata z-score 10 indikator dengan arah dikoreksi (kemiskinan, angka kesakitan, dan merokok dibalik agar nilai tinggi selalu berarti lebih baik).
- **PCA dan klaster:** PCA 2 komponen pada data terstandarisasi; K-Means dengan K = 2–5 (diatur pengguna), klaster diurutkan menurut indeks gabungan; urutan heatmap dari klaster hierarkis Ward.
- **Pencilan:** jarak Mahalanobis² d² = zᵀS⁻¹z (S = kovarians antarindikator, memakai pseudo-inversi) di atas kuantil χ² 97,5% dengan df = 10. Karena hanya ada 38 provinsi untuk 10 indikator, taksiran S tidak stabil dan pendekatan χ² kasar; penanda ini dipakai sebagai alat penjelajah, bukan uji formal.
- **Hierarki impor:** nilai tiap kelompok adalah jumlah nilai komoditas di bawahnya; pertumbuhan dihitung dari nilai yang dijumlahkan di tiap tingkat, bukan dari rata-rata pertumbuhan anaknya.
- **Teks insight** (nama daerah, angka, korelasi) dihitung langsung dari data. Korelasi yang ditampilkan adalah asosiasi, bukan bukti sebab-akibat.

## Struktur repositori

```
.
├── app.py                      # aplikasi Streamlit
├── requirements.txt
├── .streamlit/config.toml
└── data/
    ├── data_multivariate.xlsx  # 38 provinsi × 10 indikator
    ├── data_geospasial.xlsx    # indikator kab/kota (UHH, kemiskinan, sanitasi, jumlah penduduk)
    ├── data_hirarki.xlsx       # impor per kode SITC 3 digit, 2024 dan 2025
    └── indonesia_kabupaten.geojson  # batas wilayah kab/kota
```

## Menjalankan di komputer sendiri

```bash
git clone https://github.com/hen1222/uasvisdat_henny.git
cd uasvisdat_henny
pip install -r requirements.txt
streamlit run app.py
```

Butuh Python 3.10 atau lebih baru. Aplikasi terbuka di `http://localhost:8501`.

## Sumber data

Seluruh data statistik bersumber dari **BPS** (https://www.bps.go.id), diakses 2 Oktober 2026. Katalog yang sama tampil di dalam aplikasi pada bagian “Catatan data dan metodologi” dan dapat diedit di `sources.py`.

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
| `batas` | Batas wilayah administrasi kab/kota (GeoJSON) | – | - |

## Pengolahan data dan keterbatasan

- **Kode wilayah Papua.** GeoJSON memakai kode Papua dan Papua Barat sebelum pemekaran 2022, sedangkan data BPS memakai kode baru. 26 poligon dicocokkan lewat nama kab/kota (tabel `KODE_LAMA_KE_BARU` di `app.py`); file GeoJSON tidak diubah. Tanpa langkah ini, 29 kab/kota (termasuk Nduga, Asmat, dan Jayawijaya) tidak tergambar di peta.
- **Kab/kota tanpa poligon.** Daerah yang belum ada poligonnya di file batas wilayah (saat ini Muna Barat, Buton Tengah, dan Buton Selatan, pemekaran Sulawesi Tenggara) tidak tergambar di peta, tetapi tetap dihitung di tabel dan statistik.
- **Data kosong.** Beberapa daerah tidak memiliki data sanitasi (511 dari 514 daerah bernilai).
- **LISA dan Moran.** Tetangga ditentukan dari enam titik pusat terdekat, bukan batas bersama (kontigu); hasil lokal bersifat eksploratif dan tanpa koreksi uji berganda.
- **Klaster provinsi.** Siluet K-Means rendah pada K = 3 (≈ 0,20); struktur yang kuat terutama berasal dari terpisahnya Papua Tengah dan Papua Pegunungan. Baca klaster K1–K2 sebagai gradasi.
- **Cakupan komoditas impor.** Bab 3 memakai tujuh kode SITC 3 digit. Sebagian kode (instrumen optik, meter, dan instrumen ukur/kontrol) mencakup alat yang tidak khusus kesehatan, sehingga total nilainya tidak boleh dibaca sebagai impor produk kesehatan murni. Aplikasi tidak memuat data produksi dalam negeri, sehingga pernyataan tentang ruang substitusi impor adalah interpretasi, bukan temuan.
- **Potong lintang.** Data bersifat satu waktu (indikator 2024; impor 2024–2025) sehingga tidak menunjukkan tren.
- **Asosiasi bukan kausalitas.** Korelasi pada data agregat provinsi tidak membuktikan hubungan sebab-akibat dan rentan terhadap kekeliruan ekologis.

## Deklarasi penggunaan alat bantu AI

Alat bantu AI digunakan dalam pengoreksi kode dan peninjauan aplikasi ini. Seluruh data, sumber, makalah, desain, alur penelitian, dan interpretasi menjadi tanggung jawab penulis.

## Lisensi

Kode dilisensikan di bawah **MIT** (tambahkan berkas `LICENSE`). Data statistik tetap mengikuti ketentuan penggunaan BPS, dan batas wilayah mengikuti lisensi penyedia GeoJSON.

## Penulis

Henny Merry Astutik (NIM 222313120) · Politeknik Statistika STIS · 2026
