# 💍 EQStudio Admin — Kad Kahwin Digital

Dashboard admin untuk jana kad kahwin digital dengan mudah.

## 📁 Struktur Folder

```
eqstudio-admin/
├── app.py                  ← App utama Streamlit
├── requirements.txt        ← Dependencies
├── README.md               ← Fail ni
└── templates/              ← Letak semua HTML template kat sini
    ├── v2_celestial.html
    ├── v3_garden.html
    ├── v4_arabian.html
    └── portrait_royal.html
```

## 🚀 Setup

### Step 1 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 2 — Letak template HTML
Salin semua fail HTML template ke dalam folder `templates/`.
**Penting:** Template mesti ada placeholders macam `{{GROOM_NAME}}` etc.

### Step 3 — Run app
```bash
streamlit run app.py
```

## 🌐 Deploy ke Streamlit Cloud (Free)

1. Push folder ni ke GitHub repo (boleh private)
2. Pergi [share.streamlit.io](https://share.streamlit.io)
3. Connect GitHub → pilih repo → set `app.py` sebagai main file
4. Deploy!

URL akan jadi: `https://USERNAME-REPONAME-app.streamlit.app`

## 📝 Placeholders dalam HTML Template

Semua placeholder dalam format `{{NAMA}}`:

| Placeholder | Penerangan |
|---|---|
| `{{GROOM_NAME}}` | Nama panggilan pengantin lelaki |
| `{{BRIDE_NAME}}` | Nama panggilan pengantin perempuan |
| `{{GROOM_FULL}}` | Nama penuh pengantin lelaki |
| `{{BRIDE_FULL}}` | Nama penuh pengantin perempuan |
| `{{FATHER_NAME}}` | Nama bapa tuan rumah |
| `{{MOTHER_NAME}}` | Nama ibu tuan rumah |
| `{{PARENT_SIDE}}` | Pihak (Perempuan/Lelaki) |
| `{{DATE_DISPLAY}}` | eg: 10 Ogos 2026 |
| `{{DATE_DAY}}` | eg: Isnin |
| `{{DATE_HIJRI}}` | eg: 15 Safar 1448H |
| `{{DATE_ISO}}` | eg: 2026-08-10T12:00:00+08:00 |
| `{{TIME_DISPLAY}}` | eg: 12:00 Tengahari |
| `{{TIME_RAW}}` | eg: 12:00 |
| `{{VENUE_NAME}}` | Nama dewan |
| `{{VENUE_ADDRESS}}` | Alamat penuh |
| `{{WAZE_LINK}}` | Link Waze |
| `{{GMAP_LINK}}` | Link Google Maps |
| `{{CONTACT_NAME}}` | Nama contact person |
| `{{CONTACT_PHONE}}` | No telefon display |
| `{{CONTACT_PHONE_WA}}` | No telefon format WhatsApp |
| `{{MUSIC_URL}}` | Link direct MP3 |
| `{{MUSIC_LABEL}}` | Nama lagu |
| `{{HERO_PHOTO_URL}}` | (Portrait) Gambar hero |
| `{{PHOTO1_URL}}` | (Portrait) Gallery foto 1 |
| `{{PHOTO2_URL}}` | (Portrait) Gallery foto 2 |
| `{{PHOTO3_URL}}` | (Portrait) Gallery foto 3 |
| `{{OPENING_PHOTO_URL}}` | (Portrait) Gambar opening |
