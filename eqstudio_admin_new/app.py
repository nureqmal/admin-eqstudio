import streamlit as st
import json
import os
import base64
import re
import requests
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent

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
    .stButton > button:disabled { opacity: 0.4; cursor: not-allowed; }
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
    .warning-box {
        background: linear-gradient(135deg, #2e2a1a, #1f1a0f);
        border: 1px solid #5a4a2d;
        border-radius: 12px;
        padding: 1rem;
        margin: .5rem 0;
        font-size: 0.85rem;
        color: #c0b08a;
    }
    .link-box {
        background: linear-gradient(135deg, #0f2e1a, #0a1f12);
        border: 1px solid #1a5a32;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin: 1rem 0;
        word-break: break-all;
    }
    .template-card {
        background: #1e1e1e;
        border: 1px solid #333;
        border-radius: 12px;
        padding: 1rem;
        margin: .5rem 0;
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
# ─────────────────────────────────────────
TEMPLATES = {
    "Essential": {
        "v2_celestial": {
            "name": "Celestial — Bintang & Bulan",
            "file": "v2_celestial.html",
            "has_photo": False,
            "preview_emoji": "🌙",
            "desc": "Tema langit malam, bintang bersinar, navy & gold",
        },

        "v5_namabaru": {           # ← tambah ni
            "name": "Sliding Style",
            "file": "Jemputan Ijab Kabul Afifi & Zahidah (RSVP2)",
            "has_photo": False,
            "preview_emoji": "✨",
            "desc": "test afifi punya",
    },
        "v3_garden": {
            "name": "Garden — Taman Botanik",
            "file": "v3_garden.html",
            "has_photo": False,
            "preview_emoji": "🌸",
            "desc": "Tema taman bunga, sage green & dusty rose",
        },
        "v4_arabian": {
            "name": "Arabian — Malam Seribu Bintang",
            "file": "v4_arabian.html",
            "has_photo": False,
            "preview_emoji": "🏮",
            "desc": "Tema moroccan, teal & gold, lantern opening",
        },
    },
    "Portrait": {
        "portrait_royal": {
            "name": "Royal Velvet — Ada Gambar",
            "file": "portrait_royal.html",
            "has_photo": True,
            "preview_emoji": "👑",
            "desc": "Tema mewah burgundy & champagne, gallery gambar",
        },
    },
    "Cinematic": {
    "v1_cinematic": {
        "name": "Cinematic — Contoh Nama",
        "file": "v1_cinematic.html",
        "has_photo": True,
        "has_video": True,
        "preview_emoji": "🎬",
        "desc": "Penerangan ringkas",
    },
},
    "Prestige": {
    "v1_prestige": {
        "name": "Prestige — Contoh Nama",
        "file": "v1_prestige.html",
        "has_photo": True,
        "has_video": True,
        "has_gallery": True,
        "preview_emoji": "💎",
        "desc": "Penerangan ringkas",
    },
}

PLACEHOLDERS = {
    "{{GROOM_NAME}}":       "Nama pengantin lelaki",
    "{{BRIDE_NAME}}":       "Nama pengantin perempuan",
    "{{GROOM_FULL}}":       "Nama penuh pengantin lelaki",
    "{{BRIDE_FULL}}":       "Nama penuh pengantin perempuan",
    "{{FATHER_NAME}}":      "Nama bapa tuan rumah",
    "{{MOTHER_NAME}}":      "Nama ibu tuan rumah",
    "{{PARENT_SIDE}}":      "Pihak (Perempuan/Lelaki)",
    "{{DATE_DISPLAY}}":     "Tarikh papar (eg: 10 Ogos 2026)",
    "{{DATE_DAY}}":         "Hari (eg: Isnin)",
    "{{DATE_HIJRI}}":       "Tarikh hijri (eg: 15 Safar 1448H)",
    "{{DATE_ISO}}":         "Tarikh ISO untuk countdown (eg: 2026-08-10T12:00:00+08:00)",
    "{{TIME_DISPLAY}}":     "Masa (eg: 12:00 Tengahari)",
    "{{VENUE_NAME}}":       "Nama dewan",
    "{{VENUE_ADDRESS}}":    "Alamat penuh",
    "{{WAZE_LINK}}":        "Link Waze",
    "{{GMAP_LINK}}":        "Link Google Maps",
    "{{CONTACT_NAME}}":     "Nama contact person",
    "{{CONTACT_PHONE}}":    "No telefon (format: 0123456789)",
    "{{CONTACT_PHONE_WA}}": "No telefon WhatsApp (format: 60123456789)",
    "{{MUSIC_URL}}":        "Link direct MP3",
    "{{MUSIC_LABEL}}":      "Label nama lagu (eg: Beautiful In White)",
    "{{HERO_PHOTO_URL}}":   "Link gambar hero (fullscreen)",
    "{{PHOTO1_URL}}":       "Link gambar gallery 1",
    "{{PHOTO2_URL}}":       "Link gambar gallery 2",
    "{{PHOTO3_URL}}":       "Link gambar gallery 3",
    "{{OPENING_PHOTO_URL}}":"Link gambar opening",
    "{{VIDEO_URL}}":        "Link Google Drive video",
    "{{GALLERY1_URL}}":     "Link gambar gallery 1",
    "{{GALLERY2_URL}}":     "Link gambar gallery 2",
    "{{GALLERY3_URL}}":     "Link gambar gallery 3",
    "{{GALLERY4_URL}}":     "Link gambar gallery 4",
    "{{GALLERY5_URL}}":     "Link gambar gallery 5",
}

# ─────────────────────────────────────────
#  GITHUB HELPER FUNCTIONS
# ─────────────────────────────────────────
def github_upload_file(token: str, repo: str, filepath: str, content: str, commit_msg: str) -> dict:
    """
    Upload / overwrite satu file ke GitHub repo via API.
    content = raw string (bukan base64) — function ni akan encode sendiri.
    Returns dict dengan 'success', 'url', 'raw_url', 'error'.
    """
    api_url = f"https://api.github.com/repos/{repo}/contents/{filepath}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    # Check kalau file dah wujud — kena ambik SHA dulu untuk update
    sha = None
    r = requests.get(api_url, headers=headers, timeout=15)
    if r.status_code == 200:
        sha = r.json().get("sha")

    # Encode content ke base64
    content_b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    payload = {
        "message": commit_msg,
        "content": content_b64,
    }
    if sha:
        payload["sha"] = sha  # Required untuk update file sedia ada

    r = requests.put(api_url, headers=headers, json=payload, timeout=30)

    if r.status_code in (200, 201):
        data = r.json()
        raw_url = data["content"]["download_url"]
        # Convert raw URL ke GitHub Pages URL
        # raw: https://raw.githubusercontent.com/USER/REPO/main/path
        # pages: https://USER.github.io/REPO/path
        parts = raw_url.replace("https://raw.githubusercontent.com/", "").split("/")
        user = parts[0]
        repo_name = parts[1]
        # parts[2] = branch
        file_path = "/".join(parts[3:])
        pages_url = f"https://{user}.github.io/{repo_name}/{file_path}"
        return {"success": True, "pages_url": pages_url, "raw_url": raw_url}
    else:
        try:
            err = r.json().get("message", r.text)
        except Exception:
            err = r.text
        return {"success": False, "error": f"GitHub API error {r.status_code}: {err}"}


def validate_github_token(token: str, repo: str) -> tuple[bool, str]:
    """Check token valid dan ada access ke repo."""
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    r = requests.get(f"https://api.github.com/repos/{repo}", headers=headers, timeout=10)
    if r.status_code == 200:
        data = r.json()
        has_pages = data.get("has_pages", False)
        return True, "ok" if has_pages else "no_pages"
    elif r.status_code == 401:
        return False, "Token tidak valid atau expired."
    elif r.status_code == 404:
        return False, f"Repo `{repo}` tidak jumpa atau token tiada access."
    else:
        return False, f"Error {r.status_code}"


# ─────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────
def load_template(filename: str) -> str:
    path = BASE_DIR / "templates" / filename
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")

def apply_replacements(html: str, data: dict) -> str:
    for key, val in data.items():
        if val:
            html = html.replace(key, str(val))
    return html

def generate_order_id() -> str:
    now = datetime.now()
    return f"EQ{now.strftime('%y%m%d%H%M')}"

def file_to_data_url(uploaded_file) -> str:
    b64 = base64.b64encode(uploaded_file.read()).decode()
    mime = uploaded_file.type
    return f"data:{mime};base64,{b64}"

def get_whatsapp_number(phone: str) -> str:
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
    flat = {}
    for cat, templates in TEMPLATES.items():
        for key, info in templates.items():
            flat[key] = {**info, "category": cat}
    return flat

def sanitize_filename(name: str) -> str:
    """Convert nama ke URL-safe string."""
    name = name.lower().strip()
    name = re.sub(r'[^a-z0-9]+', '-', name)
    return name.strip('-')

# ─────────────────────────────────────────
#  SIDEBAR — NAVIGATION + GITHUB SETTINGS
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💍 EQStudio Admin")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["🆕 Jana Kad Baru", "⚙️ GitHub Settings", "📋 Cara Guna", "🗂️ Template Info"],
        label_visibility="collapsed"
    )
    st.markdown("---")

    # Quick status GitHub
    gh_token = st.session_state.get("gh_token", "") or st.secrets.get("GH_TOKEN", "")
    gh_repo = st.session_state.get("gh_repo", "") or st.secrets.get("GH_REPO", "")
    if gh_token and gh_repo:
        st.markdown("""
        <div style='font-size:0.75rem; color:#4CAF50; line-height:1.8'>
        ✅ <b style='color:#C9A96E'>GitHub</b> Connected<br>
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.7rem;color:#666;margin-top:2px'>📁 {gh_repo}</div>", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='font-size:0.75rem; color:#888; line-height:1.8'>
        ⚠️ GitHub belum setup<br>
        <small>Pergi ⚙️ GitHub Settings</small>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("""
    <div style='font-size:0.75rem; color:#666; line-height:1.8'>
    <b style='color:#C9A96E'>EQStudio</b><br>
    Admin Dashboard v2.0<br>
    Kad Kahwin Digital
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────
#  PAGE: GITHUB SETTINGS
# ─────────────────────────────────────────
if "⚙️ GitHub Settings" in page:
    st.markdown("# ⚙️ GitHub Settings")
    st.markdown("Setup sekali, guna selama-lamanya. Kad customer akan auto-deploy ke GitHub Pages.")
    st.markdown("---")

    st.markdown("## 📋 Setup Guide")
    with st.expander("Langkah-langkah setup (klik untuk buka)", expanded=True):
        st.markdown("""
        ### 1️⃣ Buat repo baru di GitHub
        Pergi [github.com/new](https://github.com/new) dan buat repo baru:
        - **Repository name:** contoh `eqstudio-cards` (nama ikut suka)
        - **Visibility:** ✅ **Public** (wajib untuk GitHub Pages free)
        - Tick **"Add a README file"** (supaya repo tak kosong)
        - Klik **Create repository**

        ### 2️⃣ Aktifkan GitHub Pages
        Dalam repo baru tu:
        - Pergi **Settings** → **Pages** (dalam sidebar kiri)
        - **Source:** Deploy from a branch
        - **Branch:** `main` → folder `/` (root)
        - Klik **Save**
        - URL pages kau akan jadi: `https://USERNAME.github.io/REPO-NAME/`

        ### 3️⃣ Jana GitHub Token
        Pergi [github.com/settings/tokens/new](https://github.com/settings/tokens/new):
        - **Note:** `EQStudio Admin` (nama ikut suka)
        - **Expiration:** No expiration (atau 1 year)
        - **Scopes:** Tick ✅ **`repo`** (full control of private repositories)
        - Klik **Generate token**
        - **COPY TOKEN SEKARANG** — lepas refresh page, token tak boleh tengok balik!

        ### 4️⃣ Isi details kat bawah ni
        """)

    st.markdown("---")
    st.markdown("## 🔑 Masukkan Details")

    col1, col2 = st.columns(2)
    with col1:
        input_token = st.text_input(
            "GitHub Personal Access Token",
            type="password",
            value=st.session_state.get("gh_token", ""),
            placeholder="ghp_xxxxxxxxxxxxxxxxxxxx",
            help="Token dari github.com/settings/tokens"
        )
    with col2:
        input_repo = st.text_input(
            "GitHub Repo (format: username/repo-name)",
            value=st.session_state.get("gh_repo", ""),
            placeholder="nureqmal/eqstudio-cards",
            help="Contoh: nureqmal/eqstudio-cards"
        )

    col3, col4 = st.columns([1, 3])
    with col3:
        if st.button("🔍 Test Connection"):
            if not input_token or not input_repo:
                st.error("Isi token dan repo dulu!")
            else:
                with st.spinner("Checking..."):
                    valid, msg = validate_github_token(input_token, input_repo)
                if valid:
                    st.session_state["gh_token"] = input_token
                    st.session_state["gh_repo"] = input_repo
                    if msg == "no_pages":
                        st.warning("✅ Token & repo OK! Tapi GitHub Pages **belum diaktifkan** untuk repo ni. Pergi Settings → Pages dalam repo kau.")
                    else:
                        st.success("✅ Connected! Token valid, repo accessible, Pages aktif.")
                else:
                    st.error(f"❌ {msg}")
    with col4:
        if st.button("💾 Simpan Settings"):
            if not input_token or not input_repo:
                st.error("Isi token dan repo dulu!")
            else:
                st.session_state["gh_token"] = input_token
                st.session_state["gh_repo"] = input_repo
                st.success("✅ Settings disimpan untuk sesi ini.")

    if st.session_state.get("gh_token") and st.session_state.get("gh_repo"):
        st.markdown("---")
        st.markdown(f"""
        <div class='success-box'>
            <b style='color:#4CAF50'>✅ GitHub Configured</b><br><br>
            📁 Repo: <code>{st.session_state['gh_repo']}</code><br>
            🌐 Pages URL: <code>https://{st.session_state['gh_repo'].split('/')[0]}.github.io/{st.session_state['gh_repo'].split('/')[1]}/</code><br>
            🔑 Token: <code>{'*' * 20}{st.session_state['gh_token'][-4:]}</code>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────
#  PAGE: JANA KAD BARU
# ─────────────────────────────────────────
elif "🆕 Jana Kad Baru" in page:

    st.markdown("# 🆕 Jana Kad Kahwin Digital")
    st.markdown("Isi semua maklumat customer, tekan **Jana & Deploy**, dan dapat link terus!")

    # Check GitHub configured
    gh_token = st.session_state.get("gh_token", "")
    gh_repo = st.session_state.get("gh_repo", "")
    github_ready = bool(gh_token and gh_repo)

    if not github_ready:
        st.markdown("""
        <div class='warning-box'>
            ⚠️ <b>GitHub belum setup.</b> Kad boleh dijana dan di-download, tapi <b>auto-deploy ke link permanent tidak aktif</b>.<br>
            Pergi <b>⚙️ GitHub Settings</b> dalam sidebar untuk setup.
        </div>
        """, unsafe_allow_html=True)
    else:
        username = gh_repo.split('/')[0]
        repo_name = gh_repo.split('/')[1]
        st.markdown(f"""
        <div class='info-box'>
            ✅ GitHub connected → <code>https://{username}.github.io/{repo_name}/</code>
        </div>
        """, unsafe_allow_html=True)

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
        waze_custom = st.text_input("Link Waze (opsional — auto-generate kalau kosong)", placeholder="https://waze.com/ul?...")
    with col8:
        gmap_custom = st.text_input("Link Google Maps (opsional)", placeholder="https://maps.google.com/...")
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
    hero_url = photo1_url = photo2_url = photo3_url = opening_url = ""
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

        # ── VIDEO (Cinematic & Prestige) ──
            if selected_tmpl.get("has_video"):
                st.markdown("---")
                st.markdown("## 🎬 Video Pengantin")
                st.markdown("""
                <div class='info-box'>
                    💡 Upload video ke Google Drive → klik kanan → <b>Get link</b> → tukar sharing ke <b>"Anyone with the link"</b><br>
                    Paste link tu kat bawah.
                </div>
                """, unsafe_allow_html=True)
                video_url = st.text_input("Link Google Drive Video", placeholder="https://drive.google.com/file/d/xxx/view")
            else:
                video_url = ""

        # ── GALLERY (Prestige) ──
            if selected_tmpl.get("has_gallery"):
                st.markdown("---")
                st.markdown("## 🖼️ Gallery Gambar")
                col_g1, col_g2 = st.columns(2)
                with col_g1:
                    gallery1_url = st.text_input("Gambar Gallery 1", placeholder="https://drive.google.com/...")
                    gallery2_url = st.text_input("Gambar Gallery 2", placeholder="https://drive.google.com/...")
                    gallery3_url = st.text_input("Gambar Gallery 3", placeholder="https://drive.google.com/...")
                with col_g2:
                    gallery4_url = st.text_input("Gambar Gallery 4", placeholder="https://drive.google.com/...")
                    gallery5_url = st.text_input("Gambar Gallery 5", placeholder="https://drive.google.com/...")
            else:
                gallery1_url = gallery2_url = gallery3_url = gallery4_url = gallery5_url = ""

    # ── STEP 9: JANA & DEPLOY ──
    st.markdown("## 9️⃣ Jana & Deploy")

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

    # Deploy mode selection
    if github_ready:
        deploy_mode = st.radio(
            "Mode Deploy",
            ["🚀 Jana + Deploy ke GitHub Pages (dapat link terus)", "⬇️ Jana + Download sahaja"],
            horizontal=True
        )
    else:
        deploy_mode = "⬇️ Jana + Download sahaja"
        st.info("💡 Setup GitHub untuk enable auto-deploy.")

    if st.button("✨ Jana Kad Sekarang!", disabled=bool(missing)):
        template_html = load_template(selected_tmpl["file"])

        if template_html is None:
            st.error(f"❌ Template fail tidak dijumpai: `templates/{selected_tmpl['file']}`")
        else:
            order_id = generate_order_id()

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
                "{{VIDEO_URL}}":    video_url,
                "{{GALLERY1_URL}}": gallery1_url,
                "{{GALLERY2_URL}}": gallery2_url,
                "{{GALLERY3_URL}}": gallery3_url,
                "{{GALLERY4_URL}}": gallery4_url,
                "{{GALLERY5_URL}}": gallery5_url,
            }

            if selected_tmpl["has_photo"]:
                replacements.update({
                    "{{HERO_PHOTO_URL}}":    hero_url,
                    "{{PHOTO1_URL}}":        photo1_url,
                    "{{PHOTO2_URL}}":        photo2_url,
                    "{{PHOTO3_URL}}":        photo3_url,
                    "{{OPENING_PHOTO_URL}}": opening_url,
                })

            final_html = apply_replacements(template_html, replacements)
            html_bytes = final_html.encode("utf-8")

            # Generate filename yang cantik & URL-safe
            g = sanitize_filename(groom_name)
            b = sanitize_filename(bride_name)
            filename = f"kad-{g}-{b}-{order_id.lower()}.html"

            # ── DEPLOY TO GITHUB ──
            if "Deploy ke GitHub" in deploy_mode and github_ready:
                with st.spinner("🚀 Deploying ke GitHub Pages..."):
                    result = github_upload_file(
                        token=gh_token,
                        repo=gh_repo,
                        filepath=f"cards/{filename}",
                        content=final_html,
                        commit_msg=f"Add kad: {groom_name} & {bride_name} [{order_id}]"
                    )

                if result["success"]:
                    pages_url = result["pages_url"]
                    st.markdown(f"""
                    <div class='success-box'>
                        <h3 style='color:#4CAF50;margin:0 0 .5rem'>✅ Kad Berjaya Dijana & Deployed!</h3>
                        <span class='order-id'>Order ID: {order_id}</span><br><br>
                        <b>Customer:</b> {groom_name} & {bride_name}<br>
                        <b>Tarikh:</b> {date_display}<br>
                        <b>Template:</b> {selected_tmpl['name']}<br>
                    </div>
                    """, unsafe_allow_html=True)

                    st.markdown(f"""
                    <div class='link-box'>
                        <b style='color:#C9A96E;font-size:0.85rem'>🔗 LINK KAD CUSTOMER</b><br>
                        <a href='{pages_url}' target='_blank' style='color:#4ade80;font-size:1.1rem;font-weight:600;text-decoration:none'>
                            {pages_url}
                        </a><br><br>
                        <small style='color:#666'>⚠️ GitHub Pages ambik 1-2 minit untuk aktif kali pertama. Kalau 404, tunggu sekejap dan refresh.</small>
                    </div>
                    """, unsafe_allow_html=True)

                    st.code(pages_url, language=None)
                    st.caption("☝️ Copy link kat atas untuk hantar ke customer via WhatsApp")

                else:
                    st.error(f"❌ Deploy gagal: {result['error']}")
                    st.info("Fail masih boleh di-download di bawah.")

            else:
                # Download only mode
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

            # Download button sentiasa ada
            st.download_button(
                label="⬇️ Download HTML Kad (backup)",
                data=html_bytes,
                file_name=filename,
                mime="text/html",
                use_container_width=True,
            )

            with st.expander("👁️ Preview HTML (raw)"):
                st.code(final_html[:3000] + "\n\n... [truncated]", language="html")

# ─────────────────────────────────────────
#  PAGE: CARA GUNA
# ─────────────────────────────────────────
elif "📋 Cara Guna" in page:
    st.markdown("# 📋 Cara Guna Admin Dashboard")
    st.markdown("---")
    st.markdown("""
    ## 🔄 Workflow Lengkap (dengan GitHub Auto-Deploy)

    ### 1. Setup GitHub (sekali je)
    - Pergi **⚙️ GitHub Settings** dalam sidebar
    - Ikut langkah setup: buat repo, aktif Pages, jana token
    - Test connection

    ### 2. Terima Order dari Customer
    Customer order melalui website → masuk WhatsApp dengan:
    - Nama pengantin & keluarga
    - Tarikh majlis
    - Template yang dipilih
    - Gambar (kalau Portrait)
    - Lagu pilihan

    ### 3. Host Lagu Customer
    Customer hantar MP3 → upload ke GitHub repo public:
    ```
    https://cdn.jsdelivr.net/gh/USERNAME/REPO@main/assets/NAMA_LAGU.mp3
    ```

    ### 4. Jana Kad dalam App
    - Isi semua maklumat customer
    - Pilih **"Jana + Deploy ke GitHub Pages"**
    - Klik **Jana Kad Sekarang!**

    ### 5. Hantar Link ke Customer
    - Link terus keluar dalam app selepas deploy
    - Copy dan hantar via WhatsApp
    - Link format: `https://USERNAME.github.io/REPO/cards/kad-xxxxx.html`
    - ⚠️ Tunggu 1-2 minit kali pertama untuk GitHub Pages aktif

    ---

    ## 📁 Setup Template Baru

    1. Buat HTML template baru dengan **placeholders** `{{GROOM_NAME}}` etc
    2. Letak dalam folder `templates/`
    3. Daftar dalam `TEMPLATES` dict dalam `app.py`

    ### Senarai Semua Placeholders
    """)

    for placeholder, desc in PLACEHOLDERS.items():
        st.markdown(f"- `{placeholder}` — {desc}")

# ─────────────────────────────────────────
#  PAGE: TEMPLATE INFO
# ─────────────────────────────────────────
elif "🗂️ Template Info" in page:
    st.markdown("# 🗂️ Senarai Template")
    st.markdown("---")

    for category, templates in TEMPLATES.items():
        st.markdown(f"## {'⭐' if category == 'Essential' else '📸' if category == 'Portrait' else '✨'} {category}")
        for key, info in templates.items():
            file_exists = (BASE_DIR / "templates" / info['file']).exists()
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
            "file": "nama_fail.html",
            "has_photo": True,  # atau False
            "preview_emoji": "✨",
            "desc": "Penerangan ringkas",
        },
    },
    ```
    """)
