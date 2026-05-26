import streamlit as st
import json
import os
import base64
import re
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────
st.set_page_config(
    page_title="EQStudio Admin — Kad Kahwin Digital",
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────
#  CUSTOM CSS
# ─────────────────────────────────────────
st.markdown("""
<style>
    .main { background: #0f0f0f; }
    .stApp { background: #111; }
    div[data-testid="stSidebar"] { background: #1a1a1a; }
    .block-container { padding-top: 2rem; }
    h1, h2, h3 { color: #C9A96E !important; }
    .stButton > button {
        background: linear-gradient(135deg, #C9A96E, #8B6B2E);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.6rem 1.5rem;
        width: 100%;
    }
    .stButton > button:hover { opacity: 0.9; }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background: #1e1e1e !important;
        color: #f0e8d8 !important;
        border: 1px solid #333 !important;
        border-radius: 8px !important;
    }
    .stNumberInput > div > div > input { background: #1e1e1e !important; color: #f0e8d8 !important; }
    .success-box {
        background: linear-gradient(135deg, #1a2e1a, #0f1f0f);
        border: 1px solid #2d5a2d;
        border-radius: 12px;
        padding: 1.5rem;
        margin: 1rem 0;
    }
    .info-box {
        background: linear-gradient(135deg, #1a1a2e, #0f0f1f);
        border: 1px solid #2d2d5a;
        border-radius: 12px;
        padding: 1rem;
        margin: .5rem 0;
        font-size: 0.85rem;
        color: #a0a8c0;
    }
    .template-card {
        background: #1e1e1e;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 1rem;
        margin: .5rem 0;
        cursor: pointer;
        transition: border-color 0.2s;
    }
    .category-badge {
        display: inline-block;
        background: rgba(201,169,110,0.15);
        border: 1px solid rgba(201,169,110,0.3);
        border-radius: 20px;
        padding: 2px 10px;
        font-size: 0.75rem;
        color: #C9A96E;
        margin-bottom: 0.5rem;
    }
    .order-id {
        font-family: monospace;
        background: #2a2a2a;
        padding: 4px 10px;
        border-radius: 6px;
        color: #C9A96E;
        font-size: 0.85rem;
    }
    div[data-testid="stExpander"] {
        background: #1a1a1a;
        border: 1px solid #333;
        border-radius: 10px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  TEMPLATE REGISTRY
#  Tambah template baru kat sini je!
# ─────────────────────────────────────────
TEMPLATES = {
    "Essential": {
        "v2_celestial": {
            "name": "Celestial — Bintang & Bulan",
            "file": "templates/v2_celestial.html",
            "has_photo": False,
            "preview_emoji": "🌙",
            "desc": "Tema langit malam, bintang bersinar, navy & gold",
        },
        "v3_garden": {
            "name": "Garden — Taman Botanik",
            "file": "templates/v3_garden.html",
            "has_photo": False,
            "preview_emoji": "🌸",
            "desc": "Tema taman bunga, sage green & dusty rose",
        },
        "v4_arabian": {
            "name": "Arabian — Malam Seribu Bintang",
            "file": "templates/v4_arabian.html",
            "has_photo": False,
            "preview_emoji": "🏮",
            "desc": "Tema moroccan, teal & gold, lantern opening",
        },
    },
    "Portrait": {
        "portrait_royal": {
            "name": "Royal Velvet — Ada Gambar",
            "file": "templates/portrait_royal.html",
            "has_photo": True,
            "preview_emoji": "👑",
            "desc": "Tema mewah burgundy & champagne, gallery gambar",
        },
    },
    # Tambah category baru macam ni:
    # "Premium": {
    #     "template_key": {
    #         "name": "Nama Template",
    #         "file": "templates/nama_fail.html",
    #         "has_photo": True/False,
    #         "preview_emoji": "✨",
    #         "desc": "Penerangan ringkas",
    #     },
    # },
}

# ─────────────────────────────────────────
#  PLACEHOLDERS — ini yang kena ada dalam HTML template
#  Format: {{PLACEHOLDER}}
# ─────────────────────────────────────────
PLACEHOLDERS = {
    # Info pengantin
    "{{GROOM_NAME}}":       "Nama pengantin lelaki",
    "{{BRIDE_NAME}}":       "Nama pengantin perempuan",
    "{{GROOM_FULL}}":       "Nama penuh pengantin lelaki",
    "{{BRIDE_FULL}}":       "Nama penuh pengantin perempuan",
    # Ibu bapa
    "{{FATHER_NAME}}":      "Nama bapa tuan rumah",
    "{{MOTHER_NAME}}":      "Nama ibu tuan rumah",
    "{{PARENT_SIDE}}":      "Pihak (Perempuan/Lelaki)",
    # Tarikh & masa
    "{{DATE_DISPLAY}}":     "Tarikh papar (eg: 10 Ogos 2026)",
    "{{DATE_DAY}}":         "Hari (eg: Isnin)",
    "{{DATE_HIJRI}}":       "Tarikh hijri (eg: 15 Safar 1448H)",
    "{{DATE_ISO}}":         "Tarikh ISO untuk countdown (eg: 2026-08-10T12:00:00+08:00)",
    "{{TIME_DISPLAY}}":     "Masa (eg: 12:00 Tengahari)",
    # Lokasi
    "{{VENUE_NAME}}":       "Nama dewan",
    "{{VENUE_ADDRESS}}":    "Alamat penuh",
    "{{WAZE_LINK}}":        "Link Waze",
    "{{GMAP_LINK}}":        "Link Google Maps",
    # Hubungi
    "{{CONTACT_NAME}}":     "Nama contact person",
    "{{CONTACT_PHONE}}":    "No telefon (format: 0123456789)",
    "{{CONTACT_PHONE_WA}}": "No telefon WhatsApp (format: 60123456789)",
    # Media
    "{{MUSIC_URL}}":        "Link direct MP3",
    "{{MUSIC_LABEL}}":      "Label nama lagu (eg: Beautiful In White)",
    # Gambar (Portrait sahaja)
    "{{HERO_PHOTO_URL}}":   "Link gambar hero (fullscreen)",
    "{{PHOTO1_URL}}":       "Link gambar gallery 1",
    "{{PHOTO2_URL}}":       "Link gambar gallery 2",
    "{{PHOTO3_URL}}":       "Link gambar gallery 3",
    "{{OPENING_PHOTO_URL}}":"Link gambar opening",
}

# ─────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────
def load_template(filepath: str) -> str:
    """Load HTML template dari fail."""
    path = Path(filepath)
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")

def apply_replacements(html: str, data: dict) -> str:
    """Replace semua placeholder dalam HTML dengan data customer."""
    for key, val in data.items():
        if val:
            html = html.replace(key, str(val))
    return html

def generate_order_id() -> str:
    """Jana Order ID unik."""
    now = datetime.now()
    return f"EQ{now.strftime('%y%m%d%H%M')}"

def file_to_data_url(uploaded_file) -> str:
    """Convert uploaded file to base64 data URL."""
    b64 = base64.b64encode(uploaded_file.read()).decode()
    mime = uploaded_file.type
    return f"data:{mime};base64,{b64}"

def get_whatsapp_number(phone: str) -> str:
    """Tukar nombor telefon ke format WhatsApp Malaysia."""
    phone = re.sub(r'\D', '', phone)
    if phone.startswith('0'):
        phone = '60' + phone[1:]
    elif not phone.startswith('60'):
        phone = '60' + phone
    return phone

def get_waze_link(address: str) -> str:
    encoded = address.replace(' ', '+')
    return f"https://waze.com/ul?q={encoded}&navigate=yes"

def get_gmap_link(address: str) -> str:
    encoded = address.replace(' ', '+')
    return f"https://maps.google.com/?q={encoded}"

def get_all_templates_flat():
    """Return flat dict of all templates."""
    flat = {}
    for cat, templates in TEMPLATES.items():
        for key, info in templates.items():
            flat[key] = {**info, "category": cat}
    return flat

# ─────────────────────────────────────────
#  SIDEBAR — NAVIGATION
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💍 EQStudio Admin")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["🆕 Jana Kad Baru", "📋 Cara Guna", "🗂️ Template Info"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem; color:#666; line-height:1.8'>
    <b style='color:#C9A96E'>EQStudio</b><br>
    Admin Dashboard v1.0<br>
    Kad Kahwin Digital
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────
#  PAGE: JANA KAD BARU
# ─────────────────────────────────────────
if "🆕 Jana Kad Baru" in page:

    st.markdown("# 🆕 Jana Kad Kahwin Digital")
    st.markdown("Isi semua maklumat customer di bawah, tekan **Jana Kad**, dan download terus!")
    st.markdown("---")

    # ── STEP 1: PILIH TEMPLATE ──
    st.markdown("## 1️⃣ Pilih Template")

    all_templates = get_all_templates_flat()
    cat_selected = st.selectbox(
        "Pilih Category",
        list(TEMPLATES.keys()),
        format_func=lambda x: f"{'⭐' if x == 'Essential' else '📸' if x == 'Portrait' else '✨'} {x}"
    )

    tmpl_options = TEMPLATES[cat_selected]
    tmpl_key = st.selectbox(
        "Pilih Template",
        list(tmpl_options.keys()),
        format_func=lambda k: f"{tmpl_options[k]['preview_emoji']}  {tmpl_options[k]['name']}"
    )

    selected_tmpl = tmpl_options[tmpl_key]
    st.markdown(f"""
    <div class='info-box'>
        <span class='category-badge'>{cat_selected}</span><br>
        <b style='color:#f0e8d8'>{selected_tmpl['preview_emoji']} {selected_tmpl['name']}</b><br>
        {selected_tmpl['desc']}<br>
        {'📸 Template ini memerlukan gambar pengantin' if selected_tmpl['has_photo'] else '🎨 Template tanpa gambar'}
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── STEP 2: INFO PENGANTIN ──
    st.markdown("## 2️⃣ Maklumat Pengantin")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🤵 Pengantin Lelaki**")
        groom_name = st.text_input("Nama Panggilan", placeholder="Ahmad Nazmi", key="groom")
        groom_full = st.text_input("Nama Penuh (opsional)", placeholder="Ahmad Nazmi bin Abdullah", key="groom_full")
    with col2:
        st.markdown("**👰 Pengantin Perempuan**")
        bride_name = st.text_input("Nama Panggilan", placeholder="Nur Farhana", key="bride")
        bride_full = st.text_input("Nama Penuh (opsional)", placeholder="Nur Farhana binti Ibrahim", key="bride_full")

    st.markdown("---")

    # ── STEP 3: IBU BAPA / TUAN RUMAH ──
    st.markdown("## 3️⃣ Maklumat Tuan Rumah")
    col3, col4 = st.columns(2)
    with col3:
        father_name = st.text_input("Nama Bapa", placeholder="Sufian bin Salleh")
        parent_side = st.selectbox("Pihak", ["Perempuan", "Lelaki", "Perempuan & Lelaki"])
    with col4:
        mother_name = st.text_input("Nama Ibu", placeholder="Siti Maimun")

    st.markdown("---")

    # ── STEP 4: TARIKH & MASA ──
    st.markdown("## 4️⃣ Tarikh & Masa Majlis")
    col5, col6 = st.columns(2)
    with col5:
        event_date = st.date_input("Tarikh Majlis")
        event_time = st.time_input("Masa Majlis")
        hijri_date = st.text_input("Tarikh Hijri", placeholder="15 Safar 1448H")
    with col6:
        # Auto-generate display values
        days_ms = ["Isnin","Selasa","Rabu","Khamis","Jumaat","Sabtu","Ahad"]
        months_ms = ["","Januari","Februari","Mac","April","Mei","Jun","Julai","Ogos","September","Oktober","November","Disember"]
        day_name = days_ms[event_date.weekday()]
        date_display = f"{event_date.day} {months_ms[event_date.month]} {event_date.year}"
        time_display = event_time.strftime("%I:%M %p").lstrip("0").replace("AM","Pagi").replace("PM","Tengahari/Petang")
        date_iso = f"{event_date.isoformat()}T{event_time.strftime('%H:%M:%S')}+08:00"

        st.markdown(f"""
        <div class='info-box'>
            <b style='color:#C9A96E'>Preview Tarikh:</b><br>
            📅 {day_name}, {date_display}<br>
            🕐 {event_time.strftime('%H:%M')} ({time_display})<br>
            🗓️ {hijri_date if hijri_date else '—'}<br>
            <small style='opacity:0.5'>ISO: {date_iso}</small>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")

    # ── STEP 5: LOKASI ──
    st.markdown("## 5️⃣ Lokasi Majlis")
    venue_name = st.text_input("Nama Dewan / Tempat", placeholder="Sebening Embun Garden Glass Hall")
    venue_address = st.text_area("Alamat Penuh", placeholder="Lot 15, Jalan Durian 1, Kg. Sungai Buah, 43800 Dengkil, Selangor", height=80)

    col7, col8 = st.columns(2)
    with col7:
        waze_custom = st.text_input("Link Waze (opsional — biarkan kosong untuk auto-generate)", placeholder="https://waze.com/ul?...")
    with col8:
        gmap_custom = st.text_input("Link Google Maps (opsional)", placeholder="https://maps.google.com/...")

    # Auto-generate links kalau kosong
    waze_link = waze_custom if waze_custom else (get_waze_link(f"{venue_name} {venue_address}") if venue_name else "")
    gmap_link = gmap_custom if gmap_custom else (get_gmap_link(f"{venue_name} {venue_address}") if venue_name else "")

    st.markdown("---")

    # ── STEP 6: CONTACT PERSON ──
    st.markdown("## 6️⃣ Contact Person")
    col9, col10 = st.columns(2)
    with col9:
        contact_name = st.text_input("Nama Contact Person", placeholder="Sufian bin Salleh")
        contact_phone = st.text_input("No Telefon", placeholder="011-3562 3312")
    with col10:
        if contact_phone:
            wa_num = get_whatsapp_number(contact_phone)
            st.markdown(f"""
            <div class='info-box'>
                <b style='color:#C9A96E'>WhatsApp Number:</b><br>
                📱 {wa_num}<br>
                <small style='opacity:0.5'>Format untuk wa.me link</small>
            </div>
            """, unsafe_allow_html=True)
        else:
            wa_num = ""

    st.markdown("---")

    # ── STEP 7: LAGU ──
    st.markdown("## 7️⃣ Lagu Latar")
    st.markdown("""
    <div class='info-box'>
        💡 <b>Cara host lagu:</b> Upload MP3 ke GitHub repo (public) → guna link jsDelivr:<br>
        <code>https://cdn.jsdelivr.net/gh/USERNAME/REPO@main/lagu.mp3</code>
    </div>
    """, unsafe_allow_html=True)

    music_url = st.text_input("Link Direct MP3", placeholder="https://cdn.jsdelivr.net/gh/nureqmal/eqstudio@main/assets/lagu.mp3")
    music_label = st.text_input("Nama Lagu (untuk label player)", placeholder="Beautiful In White — Westlife")

    st.markdown("---")

    # ── STEP 8: GAMBAR (Portrait sahaja) ──
    if selected_tmpl["has_photo"]:
        st.markdown("## 8️⃣ Gambar Pengantin (Portrait)")
        st.markdown("""
        <div class='info-box'>
            📸 Untuk gambar, boleh:<br>
            • <b>Upload file terus</b> — gambar akan di-embed dalam HTML (saiz fail jadi besar sikit)<br>
            • <b>Paste link URL</b> — gambar dari Google Drive / GitHub / mana-mana hosting
        </div>
        """, unsafe_allow_html=True)

        photo_method = st.radio("Cara masukkan gambar", ["📎 Upload File", "🔗 Paste Link URL"], horizontal=True)

        hero_url = photo1_url = photo2_url = photo3_url = opening_url = ""

        if photo_method == "📎 Upload File":
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                hero_file = st.file_uploader("🖼️ Hero Background (fullscreen)", type=["jpg","jpeg","png","webp"], key="hero")
                photo1_file = st.file_uploader("📸 Gallery Foto 1", type=["jpg","jpeg","png","webp"], key="p1")
                opening_file = st.file_uploader("🎴 Opening Photo", type=["jpg","jpeg","png","webp"], key="op")
            with col_p2:
                photo2_file = st.file_uploader("📸 Gallery Foto 2 (utama)", type=["jpg","jpeg","png","webp"], key="p2")
                photo3_file = st.file_uploader("📸 Gallery Foto 3", type=["jpg","jpeg","png","webp"], key="p3")

            if hero_file: hero_url = file_to_data_url(hero_file)
            if photo1_file: photo1_url = file_to_data_url(photo1_file)
            if photo2_file: photo2_url = file_to_data_url(photo2_file)
            if photo3_file: photo3_url = file_to_data_url(photo3_file)
            if opening_file: opening_url = file_to_data_url(opening_file)

        else:
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                hero_url = st.text_input("🖼️ Hero Background URL", placeholder="https://...")
                photo1_url = st.text_input("📸 Gallery Foto 1 URL", placeholder="https://...")
                opening_url = st.text_input("🎴 Opening Photo URL", placeholder="https://...")
            with col_p2:
                photo2_url = st.text_input("📸 Gallery Foto 2 URL (utama)", placeholder="https://...")
                photo3_url = st.text_input("📸 Gallery Foto 3 URL", placeholder="https://...")

        st.markdown("---")

    # ── STEP 9: JANA KAD ──
    st.markdown("## 9️⃣ Jana & Download")

    # Validation
    required = {
        "Nama pengantin lelaki": groom_name,
        "Nama pengantin perempuan": bride_name,
        "Nama bapa tuan rumah": father_name,
        "Nama dewan": venue_name,
        "Alamat majlis": venue_address,
        "No telefon contact": contact_phone,
    }
    missing = [k for k, v in required.items() if not v]

    if missing:
        st.warning(f"⚠️ Sila lengkapkan: **{', '.join(missing)}**")

    if st.button("✨ Jana Kad Sekarang!", disabled=bool(missing)):
        # Load template
        template_html = load_template(selected_tmpl["file"])

        if template_html is None:
            st.error(f"❌ Template fail tidak dijumpai: `{selected_tmpl['file']}`\n\nPastikan fail HTML template ada dalam folder `templates/`")
        else:
            order_id = generate_order_id()

            # Build replacement dict
            replacements = {
                "{{GROOM_NAME}}":       groom_name,
                "{{BRIDE_NAME}}":       bride_name,
                "{{GROOM_FULL}}":       groom_full or groom_name,
                "{{BRIDE_FULL}}":       bride_full or bride_name,
                "{{FATHER_NAME}}":      father_name,
                "{{MOTHER_NAME}}":      mother_name,
                "{{PARENT_SIDE}}":      parent_side,
                "{{DATE_DISPLAY}}":     date_display,
                "{{DATE_DAY}}":         day_name,
                "{{DATE_HIJRI}}":       hijri_date,
                "{{DATE_ISO}}":         date_iso,
                "{{TIME_DISPLAY}}":     time_display,
                "{{TIME_RAW}}":         event_time.strftime('%H:%M'),
                "{{VENUE_NAME}}":       venue_name,
                "{{VENUE_ADDRESS}}":    venue_address,
                "{{WAZE_LINK}}":        waze_link,
                "{{GMAP_LINK}}":        gmap_link,
                "{{CONTACT_NAME}}":     contact_name or father_name,
                "{{CONTACT_PHONE}}":    contact_phone,
                "{{CONTACT_PHONE_WA}}": wa_num,
                "{{MUSIC_URL}}":        music_url or "",
                "{{MUSIC_LABEL}}":      music_label or "Lagu Perkahwinan",
            }

            # Add photo replacements kalau Portrait
            if selected_tmpl["has_photo"]:
                replacements.update({
                    "{{HERO_PHOTO_URL}}":    hero_url,
                    "{{PHOTO1_URL}}":        photo1_url,
                    "{{PHOTO2_URL}}":        photo2_url,
                    "{{PHOTO3_URL}}":        photo3_url,
                    "{{OPENING_PHOTO_URL}}": opening_url,
                })

            # Apply replacements
            final_html = apply_replacements(template_html, replacements)

            # Encode for download
            html_bytes = final_html.encode("utf-8")
            filename = f"kad_{groom_name.lower().replace(' ','_')}_{bride_name.lower().replace(' ','_')}_{order_id}.html"

            st.markdown(f"""
            <div class='success-box'>
                <h3 style='color:#4CAF50;margin:0 0 .5rem'>✅ Kad Berjaya Dijana!</h3>
                <span class='order-id'>Order ID: {order_id}</span><br><br>
                <b>Customer:</b> {groom_name} & {bride_name}<br>
                <b>Tarikh:</b> {date_display}<br>
                <b>Template:</b> {selected_tmpl['name']}<br>
                <b>Fail:</b> {filename}
            </div>
            """, unsafe_allow_html=True)

            st.download_button(
                label="⬇️ Download HTML Kad",
                data=html_bytes,
                file_name=filename,
                mime="text/html",
                use_container_width=True,
            )

            # Preview
            with st.expander("👁️ Preview HTML (raw)"):
                st.code(final_html[:3000] + "\n\n... [truncated]", language="html")

# ─────────────────────────────────────────
#  PAGE: CARA GUNA
# ─────────────────────────────────────────
elif "📋 Cara Guna" in page:
    st.markdown("# 📋 Cara Guna Admin Dashboard")
    st.markdown("---")

    st.markdown("""
    ## 🔄 Workflow Lengkap

    ### 1. Terima Order dari Customer
    Customer order melalui website kau → masuk WhatsApp dengan:
    - Nama pengantin
    - Tarikh majlis
    - Template yang dipilih
    - Gambar (kalau Portrait)
    - Lagu pilihan

    ### 2. Host Lagu Customer
    Customer hantar MP3 → kau upload ke **GitHub repo public**:
    ```
    github.com/nureqmal/eqstudio → folder assets/
    ```
    Link untuk guna dalam app:
    ```
    https://cdn.jsdelivr.net/gh/nureqmal/eqstudio@main/assets/NAMA_LAGU.mp3
    ```

    ### 3. Isi Form dalam App Ni
    - Pilih category & template
    - Isi semua maklumat customer
    - Paste link lagu
    - Upload / link gambar (Portrait)
    - Klik **Jana Kad**

    ### 4. Download & Hantar
    - Download HTML file
    - Test dalam browser — preview betul-betul
    - Upload ke **GitHub Pages** repo customer
    - Hantar link kepada customer

    ---

    ## 📁 Setup Template Baru

    ### Cara Tambah Template
    1. Buat HTML template baru dengan **placeholders** `{{GROOM_NAME}}` etc
    2. Letak dalam folder `templates/`
    3. Daftar dalam `TEMPLATES` dict dalam `app.py`

    ### Senarai Semua Placeholders
    """)

    for placeholder, desc in PLACEHOLDERS.items():
        st.markdown(f"- `{placeholder}` — {desc}")

    st.markdown("""
    ---
    ## 🎵 Cara Host Lagu (Free Forever)

    **GitHub + jsDelivr (Recommended):**
    1. Upload MP3 ke GitHub repo public kau
    2. Guna link format:
    ```
    https://cdn.jsdelivr.net/gh/USERNAME/REPO@main/FOLDER/LAGU.mp3
    ```

    **Pastikan repo PUBLIC** — kalau private, lagu tak boleh diakses!
    """)

# ─────────────────────────────────────────
#  PAGE: TEMPLATE INFO
# ─────────────────────────────────────────
elif "🗂️ Template Info" in page:
    st.markdown("# 🗂️ Senarai Template")
    st.markdown("---")

    for category, templates in TEMPLATES.items():
        st.markdown(f"## {'⭐' if category == 'Essential' else '📸' if category == 'Portrait' else '✨'} {category}")
        for key, info in templates.items():
            file_exists = Path(info['file']).exists()
            status = "✅ Fail ada" if file_exists else "❌ Fail tidak jumpa"
            st.markdown(f"""
            <div class='template-card'>
                <span class='category-badge'>{category}</span>
                <b style='color:#f0e8d8;font-size:1.05rem'>{info['preview_emoji']} {info['name']}</b><br>
                <small style='color:#888'>{info['desc']}</small><br><br>
                <small>
                    📁 <code>{info['file']}</code> — {status}<br>
                    {'📸 Perlu gambar' if info['has_photo'] else '🎨 Tanpa gambar'}
                </small>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("")

    st.markdown("---")
    st.markdown("""
    ### ➕ Cara Tambah Template Baru

    Edit `app.py`, cari bahagian `TEMPLATES` di atas, tambah template baru:
    ```python
    "NamaCategory": {
        "template_key": {
            "name": "Nama Template",
            "file": "templates/nama_fail.html",
            "has_photo": True,  # atau False
            "preview_emoji": "✨",
            "desc": "Penerangan ringkas",
        },
    },
    ```
    """)
