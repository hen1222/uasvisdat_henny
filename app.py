import os, warnings
os.environ.setdefault("OMP_NUM_THREADS", "1")
warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
import json
from collections import Counter
from pathlib import Path
import numpy as np, pandas as pd, streamlit as st
import plotly.express as px, plotly.graph_objects as go
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from scipy.cluster.hierarchy import linkage, leaves_list
from scipy.stats import chi2

TGL = "2 Oktober 2026"
U = "https://www.bps.go.id/"
DS = {
    "uhh_p": ("UHH", "Usia Harapan Hidup Saat Lahir (UHH) menurut Provinsi", "2024", "https://www.bps.go.id/id/statistics-table/2/NDE0IzI=/-metode-baru--umur-harapan-hidup-saat-lahir--uhh-.html", True),
    "miskin_p": ("Kemiskinan", "Persentase Penduduk Miskin (P0) menurut Provinsi", "2024", "https://www.bps.go.id/id/statistics-table/2/NjIxIzI=/persentase-penduduk-miskin-menurut-kabupaten-kota.html", True),
    "rls_p": ("Rata-rata lama sekolah", "Rata-rata Lama Sekolah menurut Provinsi (IPM)", "2024", "https://www.bps.go.id/id/statistics-table/2/NDE1IzI=/-metode-baru--rata-rata-lama-sekolah.html", True),
    "peng_p": ("Pengeluaran per kapita", "Pengeluaran per Kapita Disesuaikan menurut Provinsi (IPM)", "2024", "https://www.bps.go.id/id/statistics-table/2/NDE2IzI=/-metode-baru--pengeluaran-per-kapita-disesuaikan.html", True),
    "san_p": ("Sanitasi layak", "Persentase Rumah Tangga yang Memiliki Akses terhadap Sanitasi Layak menurut Provinsi", "2024", "https://www.bps.go.id/id/statistics-table/2/ODM0IzI=/persentase-rumah-tangga-menurut-provinsi--tipe-daerah-dan-sanitasi-layak.html", True),
    "air_p": ("Air minum layak", "Persentase Rumah Tangga yang Memiliki Akses terhadap Sumber Air Minum Layak menurut Provinsi dan Klasifikasi Desa", "2024", "https://www.bps.go.id/id/statistics-table/2/ODU0IzI=/persentase-rumah-tangga-yang-memiliki-akses-terhadap-sumber-air-minum-layak-menurut-provinsi-dan-klasifikasi-desa--persen-.html", True),
    "morb_p": ("Angka kesakitan", "Persentase Penduduk yang Mempunyai Keluhan Kesehatan dalam Sebulan Terakhir Menurut Provinsi (Persen)", "2024", "https://www.bps.go.id/id/statistics-table/2/MjIyIzI=/persentase-penduduk-yang-mempunyai-keluhan-kesehatan-dalam-sebulan-terakhir-menurut-provinsi.html", True),
    "imun_p": ("Imunisasi dasar", "Persentase Anak Umur 12-23 Bulan yang Menerima Imunisasi Dasar Lengkap menurut Provinsi", "2024", "https://www.bps.go.id/id/statistics-table/2/MjI4MCMy/percentage-of-children-12-23-months-who-have-received-complete-basic-immunization-by-province.html", True),
    "jkn_p": ("JKN", "Persentase Penduduk yang Memiliki Jaminan Kesehatan Nasional (JKN) menurut Provinsi", "2024", "https://www.bps.go.id/id/statistics-table/2/MjI3OSMy/persentase-penduduk-yang-memiliki-jaminan-kesehatan-nasional--jkn--menurut-provinsi.html", True),
    "rokok_p": ("Merokok", "Persentase Penduduk Berumur 15 Tahun ke Atas yang Merokok Tembakau selama Sebulan Terakhir menurut Provinsi", "2024", "https://www.bps.go.id/id/statistics-table/2/MTQzNSMy/persentase-merokok-pada-penbangun-umur-15-tahun-menrut-provinsi.html", True),
    "miskin_k": ("Kemiskinan kab/kota", "Persentase Penduduk Miskin menurut Kabupaten/Kota", "2024", "https://www.bps.go.id/id/statistics-table/2/NjIxIzI=/persentase-penduduk-miskin--p0--menurut-kabupaten-kota.html", True),
    "uhh_k": ("UHH kab/kota", "[Metode Baru] Umur Harapan Hidup Saat Lahir (UHH) menurut Kabupaten/Kota", "2024", "https://www.bps.go.id/id/statistics-table/2/NDE0IzI=/-metode-baru--umur-harapan-hidup-saat-lahir--uhh-.html", True),
    "san_k": ("Sanitasi kab/kota", "Persentase Rumah Tangga dengan Akses Sanitasi Layak menurut Kabupaten/Kota", "2024", "https://www.bps.go.id/id/statistics-table/2/Mjc0OCMy/6-2-1-persentase-rumah-tangga-yang-memiliki-akses-terhadap-sanitasi-layak-menurut-kabupaten-kota-persen.html", True),
    "pend_k": ("Penduduk kab/kota", "Jumlah Penduduk menurut Kabupaten/Kota", "2024", "https://www.bps.go.id/id/statistics-table/2/Mjc9MCMy/jumlah-penduduk-menurut-kabupaten-kota-dan-kelompok-umur.html", True),
    "hir": ("Perdagangan Luar Negeri", "Statistik Perdagangan Luar Negeri Indonesia Menurut Kode SITC", "2024/2025", "https://www.bps.go.id/id/publication/2026/08/31/e15722f0d16e51d9c64536a2/statistik-perdagangan-luar-negeri-indonesia-menurut-kode-sitc-2004-dan-2025.html", True),
    "batas": ("Batas wilayah", "Batas wilayah administrasi kab/kota (GeoJSON)", "", "-", True),
}

st.set_page_config(page_title="Peta Kesehatan Indonesia", page_icon="🩺", layout="wide")
D = Path(__file__).parent / "data"
OKABE = ["#0072B2", "#E69F00", "#009E73", "#CC79A7", "#D55E00"]
INK, TEAL, SAND = "#10302c", "#0f766e", "#faf6ef"
AUTHOR = "HENNY MERRY ASTUTIK · 222313120"
_v = tuple(int(x) for x in st.__version__.split(".")[:2])
KW = {"width": "stretch"} if _v >= (1, 52) else {"use_container_width": True}
fragment = getattr(st, "fragment", None) or getattr(st, "experimental_fragment", None) or (lambda f: f)
MV = ["uhh_p", "miskin_p", "rls_p", "peng_p", "san_p", "air_p", "morb_p", "imun_p", "jkn_p", "rokok_p"]
def tag(keys):
    ys = sorted({DS[k][2][:4] for k in keys if k != "batas" and DS[k][2]})
    return "Sumber: BPS" + (f" ({ys[0]}" + (f"–{ys[-1]}" if len(ys) > 1 else "") + ")" if ys else "") + ("; batas wilayah: non-BPS" if "batas" in keys else "")

st.markdown(f"""<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,600;9..144,800&family=Inter:wght@400;500;600&display=swap');
:root{{color-scheme:light}} html{{scroll-behavior:smooth}}
html,body,[class*="css"],.stApp{{font-family:'Inter',sans-serif;color:{INK}}} .stApp{{background:{SAND}}}
.block-container{{max-width:1180px;padding-top:4.2rem}}
.stMarkdown,.stMarkdown p,.stMarkdown li,label,[data-testid="stWidgetLabel"] p,[data-testid="stCaptionContainer"] *{{color:{INK}}}
h1,h2,h3{{font-family:'Fraunces',serif!important;color:{INK}}}
.snav{{position:fixed;top:3.75rem;left:0;right:0;z-index:999;background:rgba(250,246,239,.96);border-bottom:1px solid #e3dccb;padding:.45rem 1rem;display:flex;gap:.5rem;overflow-x:auto;white-space:nowrap;justify-content:center}}
.snav a{{border:1px solid #d9d2c3;background:#fff;border-radius:99px;padding:.25rem .8rem;color:{INK}!important;text-decoration:none;font-size:.82rem;font-weight:600}} .snav a:hover{{background:{TEAL};color:#fff!important}}
.hero,.hero *{{color:#fff!important}} .hero{{background:linear-gradient(135deg,#0b3b36 0%,#0f766e 60%,#2a9d8f 100%);border-radius:22px;padding:2.6rem 2.4rem 2.1rem;margin:.5rem 0 1.2rem}}
.hero h1{{font-size:clamp(2rem,5vw,3.6rem);line-height:1.1;margin:.3rem 0 1rem}} .hero p{{font-size:1.08rem;max-width:780px;opacity:.95;margin-bottom:0}}
.kicker{{letter-spacing:.18em;font-size:.75rem;text-transform:uppercase;opacity:.85}}
.cards{{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:.9rem;margin:1rem 0}}
.card{{background:#fff;border:1px solid #e3dccb;border-radius:16px;padding:1rem 1.1rem;box-shadow:0 1px 3px rgba(0,0,0,.05)}}
.card small{{color:#5f6b68;font-size:.78rem;text-transform:uppercase;letter-spacing:.08em}} .card b{{display:block;font-family:'Fraunces',serif;font-size:2rem;color:{TEAL};margin:.2rem 0}} .card span{{font-size:.86rem;color:#44524f;line-height:1.45}}
.chap{{margin:3rem 0 .4rem;padding-top:1.6rem;border-top:1px solid #e3dccb;scroll-margin-top:7rem}} .chap small{{color:{TEAL};font-weight:700;letter-spacing:.14em;text-transform:uppercase}}
.chap h2{{font-size:clamp(1.6rem,3.6vw,2.5rem);margin:.2rem 0}} .lead{{font-size:1.06rem;max-width:840px;line-height:1.7}}
.insight{{border-left:3px solid {TEAL};padding:.15rem 0 .15rem 1rem;margin:1rem 0;line-height:1.75;font-size:1.02rem}}
.read{{color:#4a5a57;font-size:.92rem;line-height:1.65;margin:.5rem 0;padding-left:1rem;border-left:3px solid #e6dcc3}}
.cap{{font-size:.78rem;color:#5f6b68;line-height:1.55;margin:.3rem 0 .4rem;font-style:italic}} .cap b{{font-style:normal;color:{INK}}}
.why{{color:#6b7573;font-size:.82rem;line-height:1.6;margin:.3rem 0 .8rem;padding-left:1rem}}
.crumb{{font-weight:600;color:{INK}}} .teaser{{background:linear-gradient(90deg,#e6f2ef,#faf6ef);border-radius:14px;padding:1rem 1.2rem;margin:2rem 0 .5rem;border:1px solid #cfe3de}}
.teaser b{{color:{TEAL}}} .teaser a{{color:{TEAL}!important;font-weight:600}}
.pc{{background:#fff;border:1px solid #e3dccb;border-radius:14px;padding:.8rem 1rem}} .pc b{{font-family:'Fraunces',serif;font-size:1.7rem;color:{TEAL}}}
.pgrid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:.9rem;align-items:stretch;margin:.6rem 0}}
.pcard{{display:flex;flex-direction:column;background:#fff;border:1px solid #e3dccb;border-radius:16px;padding:1rem 1.1rem;box-shadow:0 1px 3px rgba(0,0,0,.05)}}
.pt{{font-size:.8rem;color:#5f6b68;text-transform:uppercase;letter-spacing:.08em}} .pv{{font-family:'Fraunces',serif;font-size:2.1rem;color:{TEAL};line-height:1.2;margin:.15rem 0 .5rem}} .pv span{{font-size:1rem;color:#5f6b68;font-family:'Inter',sans-serif}}
.prow{{display:flex;justify-content:space-between;gap:.6rem;font-size:.84rem;padding:.28rem 0;border-top:1px solid #f0ebdf}} .prow span{{color:#5f6b68}} .prow b{{text-align:right}} .ok{{color:#0a6b4f}} .bad{{color:#b3470a}}
.badge{{color:#10302c;padding:.05rem .55rem;border-radius:99px;font-size:.78rem}} .pnote{{margin-top:auto;padding-top:.7rem;font-size:.86rem;line-height:1.55;border-top:1px dashed #e3dccb}}
.st-key-metode_box [data-testid="stExpander"] details{{border:none;border-bottom:1px solid #d9d2c3;border-radius:0;background:transparent}} .st-key-metode_box [data-testid="stExpander"] summary{{padding:.9rem .2rem}} .st-key-metode_box [data-testid="stExpander"] summary p{{font-weight:700;font-size:1.05rem}}
@media(max-width:700px){{.hero{{padding:1.8rem 1.2rem}}.snav{{justify-content:flex-start}}}}
@media(max-width:700px){{.block-container{{padding-left:.7rem!important;padding-right:.7rem!important}}.hero{{padding:1.3rem 1rem;border-radius:16px}}.hero h1{{font-size:1.9rem}}.hero p{{font-size:.96rem}}.chap h2{{font-size:1.45rem}}.lead{{font-size:1rem;line-height:1.6}}
.cards{{grid-template-columns:1fr 1fr;gap:.6rem}}.card{{padding:.7rem .8rem}}.card b{{font-size:1.45rem}}.card span{{font-size:.78rem}}.insight{{font-size:.96rem;line-height:1.65;padding-left:.8rem}}.read{{font-size:.88rem}}.why,.cap{{font-size:.76rem}}.pgrid{{grid-template-columns:1fr}}.snav a{{font-size:.76rem;padding:.2rem .6rem}}.teaser{{padding:.8rem}}}}
</style>""", unsafe_allow_html=True)

def chapter(i, kicker, title, lead, anchor):
    st.markdown(f"<div id='{anchor}' class='chap'><small>Bab {i} · {kicker}</small><h2>{title}</h2></div><p class='lead'>{lead}</p>", unsafe_allow_html=True)
def insight(t): st.markdown(f"<div class='insight'>{t}</div>", unsafe_allow_html=True)
def read(t): st.markdown(f"<div class='read'>{t}</div>", unsafe_allow_html=True)
def why(t): st.markdown(f"<div class='why'>{t}</div>", unsafe_allow_html=True)
def cards(items): st.markdown("<div class='cards'>" + "".join(f"<div class='card'><small>{a}</small><b>{b}</b><span>{c}</span></div>" for a, b, c in items) + "</div>", unsafe_allow_html=True)
def teaser(n, anchor, judul, teks): st.markdown(f"<div class='teaser'><b>Berikutnya, Bab {n}</b> — {teks} <a href='#{anchor}'>{judul} →</a></div>", unsafe_allow_html=True)
def cap(title, satuan, catatan, keys):
    short = "; ".join(f"{DS[k][0]} ({DS[k][2]})" for k in keys if k != "batas")
    st.markdown(f"<div class='cap'><b>{title}</b><br>Satuan: {satuan}.<br>{catatan}<br><b>Sumber: BPS</b> — {short}." + (" Batas wilayah: non-BPS." if "batas" in keys else "") + "</div>", unsafe_allow_html=True)
    with st.expander("Rincian sumber (judul, tahun, URL, tanggal akses)"):
        for k in keys:
            d = DS[k]; st.markdown(f"- **{d[1]}**{', ' + d[2] if d[2] else ''} · {d[3] or '-'} · diakses {TGL}" + ("" if d[4] else " · "))
_RM = ["zoom2d", "pan2d", "select2d", "lasso2d", "zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d"]
def _detect_mobile():
    """Deteksi ponsel/tablet otomatis dari header peramban (butuh Streamlit >= 1.37); jika gagal, dianggap desktop."""
    try:
        h = st.context.headers; ua = h.get("User-Agent", "") or ""
        return h.get("Sec-CH-UA-Mobile", "") == "?1" or any(k in ua for k in ("Mobi", "Android", "iPhone", "iPad", "iPod", "Tablet"))
    except Exception: return False
def is_m(): return bool(st.session_state.get("mobile", False))
def cfg(name, lock=False, zoom=False):
    """Konfigurasi grafik: tombol kamera = unduh PNG beresolusi tinggi dengan latar transparan (legenda ikut di sisi grafik)."""
    return {"displaylogo": False, "scrollZoom": zoom, "modeBarButtonsToRemove": _RM if lock else (["zoomIn2d", "zoomOut2d", "autoScale2d", "resetScale2d"] if is_m() else []), "toImageButtonOptions": {"format": "png", "filename": name, "scale": 3}}
def dl(df, label, name):
    st.download_button(label, df.to_csv(index=False).encode("utf-8-sig"), file_name=name + ".csv", mime="text/csv", key="dl_" + name)
def show(fig, h=520, keys=None, lock=False, fname="grafik", leg=False, **kw):
    if lock: fig.update_xaxes(fixedrange=True); fig.update_yaxes(fixedrange=True)
    kw["config"] = cfg(fname, lock); m_ = is_m()
    m = fig.layout.margin; g = lambda v, d: d if v is None else v
    b0 = max(g(m.b, 0), 84 if m_ else 74) + (50 if (m_ and leg) else 0)
    fig.update_layout(height=h, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter", color=INK), margin=dict(l=g(m.l, 10), r=min(g(m.r, 10), 14) if m_ else g(m.r, 10), t=g(m.t, 50), b=b0))
    if m_ and leg: fig.update_layout(legend=dict(orientation="h", yref="container", y=30 / h, yanchor="bottom", x=0, xanchor="left", title=dict(text=""), font=dict(size=10)))
    if keys: fig.add_annotation(text=tag(keys), xref="paper", yref="paper", x=1, y=0, xanchor="right", yanchor="top", yshift=-(b0 - 16), showarrow=False, font=dict(size=10, color="#5f6b68"))
    ev = st.plotly_chart(fig, **KW, **kw)
    return ev if "on_select" in kw else None
def table(df):
    for kw in (KW, {"use_container_width": True}, {}):
        try: st.dataframe(df, **kw); return
        except Exception: continue

LAB = {"uhh": ("Usia Harapan Hidup", "tahun", 1), "persen_miskin": ("Penduduk Miskin", "%", -1), "rls": ("Rata-rata Lama Sekolah", "tahun", 1),
       "pengeluaran_capita": ("Pengeluaran per Kapita", "ribu Rp", 1), "sanitasi_layak": ("Sanitasi Layak", "%", 1), "air_layak": ("Air Minum Layak", "%", 1),
       "morbiditas": ("Angka Kesakitan", "%", -1), "imunisasi_lengkap": ("Imunisasi Dasar Lengkap", "%", 1), "jkn": ("Kepemilikan JKN", "%", 1), "merokok": ("Perokok ≥15 th", "%", -1)}
SHORT = {"uhh": "UHH", "persen_miskin": "Miskin", "rls": "Lama<br>sekolah", "pengeluaran_capita": "Pengeluaran", "sanitasi_layak": "Sanitasi", "air_layak": "Air<br>minum",
         "morbiditas": "Kesakitan", "imunisasi_lengkap": "Imunisasi", "jkn": "JKN", "merokok": "Merokok"}
fz = lambda v, good: f"{LAB[v][0].lower()} {'yang tinggi' if (LAB[v][2] == 1) == good else 'yang rendah'}"
VARS = list(LAB); DIRS = np.array([LAB[v][2] for v in VARS]); flat = lambda s: s.replace("<br>", " ")
INFO = {"uhh": ("Usia Harapan Hidup (UHH)", "rata-rata tahun hidup yang diharapkan bayi baru lahir bila pola kematian saat ini bertahan", "makin tinggi makin baik"),
        "persen_miskin": ("Persentase Penduduk Miskin", "porsi penduduk dengan pengeluaran di bawah garis kemiskinan", "makin tinggi makin buruk"),
        "sanitasi_layak": ("Sanitasi Layak", "persentase rumah tangga yang memakai fasilitas sanitasi layak", "makin tinggi makin baik")}
MAPKEY = {"uhh": "uhh_k", "persen_miskin": "miskin_k", "sanitasi_layak": "san_k"}
PALS = {"uhh": ["#ffffcc", "#a1dab4", "#41b6c4", "#2c7fb8", "#253494"], "sanitasi_layak": ["#ffffcc", "#a1dab4", "#41b6c4", "#2c7fb8", "#253494"], "persen_miskin": ["#ffffd4", "#fed98e", "#fe9929", "#d95f0e", "#993404"]}
REG = {"Indonesia": (-2.3, 118, 3.4), "Sumatera": (-0.5, 101, 4.6), "Jawa & Bali": (-7.6, 111, 5.4), "Nusa Tenggara": (-9, 121, 5.2), "Kalimantan": (0.2, 114, 4.8), "Sulawesi": (-2, 121, 4.8), "Maluku": (-3, 128, 5.3), "Papua": (-4.5, 138, 5.0)}
def region_of(pc): return "Sumatera" if 11 <= pc <= 21 else "Jawa & Bali" if 31 <= pc <= 36 or pc == 51 else "Nusa Tenggara" if pc in (52, 53) else "Kalimantan" if 61 <= pc <= 65 else "Sulawesi" if 71 <= pc <= 76 else "Maluku" if pc in (81, 82) else "Papua"
LISA_C = {"Tinggi-tinggi": "#D55E00", "Rendah-rendah": "#0072B2", "Tinggi-rendah": "#E69F00", "Rendah-tinggi": "#56B4E9", "Tidak signifikan": "#d9d9d9"}

# GeoJSON memakai kode Papua lama (sebelum pemekaran 2022); data BPS memakai kode baru.
KODE_LAMA_KE_BARU = {"9108": "9201", "9107": "9202", "9106": "9203", "9110": "9204", "9109": "9205", "9171": "9271", "9401": "9501", "9413": "9502", "9414": "9503", "9415": "9504",
    "9412": "9601", "9434": "9602", "9436": "9603", "9404": "9604", "9410": "9605", "9435": "9606", "9433": "9607", "9411": "9608",
    "9429": "9701", "9402": "9702", "9430": "9703", "9418": "9704", "9431": "9705", "9432": "9706", "9416": "9707", "9417": "9708"}

@st.cache_resource(show_spinner="Memuat data…")
def load():
    mv = pd.read_excel(D / "data_multivariate.xlsx").rename(columns={"kodeprkab": "provinsi"})
    mv["provinsi"] = mv.provinsi.str.title().replace({"Dki Jakarta": "DKI Jakarta", "Di Yogyakarta": "DI Yogyakarta"})
    geo = pd.read_excel(D / "data_geospasial.xlsx").rename(columns={"kodeprkab": "kabkota"})
    geo["code"] = geo.DISTRICTCODE.astype(str); geo["kabkota"] = geo.kabkota.astype(str)
    geo["jml_miskin"] = (geo.persen_miskin / 100 * geo.jumlah_penduduk).round(); geo["prov_code"] = geo.DISTRICTCODE // 100; geo["region"] = geo.prov_code.map(region_of)
    raw = json.load(open(D / "indonesia_kabupaten.geojson")); cents = {}; feats = []; kode_data = set(geo.code)
    rnd = lambda c: [round(c[0], 3), round(c[1], 3)] if isinstance(c[0], float) else [rnd(x) for x in c]
    for f in raw["features"]:
        p = f["properties"]; code = str(p.get("kodeprkab") or p.get("DISTRICTCODE")); code = KODE_LAMA_KE_BARU.get(code, code)
        if code not in kode_data: continue
        g = f["geometry"]; polys = [g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]
        pts = np.array([c for poly in polys for c in poly[0]]); cents[code] = (pts[:, 1].mean(), pts[:, 0].mean())
        feats.append({"type": "Feature", "properties": {"code": code}, "geometry": {"type": g["type"], "coordinates": rnd(g["coordinates"])}})
    geo["lat"] = geo.code.map(lambda c: cents.get(c, (np.nan,) * 2)[0]); geo["lon"] = geo.code.map(lambda c: cents.get(c, (np.nan,) * 2)[1])
    return mv, geo, {"type": "FeatureCollection", "features": feats}, pd.read_excel(D / "data_hirarki.xlsx")
mv0, geo, gj, hir = load()
provname = dict(zip(mv0.DISTRICTCODE, mv0.provinsi)); cif_total = hir["CIF 2025 (USD)"].sum() / 1e9
wmean = lambda c: (lambda d: (d[c] * d.jumlah_penduduk).sum() / d.jumlah_penduduk.sum())(geo.dropna(subset=[c]))

st.markdown(f"""<div id='top'></div><div class='snav'><a href='#top'>Awal</a><a href='#bab0'>0 Skala</a><a href='#bab1'>1 Peta kab/kota</a><a href='#bab2'>2 Pola provinsi</a><a href='#bab3'>3 Impor kesehatan</a><a href='#bab4'>4 Cek daerahmu</a><a href='#penutup'>Penutup</a><a href='#metode'>Metodologi</a></div>
<div class='hero'><div class='kicker'>Web story · Visualisasi Data BPS</div><h1>Peta Kesehatan Indonesia:<br>Siapa yang Tertinggal?</h1>
<p>Umur panjang bukan hanya urusan rumah sakit. Ia dibentuk oleh air bersih, sanitasi, pendidikan, jaminan kesehatan, dan dompet keluarga. Web story ini mengajak Anda melihat kesehatan Indonesia dari tiga jarak yaitu 514 kabupaten/kota, 38 provinsi, lalu arus impor alat kesehatan. Ayo telurusi daerahmu!!</p></div>""", unsafe_allow_html=True)
st.session_state["mobile"] = _detect_mobile()

# ============ BAB 0 ============
@fragment
def bab0():
    chapter(0, "Skala", "Seberapa sehat Indonesia, dan seberapa lebar jaraknya?", "Angka nasional memberi gambaran awal. Tiga indikator di bawah dirata-rata dengan bobot jumlah penduduk dari seluruh kabupaten/kota, lalu dibandingkan dengan jarak antara daerah terbaik dan terburuk.", "bab0")
    its = []
    for k, f in [("uhh", "{:.1f} tahun"), ("persen_miskin", "{:.1f}%"), ("sanitasi_layak", "{:.1f}%")]:
        d = geo.dropna(subset=[k]); its.append((LAB[k][0] + " (rata-rata tertimbang)", f.format(wmean(k)), f"Rentang antar kab/kota {d[k].min():.1f}–{d[k].max():.1f} {LAB[k][1]}; {INFO[k][2]}."))
    its.append(("Impor produk kesehatan", f"US${cif_total:.1f} M", f"Nilai CIF 2025 untuk {int(hir.shape[0])} komoditas SITC 3 digit."))
    cards(its)
    st.markdown("#### Peringkat 38 provinsi")
    v = st.selectbox("Pilih indikator provinsi", VARS, format_func=lambda k: f"{LAB[k][0]} ({LAB[k][1]})", key="rank_v")
    lab_v, unit_v, dir_v = LAB[v]; d = mv0[["provinsi", v]].sort_values(v, ascending=(dir_v == -1)); n = len(d)   # terbaik di atas
    col = ["#0072B2" if i < 5 else "#D55E00" if i >= n - 5 else "#b9c3c0" for i in range(n)]
    fr = go.Figure(go.Bar(y=d.provinsi, x=d[v], orientation="h", marker_color=col, text=[f"{x:.1f}" for x in d[v]], textposition="outside", cliponaxis=False, hovertemplate="<b>%{y}</b><br>" + lab_v + ": %{x:.2f} " + unit_v + "<extra></extra>"))
    fr.add_vline(x=d[v].mean(), line=dict(color=INK, dash="dash"), annotation_text=f"rata-rata {d[v].mean():.1f}", annotation_position="top")
    fr.update_layout(xaxis_title=f"{lab_v} ({unit_v})", yaxis=dict(autorange="reversed", tickfont=dict(size=10)), margin=dict(t=30, r=40)); show(fr, 900, keys=[MV[VARS.index(v)]], lock=True, fname=f"peringkat_provinsi_{v}"); dl(d.rename(columns={v: f"{lab_v} ({unit_v})"}), "Unduh data peringkat (CSV)", f"peringkat_provinsi_{v}")
    cap(f"Peringkat provinsi menurut {lab_v}", unit_v, "Biru = 5 provinsi terbaik, oranye = 5 terburuk (arah baik/buruk diperhitungkan); garis putus-putus = rata-rata antar provinsi", [MV[VARS.index(v)]])
    b, w = d.iloc[0], d.iloc[-1]; ratio = max(d[v]) / min(d[v])
    insight(f"Untuk {lab_v.lower()}, {b.provinsi} ada di posisi teratas ({b[v]:.1f} {unit_v}) dan {w.provinsi} di dasar peringkat ({w[v]:.1f} {unit_v}); selisihnya {abs(b[v]-w[v]):.1f} {unit_v}. {'Semakin tinggi angkanya semakin baik.' if dir_v == 1 else 'Semakin tinggi angkanya semakin buruk.'} Ayo coba ganti indikatornya, dan perhatikan apakah provinsi yang sama selalu berada di bawah??")
    teaser(1, "bab1", "Peta kabupaten/kota", "angka provinsi menyembunyikan perbedaan yang jauh lebih tajam di dalamnya. Bab berikut turun ke 514 kabupaten/kota.")
bab0()

# ============ BAB 1 ============
@st.cache_data(show_spinner=False)
def edges(ind, meth, k=5):
    s = geo.dropna(subset=["lat", ind])[ind]
    if meth == "Kuantil": return np.unique(np.quantile(s, np.linspace(0, 1, k + 1)))
    c = np.sort(KMeans(k, n_init=10, random_state=1).fit(s.values.reshape(-1, 1)).cluster_centers_.ravel()); return np.r_[s.min(), (c[:-1] + c[1:]) / 2, s.max()]
@st.cache_data(show_spinner=False)
def prep(ind, meth):
    gd = geo.dropna(subset=["lat", ind]).copy(); e = edges(ind, meth); lab = [f"{e[i]:.1f} – {e[i+1]:.1f}" for i in range(len(e) - 1)]
    gd["kelas"] = pd.cut(gd[ind], bins=e, labels=lab, include_lowest=True); return gd, lab
KNN = 6
@st.cache_data(show_spinner="Menghitung autokorelasi spasial…")
def moran(ind, P=499):
    d = geo.dropna(subset=["lat", ind]).reset_index(drop=True); y = d[ind].values; n = len(y); z = (y - y.mean()) / y.std()
    X = d[["lat", "lon"]].values; Dm = ((X[:, None] - X[None]) ** 2).sum(-1); np.fill_diagonal(Dm, np.inf); nb = np.argsort(Dm, 1)[:, :KNN]
    lag = z[nb].mean(1); I = (z * lag).sum() / (z * z).sum(); rng = np.random.default_rng(1)
    Ip = np.array([(zp * zp[nb].mean(1)).sum() / (zp * zp).sum() for zp in (rng.permutation(z) for _ in range(P))]); p = (1 + (Ip >= I).sum()) / (P + 1)
    Ii = z * lag; idx = rng.integers(0, n - 1, (P, n, KNN)); idx += idx >= np.arange(n)[None, :, None]; Iip = z[None, :] * z[idx].mean(2)
    pi = (1 + np.where(Ii > 0, Iip >= Ii, Iip <= Ii).sum(0)) / (P + 1)
    q = np.where(z > 0, np.where(lag > 0, "Tinggi-tinggi", "Tinggi-rendah"), np.where(lag > 0, "Rendah-tinggi", "Rendah-rendah"))
    return I, p, d.assign(z=z, lag=lag, klaster=np.where(pi < .05, q, "Tidak signifikan"))[["code", "kabkota", "prov_code", "region", "z", "lag", "klaster"]]

@st.cache_resource(show_spinner="Menggambar peta…")
def map_fig(ind, meth, layer, size_by, region, focus, mobile=False):
    gd, lab = prep(ind, meth); pal = PALS[ind]; ttl = f"{LAB[ind][0]} ({LAB[ind][1]})"
    nm = {ind: ttl, "jumlah_penduduk": "Jumlah penduduk (jiwa)", "jml_miskin": "Penduduk miskin (jiwa)"}
    hd = {"code": False, "lat": False, "lon": False, ind: ":.2f", "jumlah_penduduk": ":,", "jml_miskin": ":,"}
    base = dict(map_style="carto-positron", hover_name="kabkota", labels=nm)
    if layer == "Choropleth":
        hd["kelas"] = False
        f = px.choropleth_map(gd, geojson=gj, locations="code", featureidkey="properties.code", color="kelas", category_orders={"kelas": lab}, color_discrete_sequence=pal[:len(lab)], hover_data=hd, opacity=.85, **base); f.update_layout(legend_title_text=ttl)
    elif layer == "Simbol proporsional":
        f = px.scatter_map(gd, lat="lat", lon="lon", size=size_by, color=ind, size_max=40, color_continuous_scale=[(i / 4, c) for i, c in enumerate(pal)], hover_data=hd, opacity=.75, **base)
    else:
        I, p, ld = moran(ind); ld = ld.merge(geo[["code", ind, "jumlah_penduduk"]], on="code")
        f = px.choropleth_map(ld, geojson=gj, locations="code", featureidkey="properties.code", color="klaster", category_orders={"klaster": list(LISA_C)}, color_discrete_map=LISA_C, hover_data={"code": False, "klaster": True, ind: ":.2f", "jumlah_penduduk": ":,"}, opacity=.85, **base); f.update_layout(legend_title_text="Klaster LISA")
    c0 = REG[region]; zoom = c0[2] - (1.0 if mobile else 0); ctr = dict(lat=c0[0], lon=c0[1])
    r_ = geo[geo.code == focus]
    if len(r_) and pd.notna(r_.lat.iloc[0]):
        f.add_trace(go.Scattermap(lat=r_.lat, lon=r_.lon, mode="markers+text", text=r_.kabkota, textposition="top right", marker=dict(size=15, color=INK), showlegend=False, hoverinfo="skip")); ctr = dict(lat=float(r_.lat.iloc[0]), lon=float(r_.lon.iloc[0])); zoom = 6 if mobile else 7
    f.update_layout(map=dict(center=ctr, zoom=zoom), height=600, margin=dict(l=0, r=0, t=0, b=34), paper_bgcolor="rgba(0,0,0,0)")
    ks = [MAPKEY[ind], "batas"] + (["pend_k"] if layer != "Klaster LISA (Moran)" else []) + (["miskin_k"] if layer == "Simbol proporsional" and size_by == "jml_miskin" and ind != "persen_miskin" else [])
    if mobile:
        f.update_layout(height=470, margin=dict(l=0, r=0, t=72, b=34), legend=dict(orientation="h", x=0, y=1.01, yanchor="bottom", font=dict(size=10), title=dict(font=dict(size=10))),
                        coloraxis_colorbar=dict(orientation="h", y=1.01, yanchor="bottom", x=0.5, len=.95, thickness=10, title=dict(side="top")))
    f.add_annotation(text=tag(ks), xref="paper", yref="paper", x=1, y=0, xanchor="right", yanchor="top", yshift=-6, showarrow=False, font=dict(size=10, color="#5f6b68")); return f

BOX = {"Indonesia": (94.5, 141.5, -11.5, 6.5), "Sumatera": (94.5, 108.5, -6.3, 6.2), "Jawa & Bali": (104.8, 116, -9, -5.4), "Nusa Tenggara": (115, 127, -11.5, -8), "Kalimantan": (108.5, 119.5, -4.5, 4.5),
       "Sulawesi": (118.5, 125.5, -6, 2), "Maluku": (124, 135, -8.5, 2.5), "Papua": (130.5, 141.5, -9.5, 0.5)}
@st.cache_resource(show_spinner=False)
def polys():
    out = {}
    for f in gj["features"]:
        g = f["geometry"]; xs, ys = [], []
        for poly in ([g["coordinates"]] if g["type"] == "Polygon" else g["coordinates"]): xs += [p[0] for p in poly[0]] + [None]; ys += [p[1] for p in poly[0]] + [None]
        out[f["properties"]["code"]] = (xs, ys)
    return out
def _xy(codes):
    P = polys(); xs, ys = [], []
    for c in codes:
        if c in P: xs += P[c][0]; ys += P[c][1]
    return xs, ys
@st.cache_resource(show_spinner="Menggambar peta…")
def map2d(ind, meth, layer, size_by, region, focus, mobile=False):
    gd, lab = prep(ind, meth); pal = PALS[ind]; lab_i, unit_i, _ = LAB[ind]; f = go.Figure()
    xs, ys = _xy(list(polys())); f.add_trace(go.Scatter(x=xs, y=ys, mode="lines", fill="toself", fillcolor="#ececec", line=dict(width=.3, color="#cfcfcf"), hoverinfo="skip", showlegend=False))
    hov = [f"<b>{r.kabkota}</b><br>{provname.get(r.prov_code, '')}<br>{lab_i}: {getattr(r, ind):.1f} {unit_i}<br>Penduduk: {int(r.jumlah_penduduk):,}<br>Penduduk miskin: {int(r.jml_miskin):,}" for r in gd.itertuples()]
    if layer == "Choropleth":
        for l_, c_ in zip(lab, pal):
            x_, y_ = _xy(gd[gd.kelas == l_].code); f.add_trace(go.Scatter(x=x_, y=y_, mode="lines", fill="toself", fillcolor=c_, line=dict(width=.3, color="#666"), name=l_, hoverinfo="skip"))
        f.update_layout(legend=dict(title=dict(text=f"{lab_i} ({unit_i})"), x=1.01, y=.5, xanchor="left", itemsizing="constant"))
    elif layer == "Simbol proporsional":
        v = gd[size_by]; f.add_trace(go.Scatter(x=gd.lon, y=gd.lat, mode="markers", marker=dict(size=v, sizemode="area", sizeref=2. * v.max() / (38 ** 2), color=gd[ind], colorscale=[(i / 4, c) for i, c in enumerate(pal)], opacity=.78, line=dict(width=.4, color="#444"),
            colorbar=(dict(orientation="h", title=dict(text=f"{lab_i} ({unit_i})", side="top"), thickness=10, len=.9, x=0.5, y=-0.02, yanchor="top") if mobile else dict(title=dict(text=f"{lab_i} ({unit_i})", side="right"), thickness=12, len=.6, x=1.01, xanchor="left"))), showlegend=False, hoverinfo="skip"))
    else:
        I, p, ld = moran(ind); ld = ld.merge(gd[["code"]], on="code")
        for k_, c_ in LISA_C.items():
            x_, y_ = _xy(ld[ld.klaster == k_].code); f.add_trace(go.Scatter(x=x_, y=y_, mode="lines", fill="toself", fillcolor=c_, line=dict(width=.3, color="#666"), name=k_, hoverinfo="skip"))
        hov = [h_ + f"<br>Klaster LISA: {k_}" for h_, k_ in zip(hov, gd.code.map(dict(zip(ld.code, ld.klaster))).fillna("-"))]
        f.update_layout(legend=dict(title=dict(text="Klaster LISA"), x=1.01, y=.5, xanchor="left", itemsizing="constant"))
    f.add_trace(go.Scatter(x=gd.lon, y=gd.lat, mode="markers", marker=dict(size=11, opacity=0), text=hov, hovertemplate="%{text}<extra></extra>", showlegend=False))
    x0, x1, y0, y1 = BOX[region]; r_ = geo[geo.code == focus]
    if len(r_) and pd.notna(r_.lat.iloc[0]):
        la, lo = float(r_.lat.iloc[0]), float(r_.lon.iloc[0]); x0, x1, y0, y1 = lo - 2.2, lo + 2.2, la - 1.3, la + 1.3
        f.add_trace(go.Scatter(x=[lo], y=[la], mode="markers+text", text=[r_.kabkota.iloc[0]], textposition="top right", marker=dict(size=11, color=INK, line=dict(width=1.5, color="white")), showlegend=False, hoverinfo="skip"))
    f.update_xaxes(visible=False, range=[x0, x1], constrain="domain"); f.update_yaxes(visible=False, range=[y0, y1], scaleanchor="x", scaleratio=1, constrain="domain")
    if mobile and layer != "Simbol proporsional": f.update_layout(legend=dict(orientation="h", x=0, y=-0.02, yanchor="top", font=dict(size=10), title=dict(text="")))
    f.update_layout(height=int(max(250, min(470, 130 + 340 * (y1 - y0) / (x1 - x0)))) if mobile else 600, dragmode=False if mobile else "pan", margin=dict(l=0, r=0, t=10, b=110 if mobile else 34), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter", color=INK))
    ks = [MAPKEY[ind], "batas"] + (["pend_k"] if layer != "Klaster LISA (Moran)" else []) + (["miskin_k"] if layer == "Simbol proporsional" and size_by == "jml_miskin" and ind != "persen_miskin" else [])
    f.add_annotation(text=tag(ks), xref="paper", yref="paper", x=0, y=0, xanchor="left", yanchor="top", yshift=-96 if mobile else -6, showarrow=False, font=dict(size=10, color="#5f6b68")); return f

@fragment
def bab1():
    chapter(1, "Geospasial", "Tinggal di mana, hidup berapa lama?", f"Umur harapan hidup berbeda hingga {geo.uhh.max()-geo.uhh.min():.1f} tahun antar kabupaten/kota. Pilih indikator, wilayah, klasifikasi, dan jenis peta; cari daerah Anda lewat kotak pencarian. Seluruh deskripsi dan interpretasi di bawah menyesuaikan pilihan Anda.", "bab1")
    c1, c2, c3 = st.columns([1.2, 1, 1]); ind = c1.selectbox("Indikator (rasio)", list(INFO), format_func=lambda k: f"{LAB[k][0]} ({LAB[k][1]})")
    region = c2.selectbox("Wilayah", list(REG)); meth = c3.radio("Klasifikasi", ["Kuantil", "Natural breaks"], horizontal=True)
    c4, c5 = st.columns([1.6, 1.4]); layer = c4.radio("Jenis peta", ["Choropleth", "Simbol proporsional", "Klaster LISA (Moran)"], horizontal=True)
    latar = c5.radio("Latar peta", ["Tanpa latar", "Dengan peta dasar"], horizontal=True, help="Tanpa latar: hanya batas wilayah, hasil unduhan transparan. Dengan peta dasar: ada konteks negara dan laut.")
    names = geo.sort_values(["prov_code", "kabkota"]); lbl = {r.code: f"{r.kabkota} — {provname.get(r.prov_code, '')}" for r in names.itertuples() if pd.notna(r.lat)}
    foc = c5.selectbox("Cari kabupaten/kota", [""] + list(lbl), format_func=lambda c: "(ketik nama daerah…)" if c == "" else lbl[c])
    size_by = "jml_miskin"
    if layer == "Simbol proporsional": size_by = st.radio("Ukuran lingkaran = ", ["jml_miskin", "jumlah_penduduk"], horizontal=True, format_func=lambda x: {"jml_miskin": "Jumlah penduduk miskin", "jumlah_penduduk": "Jumlah penduduk"}[x])
    nm_i, defin, arah = INFO[ind]; lab_i, unit_i, dir_i = LAB[ind]; gdat = geo.dropna(subset=[ind]); gd, lab = prep(ind, meth)
    if region != "Indonesia": gdat = gdat[gdat.region == region]; gd = gd[gd.region == region]
    st.markdown(f"**{nm_i}** — {defin}; *{arah}*. Di **{region}** tersedia untuk {len(gdat)} kab/kota: rata-rata {gdat[ind].mean():.1f} {unit_i}, rentang {gdat[ind].min():.1f}–{gdat[ind].max():.1f}.")
    _lay = {"Choropleth": "koroplet", "Simbol proporsional": "simbol", "Klaster LISA (Moran)": "lisa"}[layer]
    if latar == "Tanpa latar": st.plotly_chart(map2d(ind, meth, layer, size_by, region, foc, is_m()), config=cfg(f"peta_{ind}_{_lay}", zoom=not is_m()), **KW)
    else:
        st.plotly_chart(map_fig(ind, meth, layer, size_by, region, foc, is_m()), config=cfg(f"peta_{ind}_{_lay}_petadasar", zoom=True), **KW)
        st.markdown("<div style='height:2.8rem'></div>", unsafe_allow_html=True)
    st.caption("Unduh: klik ikon kamera di pojok kanan atas peta untuk menyimpan PNG beresolusi tinggi. ")
    keys = [MAPKEY[ind], "batas"] + (["pend_k"] if layer != "Klaster LISA (Moran)" else []) + (["miskin_k"] if layer == "Simbol proporsional" and size_by == "jml_miskin" and ind != "persen_miskin" else [])
    sat = {"Choropleth": f"{unit_i} (warna menurut 5 kelas)", "Simbol proporsional": f"{unit_i} (warna) dan jiwa (luas lingkaran)", "Klaster LISA (Moran)": "klaster LISA (kategori)"}[layer]
    cap(f"{lab_i} menurut kabupaten/kota ({'klaster LISA' if layer.startswith('Klaster') else layer.lower()})", sat, "Kelas dihitung dari seluruh kab/kota Indonesia sehingga warna sebanding antar wilayah", keys)
    arah_pal = "YlOrBr (kuning→cokelat): nilai tinggi = kondisi buruk, sehingga warna tergelap menandai daerah bermasalah" if ind == "persen_miskin" else "YlGnBu (kuning→biru tua): nilai tinggi = kondisi baik"
    if layer == "Choropleth":
        read(f"Warna menunjukkan kelas {lab_i} ({arah}); kelas pertama di legenda adalah nilai terkecil. Daerah yang tidak berwarna belum punya poligon atau data. Arahkan kursor untuk melihat nilai dan jumlah penduduknya.")
    elif layer == "Simbol proporsional":
        read(f"Luas lingkaran menunjukkan {'jumlah penduduk miskin (persentase kali jumlah penduduk)' if size_by == 'jml_miskin' else 'jumlah penduduk'}, warnanya menunjukkan {lab_i} ({arah}). Lingkaran besar yang berwarna gelap adalah tempat banyak orang terdampak.")
        why("Choropleth memperlihatkan seberapa buruk persentasenya, sedangkan simbol proporsional memperlihatkan berapa banyak orang yang terdampak. Luas lingkaran, bukan jari-jarinya, dibuat sebanding dengan jumlah agar ukuran tidak terkesan berlebihan.")
    else:
        I, p, ld = moran(ind); cnt = (ld[ld.region == region] if region != "Indonesia" else ld).klaster.value_counts()
        read(f"Warna menunjukkan jenis klaster. Tinggi-tinggi berarti daerah bernilai tinggi dan tetangganya juga tinggi; rendah-rendah kebalikannya; tinggi-rendah dan rendah-tinggi adalah daerah yang berbeda dari sekitarnya; abu-abu berarti polanya tidak cukup kuat (α = 0,05). Untuk {lab_i}, nilai tinggi berarti {'kondisi buruk' if dir_i == -1 else 'kondisi baik'}.")
        insight(f"Indeks Moran untuk {lab_i} sebesar {I:.2f} (p = {p:.3f}). " + ("Nilainya positif dan signifikan, artinya daerah yang bertetangga cenderung punya nilai yang mirip. " if I > 0 and p < .05 else "Tidak ada bukti kuat bahwa daerah yang bertetangga bernilai mirip. ") + f"Di {region} tercatat " + ", ".join(f"{v} daerah {k.lower()}" for k, v in cnt.items()) + ". Tetangga yang dipakai adalah enam daerah terdekat dari titik pusat tiap daerah.")
    gm = (gd[ind] * gd.jumlah_penduduk).sum() / gd.jumlah_penduduk.sum(); mu = gd[ind].mean(); bad_high = ind == "persen_miskin"; worst = lab[-1] if bad_high else lab[0]
    wg = gd[gd.kelas == worst]; lebih_baik = (gm > mu) == (dir_i == 1)
    tb = gd.groupby("kelas", observed=True).agg(**{"Kab/kota": ("code", "count"), "Penduduk (juta)": ("jumlah_penduduk", lambda s: s.sum() / 1e6)}); tb["% penduduk"] = tb["Penduduk (juta)"] / tb["Penduduk (juta)"].sum() * 100; tb = tb.round(1); tb.index.name = f"Kelas {lab_i} ({unit_i})"
    def konsentrasi(sub, base):
        d = pd.DataFrame({"k": sub.prov_code.value_counts(), "n": base.prov_code.value_counts()}).dropna(); d = d[d.n >= (5 if region == "Indonesia" else 3)]; d["p"] = d.k / d.n
        return ", ".join(f"{provname.get(i, i)} ({int(r.k)} dari {int(r.n)} kab/kota)" for i, r in d.sort_values(["p", "k"], ascending=False).head(3).iterrows()) or "—"
    c_a, c_b = st.columns([1, 1.2])
    with c_a: table(tb)
    with c_b: insight(f"Di {region}, kelas terburuk untuk {lab_i} ({worst} {unit_i}) dihuni {len(wg)} kab/kota, sekitar {wg.jumlah_penduduk.sum()/1e6:.1f} juta jiwa atau {wg.jumlah_penduduk.sum()/max(gd.jumlah_penduduk.sum(), 1)*100:.0f}% penduduk wilayah ini. Daerah-daerah itu paling terkonsentrasi di {konsentrasi(wg, gd)}. Rata-rata yang ditimbang jumlah penduduk ({gm:.1f}) {'lebih tinggi' if gm > mu else 'lebih rendah'} dari rata-rata biasa ({mu:.1f}), artinya penduduk rata-rata tinggal di daerah yang kondisinya {'lebih baik' if lebih_baik else 'lebih buruk'} dari daerah rata-rata.")
    best = gdat.nlargest(3, ind) if dir_i == 1 else gdat.nsmallest(3, ind); bad = gdat.nsmallest(3, ind) if dir_i == 1 else gdat.nlargest(3, ind)
    n10 = max(int(len(gdat) * .1), 1); w10 = gdat.nsmallest(n10, ind) if dir_i == 1 else gdat.nlargest(n10, ind); fmt = lambda d: ", ".join(f"{n} ({v:.1f})" for n, v in zip(d.kabkota, d[ind]))
    insight(f"Selisih antara daerah terbaik dan terburuk di {region} mencapai {gdat[ind].max()-gdat[ind].min():.1f} {'poin persen' if unit_i == '%' else unit_i}. Terbaik: {fmt(best)}. Terburuk: {fmt(bad)}. Dari {n10} kab/kota terbawah (10%), porsi terbesar ada di {konsentrasi(w10, gdat)}.")
    st.markdown("#### Kenapa kuantil, bukan natural breaks?")
    e1, e2 = edges(ind, "Kuantil"), edges(ind, "Natural breaks"); sd = geo.dropna(subset=["lat", ind])[ind]
    fh = go.Figure(go.Histogram(x=sd, nbinsx=40, marker_color="#9fb8b3", name="Jumlah daerah", hovertemplate="%{x}: %{y} daerah<extra></extra>"))
    for e_, nm_, c_, dsh in [(e1, "Batas kuantil", "#0072B2", "dash"), (e2, "Batas natural breaks", "#D55E00", "dot")]:
        for b_ in e_[1:-1]: fh.add_vline(x=b_, line=dict(color=c_, dash=dsh, width=2))
        fh.add_trace(go.Scatter(x=[None], y=[None], mode="lines", line=dict(color=c_, dash=dsh, width=2), name=nm_))
    fh.update_layout(xaxis_title=f"{lab_i} ({unit_i})", yaxis_title="Jumlah kab/kota", legend=dict(x=1.02, y=1, xanchor="left")); show(fh, 380, keys=[MAPKEY[ind]], lock=True, leg=True, fname=f"sebaran_kelas_{ind}")
    cap(f"Sebaran {lab_i} kabupaten/kota dan batas kelas peta", "jumlah kab/kota (tinggi batang)", "Garis putus-putus = batas kelas kuantil, garis titik = batas natural breaks; seluruh Indonesia", [MAPKEY[ind]])
    cn = pd.cut(sd, e2, include_lowest=True).value_counts(sort=False); big = int(cn.max())
    insight(f"Median {sd.median():.1f} dan rata-rata {sd.mean():.1f} {unit_i}, {'jadi ada sebagian daerah bernilai sangat tinggi yang menarik rata-rata ke atas' if sd.mean() > sd.median() * 1.02 else 'jadi ada sebagian daerah bernilai sangat rendah yang menarik rata-rata ke bawah' if sd.mean() < sd.median() * .98 else 'sebarannya cukup simetris'}. Kuantil membagi tiap kelas sekitar {len(sd)//5} daerah, sedangkan natural breaks menghasilkan {', '.join(str(int(x)) for x in cn)}; kelas terbesarnya memuat {big} dari {len(sd)} daerah ({big/len(sd)*100:.0f}%). Semakin timpang jumlah per kelas, semakin berbeda hasil kedua metode.")
    st.markdown("#### Rentang di dalam provinsi")
    rows = []
    for pc, g_ in gdat.groupby("prov_code"):
        lo, hi = g_.loc[g_[ind].idxmin()], g_.loc[g_[ind].idxmax()]; rows.append(dict(prov=provname.get(pc, str(pc)), lo=lo[ind], hi=hi[ind], lo_n=lo.kabkota, hi_n=hi.kabkota, gap=hi[ind] - lo[ind], n=len(g_)))
    pg = pd.DataFrame(rows).query("n >= 3").sort_values("gap").tail(12)
    if len(pg):
        lo_c, hi_c = ("#D55E00", "#0072B2") if dir_i == 1 else ("#0072B2", "#D55E00"); pad = (pg.hi.max() - pg.lo.min()) * .09
        fg = go.Figure(go.Bar(y=pg.prov, x=pg.gap, base=pg.lo, orientation="h", width=.62, marker=dict(color=pg.gap, colorscale=[[0, "#2a9d8f"], [1, "#0b3b36"]]), text=[f"Δ {g:.1f}" for g in pg.gap], textposition="inside", insidetextanchor="middle", textfont=dict(color="white", size=12),
            customdata=np.c_[pg.lo_n, pg.lo, pg.hi_n, pg.hi, pg.gap], hovertemplate="<b>%{y}</b><br>Terendah: %{customdata[0]} (%{customdata[1]:.1f})<br>Tertinggi: %{customdata[2]} (%{customdata[3]:.1f})<br>Selisih: %{customdata[4]:.1f} " + unit_i + "<extra></extra>"))
        for vals, c_, pos in [(pg.lo, lo_c, "middle left"), (pg.hi, hi_c, "middle right")]: fg.add_trace(go.Scatter(x=vals, y=pg.prov, mode="text", text=[f"<b>{v:.1f}</b>" for v in vals], textposition=pos, textfont=dict(size=12, color=c_), hoverinfo="skip", showlegend=False, cliponaxis=False))
        fg.update_layout(showlegend=False, margin=dict(t=10), xaxis=dict(title=f"{lab_i} ({unit_i})", range=[pg.lo.min() - pad, pg.hi.max() + pad], gridcolor="#e6e0d2"), yaxis=dict(automargin=True, categoryorder="array", categoryarray=list(pg.prov))); show(fg, 460, keys=[MAPKEY[ind], "batas"], lock=True, fname=f"rentang_provinsi_{ind}"); dl(pg.drop(columns=["n"]), "Unduh data rentang (CSV)", f"rentang_provinsi_{ind}")
        cap(f"Rentang {lab_i} di dalam provinsi ({region})", unit_i, "Hanya provinsi dengan ≥ 3 kab/kota; maksimal 12 provinsi dengan selisih terbesar", [MAPKEY[ind], "batas"])
        read(f"Satu batang mewakili satu provinsi, dari kab/kota dengan {lab_i} terendah (angka kiri) ke tertinggi (angka kanan); Δ adalah selisihnya. Makin panjang dan gelap batangnya, makin timpang provinsi itu. Angka oranye menandai kondisi terburuk dan biru kondisi terbaik.")
        t = pg.iloc[-1]; insight(f"Provinsi paling timpang di {region} adalah {t.prov}: {t.lo_n} ({t.lo:.1f}) dan {t.hi_n} ({t.hi:.1f}) terpaut {t.gap:.1f} {unit_i}. Rata-rata provinsi tidak memperlihatkan perbedaan sebesar ini.")
    else: st.info("Wilayah ini tidak punya provinsi dengan ≥ 3 kab/kota bernilai.")
    tanpa = geo[geo.lat.isna()].kabkota.tolist()
    st.caption(f"Peta menampilkan {int(geo.lat.notna().sum())} dari {len(geo)} kab/kota. " + (f"{len(tanpa)} daerah belum tergambar karena belum ada poligonnya ({', '.join(tanpa)}); " if tanpa else "") + f"{int(geo.sanitasi_layak.isna().sum())} daerah tanpa data sanitasi.")
    teaser(2, "bab2", "Pola antarprovinsi", "peta menunjukkan <i>di mana</i> kesenjangan terjadi. Bab berikut bertanya <i>mengapa</i>: indikator apa yang membedakan provinsi.")
bab1()

# ============ BAB 2 ============
@st.cache_data(show_spinner="Menghitung PCA & klaster…")
def analyze(k):
    m = mv0.copy(); Z = StandardScaler().fit_transform(m[VARS]); pca = PCA(2).fit(Z); sc = pca.transform(Z); cl = KMeans(k, n_init=10, random_state=1).fit_predict(Z)
    m["indeks"] = (Z * DIRS).mean(1); order = m.groupby(cl).indeks.mean().sort_values(ascending=False).index.tolist(); rk = {c: i for i, c in enumerate(order)}
    m["kid"] = [rk[c] for c in cl]; m["klaster"] = [f"K{rk[c]+1} · indeks {m.indeks[cl == c].mean():+.2f}" for c in cl]; m["PC1"], m["PC2"] = sc[:, 0], sc[:, 1]
    m["md2"] = np.einsum("ij,jk,ik->i", Z, np.linalg.pinv(np.cov(Z.T)), Z); m["pencilan"] = m.md2 > chi2.ppf(.975, len(VARS))   # jarak Mahalanobis² (memperhitungkan korelasi antarindikator)
    return m, Z, pca.components_, pca.explained_variance_ratio_, leaves_list(linkage(Z, "ward")), leaves_list(linkage(Z.T, "ward"))

@fragment
def bab2():
    chapter(2, "Data berdimensi tinggi", "Provinsi mana yang ‘mirip’, dan mana yang menyimpang?", "Sepuluh indikator diringkas jadi dua sumbu lewat PCA lalu dikelompokkan. <b>Pilih titik di biplot dengan kotak/lasso</b> (atau pilih provinsi manual): provinsi yang sama menyala di parallel coordinates di sampingnya, juga di heatmap dan radar (brushing &amp; linking).", "bab2")
    a1, a2, a3 = st.columns([1, 1, 2]); k = a1.slider("Jumlah klaster (K-Means)", 2, 5, 3); arrows = a2.checkbox("Panah & label variabel", value=not is_m()); mv, Z, comp, evr, ro, co = analyze(k)
    extra = a3.multiselect("Pilih provinsi manual (opsional)", mv.provinsi); cats = sorted(mv.klaster.unique(), key=lambda s: int(s[1]))
    Lc, Rc = st.columns(2)
    with Lc:
        st.markdown("**① Biplot PCA** — tarik kotak/lasso untuk memilih")
        fb = px.scatter(mv, x="PC1", y="PC2", color="klaster", custom_data=["provinsi"], hover_name="provinsi", category_orders={"klaster": cats}, color_discrete_sequence=OKABE, hover_data={"PC1": ":.2f", "PC2": ":.2f", "klaster": False}); fb.update_traces(marker=dict(size=12, line=dict(width=1, color="white")))
        po = mv[mv.pencilan]
        if len(po): fb.add_trace(go.Scatter(x=po.PC1, y=po.PC2, mode="markers", name="Pencilan (Mahalanobis)", marker=dict(symbol="diamond-open", size=22, line=dict(width=2, color=INK)), customdata=po[["provinsi"]].values, hoverinfo="skip"))
        if extra: ex = mv[mv.provinsi.isin(extra)]; fb.add_trace(go.Scatter(x=ex.PC1, y=ex.PC2, mode="markers", name="Dipilih manual", marker=dict(symbol="circle-open", size=22, line=dict(width=3, color="#D55E00")), customdata=ex[["provinsi"]].values, hoverinfo="skip"))
        if arrows:
            Ld = comp.T; sc_ = 0.8 * min(mv.PC1.abs().max(), mv.PC2.abs().max()) / np.linalg.norm(Ld, axis=1).max()
            for v, (x, y) in zip(VARS, Ld * sc_):
                fb.add_annotation(x=x, y=y, ax=0, ay=0, xref="x", yref="y", axref="x", ayref="y", showarrow=True, text="", arrowhead=2, arrowwidth=1.5, arrowcolor="#6b7a77")
                fb.add_annotation(x=x, y=y, xref="x", yref="y", showarrow=False, text=f"<b>{flat(SHORT[v])}</b>", font=dict(size=11, color=INK), bgcolor="rgba(255,255,255,.8)", xanchor="left" if x >= 0 else "right", yanchor="bottom" if y >= 0 else "top")
        fb.update_layout(margin=dict(t=20), legend=dict(x=1.02, y=1, xanchor="left", title=""), dragmode=False if is_m() else "lasso", xaxis_title=f"PC1 ({evr[0]*100:.0f}% varians)", yaxis_title=f"PC2 ({evr[1]*100:.0f}% varians)")
        ev = show(fb, 460 if is_m() else 560, keys=MV, key="pca", leg=True, fname="biplot_pca", on_select="rerun", selection_mode=("points", "box", "lasso"))
    sel = sorted(({p["customdata"][0] for p in ev.selection.points if p.get("customdata")} if ev and ev.selection.points else set()) | set(extra))
    with Rc:
        st.markdown("**② Parallel coordinates** — garis oranye = provinsi terpilih")
        col = np.where(mv.provinsi.isin(sel), 1, 0) if sel else mv.kid + .5
        cs = [[0, "#c9ced3"], [1, "#D55E00"]] if sel else sum([[[i / k, OKABE[i]], [(i + 1) / k, OKABE[i]]] for i in range(k)], [])
        fp = go.Figure(go.Parcoords(line=dict(color=col, colorscale=cs, cmin=0, cmax=1 if sel else k), labelangle=-45 if is_m() else -35, labelside="top", labelfont=dict(size=10), tickfont=dict(size=9), dimensions=[dict(label=SHORT[v], values=mv[v]) for v in VARS]))
        fp.update_layout(margin=dict(l=26 if is_m() else 40, r=34 if is_m() else 40, t=110, b=20)); show(fp, 500 if is_m() else 560, keys=MV, fname="parallel_coordinates")
    if sel: st.success(f"{len(sel)} provinsi terpilih: " + ", ".join(sel))
    else: st.caption("Belum ada seleksi — tarik kotak/lasso pada biplot atau pilih provinsi manual untuk menyorotnya di semua tampilan. Seret pada sumbu parallel coordinates untuk menyaring di tampilan itu saja.")
    cap("Biplot PCA dan parallel coordinates 38 provinsi", f"skor komponen utama (biplot); satuan asli tiap indikator (sumbu parallel coordinates)", "Data distandarkan (z-score) sebelum PCA dan K-Means; warna = klaster; ◇ = pencilan Mahalanobis", MV)
    t = pd.Series(comp[0], index=VARS).abs().sort_values(ascending=False).head(3).index
    read(f"Titik yang berdekatan menggambarkan provinsi dengan profil mirip, dan warna menunjukkan klasternya. Panah menunjuk arah naiknya indikator. Sumbu PC1 ({evr[0]*100:.0f}% varians) terutama dibentuk oleh {', '.join(LAB[v][0].lower() for v in t)}. Di parallel coordinates, tiap garis adalah satu provinsi; garis yang menjulang ke ujung banyak sumbu menandai provinsi ekstrem. Pada sumbu miskin, kesakitan, dan merokok, makin tinggi berarti makin buruk.")
    if sel:
        ms = mv.provinsi.isin(sel).values; zs = pd.Series((Z * DIRS)[ms].mean(0), index=VARS).sort_values(); kl = mv[ms].klaster.str[:2].value_counts()
        insight(f"{len(sel)} provinsi yang Anda pilih ({', '.join(sel[:6])}{' dan lainnya' if len(sel) > 6 else ''}) punya indeks gabungan rata-rata {mv.indeks[ms].mean():+.2f}, sedangkan rata-rata nasional 0. Mereka tersebar di klaster {', '.join(f'{a} ({b})' for a, b in kl.items())}. Dibanding provinsi lain, kelebihan terbesarnya ada pada {fz(zs.index[-1], True)} ({zs.iloc[-1]:+.1f} simpangan baku) dan kekurangan terbesarnya pada {fz(zs.index[0], False)} ({zs.iloc[0]:+.1f}).")
    zd = pd.DataFrame(Z * DIRS, columns=VARS).groupby(mv.kid.values).mean(); rows = []
    for c in zd.index:
        s = zd.loc[c].sort_values(); mem = mv[mv.kid == c].provinsi.tolist()
        rows.append({"Klaster": cats[c], "n": len(mem), "Unggul pada": ", ".join(LAB[v][0] for v in s.index[::-1][:2]), "Lemah pada": ", ".join(LAB[v][0] for v in s.index[:2]), "Anggota": ", ".join(mem)})
    table(pd.DataFrame(rows).set_index("Klaster"))
    dl(mv[["provinsi", "klaster", "PC1", "PC2", "indeks", "pencilan"] + VARS], "Unduh data multivariat (CSV)", "data_multivariat_provinsi")
    def ekstrem(i): z = Z[i]; o = np.argsort(-np.abs(z))[:2]; return ", ".join(f"{LAB[VARS[j]][0].lower()} {'sangat tinggi' if z[j] > 0 else 'sangat rendah'}" for j in o)
    det = "; ".join(f"{mv.provinsi[i]} ({ekstrem(i)})" for i in np.where(mv.pencilan)[0]); r = lambda a, b: mv[a].corr(mv[b])
    wc = Counter(mv.provinsi.values[np.argmin(Z * DIRS, axis=0)]).most_common(2); cvs = mv[VARS].std() / mv[VARS].mean()
    insight(f"{mv.loc[mv.indeks.idxmax(), 'provinsi']} punya indeks gabungan tertinggi dan {mv.loc[mv.indeks.idxmin(), 'provinsi']} yang terendah. K1 adalah kelompok dengan profil terbaik, K{k} yang paling lemah. " + (f"Provinsi yang tergolong pencilan: {det}. " if det else "Tidak ada provinsi yang tergolong pencilan. ") + f"{wc[0][0]} paling buruk pada {wc[0][1]} dari {len(VARS)} indikator, disusul {wc[1][0]} ({wc[1][1]}). Indikator yang paling beragam antarprovinsi adalah {LAB[cvs.drop('uhh').idxmax()][0].lower()}, sedangkan UHH sebarannya relatif sempit (koefisien variasi {cvs.uhh*100:.1f}%) tetapi tetap terpaut {mv.uhh.max()-mv.uhh.min():.1f} tahun. UHH berkorelasi dengan kemiskinan (r = {r('uhh','persen_miskin'):.2f}), sanitasi (r = {r('uhh','sanitasi_layak'):.2f}), dan lama sekolah (r = {r('uhh','rls'):.2f}); ini hubungan, bukan bukti sebab-akibat.")
    view = st.radio("Tampilan tambahan", ["Heatmap terklaster", "Radar perbandingan"], horizontal=True)
    if view == "Heatmap terklaster":
        Zo = Z[ro][:, co]; nm = mv.provinsi.values[ro]; ms = np.isin(nm, sel); xl = [flat(SHORT[VARS[j]]) for j in co]
        fh = go.Figure(go.Heatmap(z=Zo, x=xl, y=nm, colorscale="RdBu", zmid=0, opacity=.3 if sel else 1, colorbar=dict(title="z-score"), hovertemplate="%{y}<br>%{x}: z=%{z:.2f}<extra></extra>"))
        if sel: fh.add_trace(go.Heatmap(z=np.where(ms[:, None], Zo, np.nan), x=xl, y=nm, colorscale="RdBu", zmid=0, showscale=False, hoverinfo="skip"))
        for i in np.where(ms)[0]: fh.add_shape(type="rect", xref="paper", x0=0, x1=1, yref="y", y0=i - .5, y1=i + .5, line=dict(color="#D55E00", width=2))
        fh.update_yaxes(tickmode="array", tickvals=nm, ticktext=[f"<span style='color:#D55E00'><b>▶ {n}</b></span>" if m else n for n, m in zip(nm, ms)], autorange="reversed", tickfont=dict(size=10)); fh.update_xaxes(tickangle=-35, side="top")
        fh.update_layout(margin=dict(l=10, r=10, t=90, b=10)); show(fh, 840, keys=MV, lock=True, fname="heatmap_terklaster")
        cap("Heatmap terklaster z-score 38 provinsi × 10 indikator", "z-score (simpangan baku dari rata-rata antarprovinsi)", "Baris dan kolom diurut klaster hierarkis (Ward); provinsi terpilih diberi bingkai oranye, lainnya dipudarkan", MV)
        cm = mv[VARS].corr().abs().where(np.triu(np.ones((10, 10), bool), 1)).stack().sort_values(ascending=False).head(3)
        read("Biru berarti di atas rata-rata antarprovinsi dan merah di bawahnya, tanpa melihat apakah itu baik atau buruk. Baris yang berdekatan adalah provinsi yang mirip, kolom yang berdekatan adalah indikator yang bergerak bersama.")
        insight("Pasangan indikator yang paling erat hubungannya: " + "; ".join(f"{LAB[a][0].lower()} dengan {LAB[b][0].lower()} (|r| = {v:.2f})" for (a, b), v in cm.items()) + ". Blok warna yang seragam sepanjang satu baris menandai kelompok provinsi berprofil serupa, sedangkan baris di ujung heatmap adalah provinsi yang paling berbeda dari yang lain.")
    else:
        d = sel[:4] if sel else [mv.loc[mv.indeks.idxmax(), "provinsi"], mv.loc[mv.indeks.idxmin(), "provinsi"]]
        pick = st.multiselect("Provinsi untuk radar (maks. 4)", mv.provinsi, default=d, max_selections=4); mm = (mv[VARS] - mv[VARS].min()) / (mv[VARS].max() - mv[VARS].min()) * 100
        for v in VARS:
            if LAB[v][2] == -1: mm[v] = 100 - mm[v]
        fr = go.Figure()
        for i, p in enumerate(pick):
            vals = mm[mv.provinsi == p].iloc[0].tolist(); th = [flat(SHORT[v]) for v in VARS]; fr.add_trace(go.Scatterpolar(r=vals + vals[:1], theta=th + th[:1], name=p, fill="toself", opacity=.55, line_color=OKABE[i]))
        fr.update_layout(polar=dict(radialaxis=dict(range=[0, 100])), title="Skor 0–100 (makin keluar = makin baik)"); show(fr, 520, keys=MV, lock=True, leg=True, fname="radar_provinsi")
        cap("Radar perbandingan provinsi", "skor 0–100 (min–max antarprovinsi)", "Indikator ‘buruk’ dibalik sehingga luas bidang lebih besar selalu berarti kondisi lebih baik", MV)
        read("Makin jauh sebuah sudut dari pusat, makin baik provinsi itu pada indikator tersebut dibanding provinsi lain.")
        for p in pick: s = mm[mv.provinsi == p].iloc[0]; st.markdown(f"- **{p}**: rata-rata skor {s.mean():.0f}; terkuat pada *{LAB[s.idxmax()][0]}* ({s.max():.0f}), terlemah pada *{LAB[s.idxmin()][0]}* ({s.min():.0f}).")
    teaser(3, "bab3", "Arus impor kesehatan", "kesehatan juga bergantung pada alat dan obat. Bab berikut menelusuri struktur impor produk kesehatan Indonesia.")
bab2()

# ============ BAB 3 ============
@st.cache_resource(show_spinner=False)
def nodes():
    h = hir.rename(columns={"Kode 3 Digit": "kode", "1 Digit (Kategori Utama)": "L1", "2 Digit (Sub-Kategori)": "L2", "3 Digit (Detail Komoditas)": "L3", "CIF 2025 (USD)": "c25", "CIF 2024 (USD)": "c24", "Berat 2025 (kg)": "w25"})
    S1 = {"Chemicals and related products, n.e.s.": "Kimia & Farmasi", "Miscellaneous manufactured articles": "Barang Manufaktur Lain", "Machinery and transport equipment": "Mesin & Peralatan"}
    S2 = {"Medicinal and pharmaceutical products": "Produk Medis & Farmasi", "Electrical machinery, apparatus and appliances, n.e.s., and electrical parts thereof": "Mesin & Aparat Listrik", "Professional, scientific and controlling instruments and apparatus, n.e.s.": "Instrumen Ilmiah & Ukur"}
    S3 = {541: "Bahan Medis & Farmasi", 542: "Obat-obatan", 871: "Instrumen Optik", 872: "Instrumen & Alat Medis", 873: "Meter & Pencacah", 874: "Instrumen Ukur & Kontrol", 774: "Alat Listrik Medis & Radiologi"}
    h["L1"] = h.L1.map(S1).fillna(h.L1); h["L2"] = h.L2.map(S2).fillna(h.L2); h["L3"] = [f"{S3.get(c, l)} ({c})" for c, l in zip(h.kode, h.L3)]
    R = "Impor Kesehatan"; rows = [dict(id=R, parent="", label=R, c25=h.c25.sum(), c24=h.c24.sum(), w25=h.w25.sum(), lv=0)]
    for lv, keys in enumerate([["L1"], ["L1", "L2"], ["L1", "L2", "L3"]], 1):
        for key, g in h.groupby(keys, sort=False):
            key = (key,) if isinstance(key, str) else key
            rows.append(dict(id=" / ".join((R,) + key), parent=" / ".join((R,) + key[:-1]), label=key[-1], c25=g.c25.sum(), c24=g.c24.sum(), w25=g.w25.sum(), lv=lv))
    nd = pd.DataFrame(rows); nd["growth"] = (nd.c25 / nd.c24 - 1) * 100; nd["perkg"] = nd.c25 / nd.w25; return h, nd, R
h, nd, ROOT = nodes()
def _go(a, b): st.session_state["s1"], st.session_state["s2"] = a, b

@fragment
def bab3():
    chapter(3, "Data hierarki", "Ke mana uang impor kesehatan pergi?", "Indonesia masih mengimpor banyak obat dan alat kesehatan. Telusuri struktur SITC dari kelompok besar sampai komoditas: <b>ukuran = nilai impor (CIF 2025)</b>, <b>warna = pertumbuhan 2025 vs 2024</b>. Masuk ke dalam kelompok lewat dropdown, keluar lewat tombol breadcrumb.", "bab3")
    c = st.columns(2); s1 = c[0].selectbox("Level 1 — kelompok", ["(semua)"] + list(h.L1.unique()), key="s1"); o2 = ["(semua)"] + (list(h[h.L1 == s1].L2.unique()) if s1 != "(semua)" else [])
    if st.session_state.get("s2") not in o2: st.session_state["s2"] = "(semua)"
    s2 = c[1].selectbox("Level 2 — sub-kelompok", o2, key="s2"); path = [ROOT] + [x for x in (s1, s2) if x != "(semua)"]; nid = " / ".join(path)
    bc = st.columns([1.3, 1.5, 1.5, 3]); st.markdown("<span class='crumb'>Posisi: " + " › ".join(path) + "</span>", unsafe_allow_html=True)
    bc[0].button("" + ROOT, on_click=_go, args=("(semua)", "(semua)"), key="b0", disabled=len(path) == 1)
    if s1 != "(semua)": bc[1].button("← " + s1, on_click=_go, args=(s1, "(semua)"), key="b1", disabled=s2 == "(semua)")
    view = st.radio("Representasi", ["Treemap", "Sunburst", "Icicle"], horizontal=True); m_ = max(abs(nd.growth).max(), 1)
    com = dict(ids=nd.id, labels=nd.label, parents=nd.parent, values=nd.c25, branchvalues="total", level=nid, customdata=np.c_[nd.c25 / 1e6, nd.growth, nd.perkg],
               marker=dict(colors=nd.growth, colorscale="RdBu", cmid=0, cmin=-m_, cmax=m_, colorbar=dict(title="Pertumbuhan<br>2025 vs 2024 (%)")),
               hovertemplate="<b>%{label}</b><br>Nilai impor: US$ %{customdata[0]:,.0f} juta<br>Pertumbuhan: %{customdata[1]:.1f}%<br>Nilai per kg: US$ %{customdata[2]:,.1f}<extra></extra>")
    if is_m(): com["marker"]["colorbar"] = dict(orientation="h", y=-0.02, yanchor="top", x=0.5, len=.9, thickness=10, title=dict(text="Pertumbuhan 2025 vs 2024 (%)", side="top"))
    fig = go.Figure({"Treemap": go.Treemap(**com, pathbar=dict(visible=False), textinfo="label+percent root"), "Sunburst": go.Sunburst(**com, textinfo="label"), "Icicle": go.Icicle(**com, tiling=dict(orientation="v"))}[view]); fig.update_layout(margin=dict(b=100 if is_m() else 10)); show(fig, 480 if is_m() else 540, keys=["hir"], fname=f"impor_kesehatan_{view.lower()}")
    cap(f"Struktur impor produk kesehatan menurut SITC ({view.lower()})", "US$ (ukuran = nilai CIF 2025); persen (warna = pertumbuhan 2025 vs 2024)", "Hierarki: total → kelompok (1 digit) → sub-kelompok (2 digit) → komoditas (3 digit). Pertumbuhan tiap tingkat dihitung dari nilai yang dijumlahkan, bukan rata-rata di bawahnya", ["hir"])
    read("Luas kotak atau irisan menunjukkan nilai impor, warnanya menunjukkan pertumbuhan: biru berarti naik, merah turun, putih tidak berubah (skala simetris di titik 0). Pilih kelompok lewat dropdown atau tombol di atas; klik pada grafik hanya memperbesar sementara dan tidak mengubah ringkasan di bawahnya.")
    n = nd[nd.id == nid].iloc[0]; ch = nd[nd.parent == nid].sort_values("c25", ascending=False); tot = nd.c25.iloc[0]
    txt = f"{n.label} bernilai US$ {n.c25/1e9:.2f} miliar, atau {n.c25/tot*100:.0f}% dari seluruh impor kesehatan, dan {'naik' if n.growth >= 0 else 'turun'} {abs(n.growth):.1f}% dibanding 2024, dengan harga rata-rata US$ {n.perkg:,.0f} per kg."
    if len(ch) == 1: txt += f" Isinya hanya satu: {ch.iloc[0].label}."
    elif len(ch): txt += f" Isi terbesarnya adalah {ch.iloc[0].label} ({ch.iloc[0].c25/n.c25*100:.0f}% dari kelompok ini), sedangkan yang tumbuh paling cepat adalah {ch.sort_values('growth').iloc[-1].label} ({ch.growth.max():+.1f}%)."
    insight(txt); lf = nd[nd.lv == 3].sort_values("c25", ascending=False); fast = lf.sort_values("growth").iloc[-1]; mahal = lf.sort_values("perkg").iloc[-1]
    insight(f"Komoditas impor kesehatan terbesar adalah {lf.iloc[0].label} (US$ {lf.iloc[0].c25/1e9:.2f} miliar, {lf.iloc[0].c25/tot*100:.0f}% dari total), yang tumbuh paling cepat {fast.label} ({fast.growth:+.1f}%), dan yang paling mahal per kilogram {mahal.label} (US$ {mahal.perkg:,.0f}). Secara keseluruhan impor {'naik' if nd.growth.iloc[0] >= 0 else 'turun'} {abs(nd.growth.iloc[0]):.1f}%. Harga per kilogram yang tinggi pada instrumen dan alat medis menunjukkan barang berteknologi tinggi yang masih diimpor, jadi di sanalah ruang terbesar untuk substitusi impor.")
    st.markdown("#### Daftar komoditas 3 digit (bisa diurutkan)")
    table(lf[["label", "c25", "c24", "growth", "perkg"]].rename(columns={"label": "Komoditas", "c25": "CIF 2025 (US$)", "c24": "CIF 2024 (US$)", "growth": "Pertumbuhan (%)", "perkg": "US$ per kg"}).round(1).set_index("Komoditas"))
    teaser(4, "bab4", "Cek daerahmu", "setelah melihat gambaran besar, saatnya melihat posisi daerah Anda sendiri.")
bab3()

# ============ BAB 4 ============
LISA_ARTI = {"Tinggi-tinggi": "daerah ini <b>dan tetangganya</b> sama-sama bernilai tinggi", "Rendah-rendah": "daerah ini <b>dan tetangganya</b> sama-sama bernilai rendah",
             "Tinggi-rendah": "daerah ini bernilai tinggi tetapi <b>dikelilingi tetangga bernilai rendah</b>", "Rendah-tinggi": "daerah ini bernilai rendah tetapi <b>dikelilingi tetangga bernilai tinggi</b>",
             "Tidak signifikan": "<b>tidak ada pola pengelompokan</b> yang cukup kuat secara statistik (α = 0,05)"}

@fragment
def bab4():
    chapter(4, "Profil daerah", "Cek daerahmu", "Pilih satu kabupaten/kota untuk melihat posisinya pada tiga indikator kesehatan: peringkat nasional, selisih dari rata-rata, peringkat di provinsinya, dan apakah daerah sekitarnya ikut berkondisi serupa (klaster LISA).", "bab4")
    d0 = geo.dropna(subset=["lat"]).sort_values(["prov_code", "kabkota"]); lb = {r.code: f"{r.kabkota} — {provname.get(r.prov_code, '')}" for r in d0.itertuples()}
    sb = d0[d0.kabkota.str.contains("Surabaya")]; code = st.selectbox("Kabupaten/kota", list(lb), format_func=lb.get, index=list(lb).index(sb.code.iloc[0]) if len(sb) else 0, key="cek")
    r = geo[geo.code == code].iloc[0]; kab = r.kabkota; prov = provname.get(r.prov_code, ""); html = []; ring = []; figs = []
    KAL = {"uhh": lambda v, a, b, n: f"Bayi yang lahir di {kab} diharapkan hidup {v:.1f} tahun, {abs(a):.1f} tahun {'lebih lama' if a > 0 else 'lebih singkat'} dari rata-rata nasional ({n:.1f} tahun).",
           "persen_miskin": lambda v, a, b, n: f"{v:.1f}% penduduk {kab} hidup di bawah garis kemiskinan, {abs(a):.1f} poin persen {'di atas' if a > 0 else 'di bawah'} rata-rata nasional ({n:.1f}%).",
           "sanitasi_layak": lambda v, a, b, n: f"{v:.1f}% rumah tangga di {kab} memakai sanitasi layak, {abs(a):.1f} poin persen {'lebih tinggi' if a > 0 else 'lebih rendah'} dari rata-rata nasional ({n:.1f}%)."}
    for ind in INFO:
        lab_i, unit_i, dir_i = LAB[ind]; dd = geo.dropna(subset=[ind]); val = r[ind]; n_all = len(dd)
        if pd.isna(val):
            html.append(f"<div class='pcard'><div class='pt'>{lab_i}</div><div class='pv'>—</div><div class='pnote'>Data {lab_i.lower()} tidak tersedia untuk {kab}.</div></div>"); figs.append(None); continue
        better = (lambda s: (s < val) if dir_i == -1 else (s > val))
        rk = int(better(dd[ind]).sum() + 1) if False else int(((dd[ind] > val) if dir_i == 1 else (dd[ind] < val)).sum() + 1)
        dp = dd[dd.prov_code == r.prov_code]; rp = int(((dp[ind] > val) if dir_i == 1 else (dp[ind] < val)).sum() + 1); nat = wmean(ind); diff = val - nat; bagus = (diff > 0) == (dir_i == 1)
        pct = (n_all - rk) / (n_all - 1) * 100; I, p, ld = moran(ind); lisa = ld[ld.code == code].klaster.iloc[0]; ring.append((lab_i, bagus, pct, rk, n_all))
        arti = LISA_ARTI[lisa] + (" (‘tinggi’ pada kemiskinan berarti kondisi buruk)" if ind == "persen_miskin" and lisa != "Tidak signifikan" else "")
        html.append(f"""<div class='pcard'><div class='pt'>{lab_i}</div><div class='pv'>{val:.1f} <span>{unit_i}</span></div>
<div class='prow'><span>Peringkat nasional</span><b>{rk} dari {n_all}</b></div><div class='prow'><span>Lebih baik dari</span><b>{pct:.0f}% daerah lain</b></div>
<div class='prow'><span>Selisih dari rata-rata nasional</span><b class='{'ok' if bagus else 'bad'}'>{diff:+.1f} {unit_i} · {'lebih baik' if bagus else 'lebih buruk'}</b></div>
<div class='prow'><span>Peringkat di provinsinya</span><b>{rp} dari {len(dp)}</b></div>
<div class='prow'><span>Klaster LISA</span><b class='badge' style='background:{LISA_C[lisa]}'>{lisa}</b></div>
<div class='pnote'>{KAL[ind](val, diff, bagus, nat)}<br><br><i>Klaster LISA:</i> {arti}.</div></div>""")
        lo_, hi_ = dd[ind].min(), dd[ind].max(); pad = (hi_ - lo_) * .04
        fh = go.Figure(go.Histogram(x=dd[ind], nbinsx=30, marker_color="#c9d6d3", hoverinfo="skip")); fh.add_vline(x=val, line=dict(color="#D55E00", width=3))
        fh.add_annotation(x=val, y=1, yref="paper", text=f"<b>{kab}</b>", showarrow=False, yanchor="bottom", xanchor="right" if val > (lo_ + hi_) / 2 else "left", font=dict(color="#D55E00", size=11))
        fh.update_layout(margin=dict(t=40, b=45, l=10, r=10), height=250, paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", yaxis_visible=False, xaxis=dict(title=f"{lab_i} ({unit_i})", range=[lo_ - pad, hi_ + pad], fixedrange=True), yaxis_fixedrange=True, dragmode=False, bargap=.05, font=dict(color=INK, size=11)); figs.append(fh)
    st.markdown("<div class='pgrid'>" + "".join(html) + "</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    for c_, fh in zip(cols, figs):
        if fh is not None: c_.plotly_chart(fh, config=cfg(f"profil_{kab}", True), **KW)
    read("Peringkat 1 berarti kondisi terbaik; untuk kemiskinan, peringkat 1 adalah persentase terendah. Pada histogram, batang abu-abu menunjukkan sebaran seluruh kab/kota dan garis oranye posisi daerah Anda. Klaster LISA menunjukkan apakah daerah dan enam tetangga terdekatnya bernilai serupa: ‘tinggi-tinggi’ pada harapan hidup atau sanitasi berarti kelompok yang kondisinya baik, pada kemiskinan berarti kelompok yang kondisinya buruk.")
    cap(f"Profil {kab} dibanding kab/kota lain", "tahun atau persen sesuai indikator", "Rata-rata nasional ditimbang jumlah penduduk; peringkat dihitung dari daerah yang memiliki data tiap indikator", ["uhh_k", "miskin_k", "san_k", "pend_k"])
    if ring:
        up = [x for x in ring if x[1]]; best_ = max(ring, key=lambda x: x[2]); worst_ = min(ring, key=lambda x: x[2])
        insight(f"{kab} ({prov}, {r.jumlah_penduduk/1e6:.2f} juta jiwa): {len(up)} dari {len(ring)} indikator lebih baik daripada rata-rata nasional. Yang paling menonjol adalah {best_[0].lower()}, lebih baik dari {best_[2]:.0f}% daerah lain (peringkat {best_[3]} dari {best_[4]}); yang paling tertinggal adalah {worst_[0].lower()}, lebih baik dari {worst_[2]:.0f}% daerah lain (peringkat {worst_[3]} dari {worst_[4]}). Peringkat nasional tidak memperlihatkan ketimpangan di dalam daerah itu sendiri.")
bab4()

# ============ PENUTUP ============
st.markdown("<div id='penutup' class='chap'><small>Penutup</small><h2>Kesehatan adalah cerita ketimpangan</h2></div>", unsafe_allow_html=True)
_idx = pd.Series((StandardScaler().fit_transform(mv0[VARS]) * DIRS).mean(1), index=mv0.provinsi); rr = lambda v: mv0.uhh.corr(mv0[v]); lo = ", ".join(_idx.nsmallest(3).index)
cards([("1 · Wilayah", f"{geo.uhh.max()-geo.uhh.min():.1f} tahun", f"selisih UHH antar kab/kota ({geo.uhh.min():.1f}–{geo.uhh.max():.1f}). Rata-rata tertimbang nasional {wmean('uhh'):.1f} tahun. Lihat <a href='#bab1'>Bab 1</a>."),
       ("2 · Pola provinsi", f"r = {rr('sanitasi_layak'):.2f}", f"korelasi UHH dengan sanitasi layak (air minum r = {rr('air_layak'):.2f}; lama sekolah r = {rr('rls'):.2f}). Provinsi berindeks terendah: {lo}. Lihat <a href='#bab2'>Bab 2</a>."),
       ("3 · Impor", f"US${cif_total:.1f} M", f"impor produk kesehatan 2025, naik {nd.growth.iloc[0]:+.1f}% dari 2024. Lihat <a href='#bab3'>Bab 3</a>.")])
st.markdown(f"""### Jadi, siapa yang tertinggal?
<p class='lead'>Di tingkat nasional, rata-rata terlihat baik: harapan hidup {wmean('uhh'):.1f} tahun. Tetapi rata-rata menyembunyikan jurang. Antar kabupaten/kota, harapan hidup terpaut {geo.uhh.max()-geo.uhh.min():.1f} tahun, dan daerah terendah mengelompok secara spasial (lihat klaster LISA di Bab 1).</p>
<p class='lead'>Antar provinsi, harapan hidup berjalan beriringan dengan sanitasi, air minum, dan pendidikan. Itu sebuah asosiasi, bukan bukti sebab-akibat; tetapi artinya intervensi dasar di daerah berindeks terendah ({lo}) kemungkinan paling besar dampaknya.</p>
<p class='lead'>Di hilir, ketergantungan pada impor alat kesehatan bernilai tinggi per kilogram menunjukkan bahwa kesehatan juga soal kemandirian industri, bukan hanya layanan.</p>""", unsafe_allow_html=True)
st.markdown("<div id='metode' class='chap'><small>Lampiran</small><h2>Catatan data dan metodologi</h2></div><p class='lead'>Ringkasan sumber, rumus, dan keputusan pengolahan data yang dipakai di seluruh web story. Klik judul untuk membuka.</p>", unsafe_allow_html=True)
try: box = st.container(key="metode_box")
except TypeError: box = st.container()
with box:
    with st.expander("Sumber data utama (BPS)"):
        st.markdown("Seluruh angka indikator, jumlah penduduk, dan nilai impor berasal dari tabel statistik BPS berikut.")
        table(pd.DataFrame([{"Kode": k, "Judul tabel/publikasi": v[1], "Tahun": v[2] or "-", "URL": v[3] or "[belum diisi]", "Diakses": TGL} for k, v in DS.items() if k != "batas"]))
    with st.expander("Data referensi di luar BPS"):
        st.markdown("- **Batas kabupaten/kota**: berkas GeoJSON kab/kota. Kode Papua lama (sebelum pemekaran 2022) dipetakan ke kode BPS yang baru agar data dan poligon dapat digabung.\n- Data referensi hanya dipakai untuk menggambar peta; semua angka yang divisualisasikan berasal dari BPS.")
    with st.expander("Metode dan rumus"):
        st.markdown("""**Klasifikasi peta (Bab 1).** Kuantil: 5 kelas dengan jumlah daerah yang sama. Natural breaks: k-means satu dimensi dengan 5 kelas (setara Fisher-Jenks). Kelas dihitung dari seluruh kab/kota Indonesia agar warna sebanding antar wilayah.

**Rata-rata tertimbang penduduk.** x̄ = Σ(xᵢ · Pᵢ) / ΣPᵢ, dengan Pᵢ jumlah penduduk kab/kota i.

**Jumlah penduduk miskin (simbol proporsional).** Persentase penduduk miskin × jumlah penduduk kab/kota.

**Moran's I dan LISA (Bab 1).** Nilai dibakukan (z). Bobot spasial: 6 tetangga terdekat dari titik pusat tiap daerah, standardisasi baris. I = Σ zᵢ·(Wz)ᵢ / Σ zᵢ². Signifikansi dari 499 permutasi acak, α = 0,05. Klaster LISA: tinggi-tinggi, rendah-rendah, tinggi-rendah, rendah-tinggi, dan tidak signifikan.

**Analisis multivariat (Bab 2).** Sepuluh indikator dibakukan (z-score), lalu PCA dua komponen, K-Means, dan klaster hierarkis Ward untuk urutan heatmap. Indeks gabungan = rata-rata z-score dengan arah dikoreksi (kemiskinan, kesakitan, dan merokok dibalik). Pencilan: jarak Mahalanobis² d² = zᵀS⁻¹z (S = kovarians antarindikator) melebihi χ² 97,5% dengan df = 10.

**Hierarki impor (Bab 3).** Nilai tiap kelompok = jumlah nilai komoditas di bawahnya. Pertumbuhan = (CIF 2025 − CIF 2024) / CIF 2024 × 100%, dihitung dari nilai yang dijumlahkan di tiap tingkat, bukan dari rata-rata pertumbuhan anaknya. Warna memakai skala divergen simetris di titik 0.""")
    with st.expander("Perangkat dan palet warna"):
        st.markdown("""- **Perangkat:** Python, Streamlit, Plotly, pandas, NumPy, scikit-learn, dan SciPy.
- **Palet warna:** Okabe-Ito untuk kategori; ColorBrewer YlGnBu dan YlOrBr untuk skala berurutan; RdBu untuk skala divergen. Semuanya dipilih agar dapat dibaca pembaca buta warna.
- **Penggunaan alat bantu AI:** alat bantu AI dipakai sebagai pendamping pengembangan sedangkan untuk seluruh isi, pengolahan, dan interpretasi menjadi tanggung jawab penyusun.""")
st.markdown(f"<p style='text-align:center;margin-top:2rem'><a href='#top'>↑ Baca ulang dari awal</a><br><small>Disusun oleh {AUTHOR} · Visualisasi Data · Politeknik Statistika STIS · 2026<br>Sumber data utama: Badan Pusat Statistik (BPS).</small></p>", unsafe_allow_html=True)
