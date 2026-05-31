import streamlit as st
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
        color: white; border: none; border-radius: 8px;
        font-weight: 600; padding: 0.6rem 1.5rem; width: 100%;
    }
    .stButton > button:hover { opacity: 0.9; }
    .stButton > button:disabled { opacity: 0.4; cursor: not-allowed; }
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        background: #1e1e1e !important; color: #f0e8d8 !important;
        border: 1px solid #333 !important; border-radius: 8px !important;
    }
    .stNumberInput > div > div > input { background: #1e1e1e !important; color: #f0e8d8 !important; }
    .success-box {
        background: linear-gradient(135deg, #1a2e1a, #0f1f0f);
        border: 1px solid #2d5a2d; border-radius: 12px; padding: 1.5rem; margin: 1rem 0;
    }
    .info-box {
        background: linear-gradient(135deg, #1a1a2e, #0f0f1f);
        border: 1px solid #2d2d5a; border-radius: 12px;
        padding: 1rem; margin: .5rem 0; font-size: 0.85rem; color: #a0a8c0;
    }
    .warning-box {
        background: linear-gradient(135deg, #2e2a1a, #1f1a0f);
        border: 1px solid #5a4a2d; border-radius: 12px;
        padding: 1rem; margin: .5rem 0; font-size: 0.85rem; color: #c0b08a;
    }
    .link-box {
        background: linear-gradient(135deg, #0f2e1a, #0a1f12);
        border: 1px solid #1a5a32; border-radius: 12px;
        padding: 1.2rem 1.5rem; margin: 1rem 0; word-break: break-all;
    }
    .template-card {
        background: #1e1e1e; border: 1px solid #333;
        border-radius: 12px; padding: 1rem; margin: .5rem 0;
    }
    .category-badge {
        display: inline-block; background: rgba(201,169,110,0.15);
        border: 1px solid rgba(201,169,110,0.3); border-radius: 20px;
        padding: 2px 10px; font-size: 0.75rem; color: #C9A96E; margin-bottom: 0.5rem;
    }
    .order-id {
        font-family: monospace; background: #2a2a2a;
        padding: 4px 10px; border-radius: 6px; color: #C9A96E; font-size: 0.85rem;
    }
    div[data-testid="stExpander"] {
        background: #1a1a1a; border: 1px solid #333; border-radius: 10px;
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
    },
}

# ─────────────────────────────────────────
#  PLACEHOLDER OPTIONS (untuk Template Converter)
#  Key   = label yang dipapar kat user
#  Value = placeholder {{CURLY}} dalam template HTML
# ─────────────────────────────────────────
PLACEHOLDER_OPTIONS = {
    "-- Pilih Placeholder --": "",
    "{{GROOM_NAME}} — Nama pengantin lelaki":                   "{{GROOM_NAME}}",
    "{{BRIDE_NAME}} — Nama pengantin perempuan":                "{{BRIDE_NAME}}",
    "{{FATHER_NAME}} — Nama bapa / tuan rumah":                 "{{FATHER_NAME}}",
    "{{MOTHER_NAME}} — Nama ibu / tuan rumah":                  "{{MOTHER_NAME}}",
    "{{DATE_DISPLAY}} — Tarikh papar (eg: 10 Ogos 2026)":       "{{DATE_DISPLAY}}",
    "{{DATE_DAY}} — Hari majlis (eg: Isnin)":                   "{{DATE_DAY}}",
    "{{DATE_HIJRI}} — Tarikh Hijri (eg: 15 Safar 1448H)":       "{{DATE_HIJRI}}",
    "{{DATE_ISO}} — Tarikh ISO countdown (2026-08-10T12:00:00)":"{{DATE_ISO}}",
    "{{DATE_DD}} — Nombor hari (eg: 10)":                       "{{DATE_DD}}",
    "{{DATE_MM}} — Nombor bulan (eg: 08)":                      "{{DATE_MM}}",
    "{{DATE_YYYY}} — Tahun (eg: 2026)":                         "{{DATE_YYYY}}",
    "{{TIME_DISPLAY}} — Masa majlis (eg: 12:00 Tengahari)":     "{{TIME_DISPLAY}}",
    "{{VENUE_NAME}} — Nama dewan / tempat":                     "{{VENUE_NAME}}",
    "{{VENUE_ADDRESS}} — Alamat penuh venue":                   "{{VENUE_ADDRESS}}",
    "{{VENUE_CITY}} — Bandar / negeri":                         "{{VENUE_CITY}}",
    "{{WAZE_LINK}} — Link Waze penuh":                          "{{WAZE_LINK}}",
    "{{GMAP_LINK}} — Link Google Maps penuh":                   "{{GMAP_LINK}}",
    "{{CONTACT_PHONE}} — No telefon (eg: 011-3562 3312)":       "{{CONTACT_PHONE}}",
    "{{CONTACT_PHONE_WA}} — No WA tanpa + (eg: 601135623312)":  "{{CONTACT_PHONE_WA}}",
    "{{MUSIC_URL}} — Link direct MP3":                          "{{MUSIC_URL}}",
    "{{MUSIC_LABEL}} — Nama lagu":                              "{{MUSIC_LABEL}}",
    "{{HERO_PHOTO_URL}} — Link gambar hero":                    "{{HERO_PHOTO_URL}}",
    "{{PHOTO1_URL}} — Link gallery gambar 1":                   "{{PHOTO1_URL}}",
    "{{PHOTO2_URL}} — Link gallery gambar 2":                   "{{PHOTO2_URL}}",
    "{{PHOTO3_URL}} — Link gallery gambar 3":                   "{{PHOTO3_URL}}",
    "{{OPENING_PHOTO_URL}} — Link gambar opening":              "{{OPENING_PHOTO_URL}}",
    "{{VIDEO_URL}} — Link video Google Drive":                  "{{VIDEO_URL}}",
    "{{GALLERY1_URL}} — Link gallery 1":                        "{{GALLERY1_URL}}",
    "{{GALLERY2_URL}} — Link gallery 2":                        "{{GALLERY2_URL}}",
    "{{GALLERY3_URL}} — Link gallery 3":                        "{{GALLERY3_URL}}",
    "{{GALLERY4_URL}} — Link gallery 4":                        "{{GALLERY4_URL}}",
    "{{GALLERY5_URL}} — Link gallery 5":                        "{{GALLERY5_URL}}",
}

# ─────────────────────────────────────────
#  GITHUB HELPER FUNCTIONS
# ─────────────────────────────────────────
def github_upload_file(token, repo, filepath, content, commit_msg):
    api_url = f"https://api.github.com/repos/{repo}/contents/{filepath}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    sha = None
    r = requests.get(api_url, headers=headers, timeout=15)
    if r.status_code == 200:
        sha = r.json().get("sha")
    content_b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    payload = {"message": commit_msg, "content": content_b64}
    if sha:
        payload["sha"] = sha
    r = requests.put(api_url, headers=headers, json=payload, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        raw_url = data["content"]["download_url"]
        parts = raw_url.replace("https://raw.githubusercontent.com/", "").split("/")
        user = parts[0]
        repo_name = parts[1]
        file_path = "/".join(parts[3:])
        pages_url = f"https://{user}.github.io/{repo_name}/{file_path}"
        return {"success": True, "pages_url": pages_url, "raw_url": raw_url}
    else:
        try:
            err = r.json().get("message", r.text)
        except Exception:
            err = r.text
        return {"success": False, "error": f"GitHub API error {r.status_code}: {err}"}

def validate_github_token(token, repo):
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    r = requests.get(f"https://api.github.com/repos/{repo}", headers=headers, timeout=10)
    if r.status_code == 200:
        has_pages = r.json().get("has_pages", False)
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
def load_template(filename):
    path = BASE_DIR / "templates" / filename
    if not path.exists():
        return None
    return path.read_text(encoding="utf-8")

def apply_replacements(html, data):
    # Sort by key length DESC — replace yang lebih spesifik/panjang dulu
    for key, val in sorted(data.items(), key=lambda x: len(x[0]), reverse=True):
        if val is not None and val != "":
            html = html.replace(key, str(val))
    return html

def generate_order_id():
    return f"EQ{datetime.now().strftime('%y%m%d%H%M')}"

def file_to_data_url(uploaded_file):
    b64 = base64.b64encode(uploaded_file.read()).decode()
    return f"data:{uploaded_file.type};base64,{b64}"

def get_whatsapp_number(phone):
    phone = re.sub(r'\D', '', phone)
    if phone.startswith('0'):
        phone = '60' + phone[1:]
    elif not phone.startswith('60'):
        phone = '60' + phone
    return phone

def get_waze_link(venue_name, address):
    q = f"{venue_name} {address}".replace(' ', '+')
    return f"https://waze.com/ul?q={q}&navigate=yes"

def get_gmap_link(venue_name, address):
    q = f"{venue_name} {address}".replace(' ', '+')
    return f"https://maps.google.com/?q={q}"

def sanitize_filename(name):
    name = name.lower().strip()
    name = re.sub(r'[^a-z0-9]+', '-', name)
    return name.strip('-')

# ─────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💍 EQStudio Admin")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["🆕 Jana Kad Baru", "🔧 Template Converter", "⚙️ GitHub Settings", "📋 Cara Guna", "🗂️ Template Info"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    gh_token = st.session_state.get("gh_token", "") or st.secrets.get("GH_TOKEN", "")
    gh_repo  = st.session_state.get("gh_repo",  "") or st.secrets.get("GH_REPO",  "")
    if gh_token and gh_repo:
        st.markdown("<div style='font-size:0.75rem;color:#4CAF50'>✅ <b style='color:#C9A96E'>GitHub</b> Connected</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.7rem;color:#666;margin-top:2px'>📁 {gh_repo}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-size:0.75rem;color:#888'>⚠️ GitHub belum setup<br><small>Pergi ⚙️ GitHub Settings</small></div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<div style='font-size:0.75rem;color:#666'><b style='color:#C9A96E'>EQStudio</b><br>Admin Dashboard v2.1<br>Kad Kahwin Digital</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  PAGE: GITHUB SETTINGS
# ─────────────────────────────────────────
if "⚙️ GitHub Settings" in page:
    st.markdown("# ⚙️ GitHub Settings")
    st.markdown("Setup sekali, guna selama-lamanya. Kad customer akan auto-deploy ke GitHub Pages.")
    st.markdown("---")
    with st.expander("📋 Langkah-langkah setup (klik untuk buka)", expanded=True):
        st.markdown("""
        ### 1️⃣ Buat repo baru di GitHub
        Pergi [github.com/new](https://github.com/new):
        - **Repository name:** contoh `eqstudio-cards`
        - **Visibility:** ✅ **Public**
        - Tick **"Add a README file"**
        - Klik **Create repository**

        ### 2️⃣ Aktifkan GitHub Pages
        - Pergi **Settings → Pages**
        - **Source:** Deploy from a branch → `main` → `/` (root)
        - Klik **Save**

        ### 3️⃣ Jana GitHub Token
        Pergi [github.com/settings/tokens/new](https://github.com/settings/tokens/new):
        - **Expiration:** No expiration
        - **Scopes:** Tick ✅ `repo`
        - **COPY TOKEN SEKARANG**

        ### 4️⃣ Isi details kat bawah
        """)
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        input_token = st.text_input("GitHub Personal Access Token", type="password",
            value=st.session_state.get("gh_token", ""), placeholder="ghp_xxxxxxxxxxxxxxxxxxxx")
    with col2:
        input_repo = st.text_input("GitHub Repo (username/repo-name)",
            value=st.session_state.get("gh_repo", ""), placeholder="nureqmal/eqstudio-cards")
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
                        st.warning("✅ Token OK! Tapi GitHub Pages belum diaktifkan.")
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
                st.success("✅ Settings disimpan.")
    if st.session_state.get("gh_token") and st.session_state.get("gh_repo"):
        st.markdown("---")
        r = st.session_state['gh_repo']
        st.markdown(f"""
        <div class='success-box'>
            <b style='color:#4CAF50'>✅ GitHub Configured</b><br><br>
            📁 Repo: <code>{r}</code><br>
            🌐 Pages: <code>https://{r.split('/')[0]}.github.io/{r.split('/')[1]}/</code><br>
            🔑 Token: <code>{'*'*20}{st.session_state['gh_token'][-4:]}</code>
        </div>
        """, unsafe_allow_html=True)

# ─────────────────────────────────────────
#  PAGE: JANA KAD BARU
# ─────────────────────────────────────────
elif "🆕 Jana Kad Baru" in page:
    st.markdown("# 🆕 Jana Kad Kahwin Digital")
    st.markdown("Isi semua maklumat customer, tekan **Jana & Deploy**, dan dapat link terus!")

    gh_token = st.session_state.get("gh_token", "") or st.secrets.get("GH_TOKEN", "")
    gh_repo  = st.session_state.get("gh_repo",  "") or st.secrets.get("GH_REPO",  "")
    github_ready = bool(gh_token and gh_repo)

    if not github_ready:
        st.markdown("<div class='warning-box'>⚠️ <b>GitHub belum setup.</b> Pergi <b>⚙️ GitHub Settings</b>.</div>", unsafe_allow_html=True)
    else:
        u, r = gh_repo.split('/')
        st.markdown(f"<div class='info-box'>✅ GitHub connected → <code>https://{u}.github.io/{r}/</code></div>", unsafe_allow_html=True)

    st.markdown("---")

    # STEP 1: TEMPLATE
    st.markdown("## 1️⃣ Pilih Template")
    cat_selected = st.selectbox("Pilih Category", list(TEMPLATES.keys()),
        format_func=lambda x: f"{'⭐' if x=='Essential' else '📸' if x=='Portrait' else '🎬' if x=='Cinematic' else '💎'} {x}")
    tmpl_options = TEMPLATES[cat_selected]
    tmpl_key = st.selectbox("Pilih Template", list(tmpl_options.keys()),
        format_func=lambda k: f"{tmpl_options[k]['preview_emoji']}  {tmpl_options[k]['name']}")
    selected_tmpl = tmpl_options[tmpl_key]
    st.markdown(f"""
    <div class='info-box'>
        <span class='category-badge'>{cat_selected}</span><br>
        <b style='color:#f0e8d8'>{selected_tmpl['preview_emoji']} {selected_tmpl['name']}</b><br>
        {selected_tmpl['desc']}<br>
        {'📸 Template ini memerlukan gambar' if selected_tmpl.get('has_photo') else '🎨 Template tanpa gambar'}
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    # STEP 2: PENGANTIN
    st.markdown("## 2️⃣ Maklumat Pengantin")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**🤵 Pengantin Lelaki**")
        groom_name = st.text_input("Nama Panggilan", placeholder="Ahmad", key="groom")
        groom_full = st.text_input("Nama Penuh", placeholder="Ahmad bin Abdullah", key="groom_full")
    with col2:
        st.markdown("**👰 Pengantin Perempuan**")
        bride_name = st.text_input("Nama Panggilan", placeholder="Sarah", key="bride")
        bride_full = st.text_input("Nama Penuh", placeholder="Sarah binti Ibrahim", key="bride_full")
    st.markdown("---")

    # STEP 3: TUAN RUMAH
    st.markdown("## 3️⃣ Maklumat Tuan Rumah")
    col3, col4 = st.columns(2)
    with col3:
        father_name  = st.text_input("Nama Bapa (Lelaki)", placeholder="Abdullah bin Salleh")
        mother_name  = st.text_input("Nama Ibu (Lelaki)", placeholder="Siti binti Ahmad")
    with col4:
        father_bride = st.text_input("Nama Bapa (Perempuan)", placeholder="Ibrahim bin Hassan")
        mother_bride = st.text_input("Nama Ibu (Perempuan)", placeholder="Aminah binti Yusof")
        parent_side  = st.selectbox("Pihak Tuan Rumah", ["Perempuan", "Lelaki", "Perempuan & Lelaki"])

    # Tentukan FATHER_NAME & MOTHER_NAME ikut pihak tuan rumah
    if parent_side == "Lelaki":
        host_father = father_name
        host_mother = mother_name
    elif parent_side == "Perempuan":
        host_father = father_bride or father_name
        host_mother = mother_bride or mother_name
    else:  # Perempuan & Lelaki
        host_father = f"{father_name} & {father_bride}" if father_bride else father_name
        host_mother = f"{mother_name} & {mother_bride}" if mother_bride else mother_name

    st.markdown("---")

    # STEP 4: TARIKH
    st.markdown("## 4️⃣ Tarikh & Masa Majlis")
    col5, col6 = st.columns(2)
    with col5:
        event_date = st.date_input("Tarikh Majlis")
        event_time = st.time_input("Masa Majlis")
        hijri_date = st.text_input("Tarikh Hijri", placeholder="15 Safar 1448H")
    with col6:
        days_ms   = ["Isnin","Selasa","Rabu","Khamis","Jumaat","Sabtu","Ahad"]
        months_ms = ["","Januari","Februari","Mac","April","Mei","Jun","Julai","Ogos","September","Oktober","November","Disember"]
        day_name     = days_ms[event_date.weekday()]
        date_display = f"{event_date.day} {months_ms[event_date.month]} {event_date.year}"
        date_iso     = f"{event_date.isoformat()}T{event_time.strftime('%H:%M:%S')}+08:00"
        time_display = event_time.strftime('%H:%M')
        st.markdown(f"""
        <div class='info-box'>
            <b style='color:#C9A96E'>Preview:</b><br>
            📅 {day_name}, {date_display}<br>
            🕐 {time_display}<br>
            🗓️ {hijri_date if hijri_date else '—'}<br>
            <small style='opacity:0.5'>ISO: {date_iso}</small>
        </div>
        """, unsafe_allow_html=True)
    st.markdown("---")

    # STEP 5: LOKASI
    st.markdown("## 5️⃣ Lokasi Majlis")
    venue_name    = st.text_input("Nama Dewan / Tempat", placeholder="Dewan Seri Kenangan")
    venue_address = st.text_area("Alamat Penuh", placeholder="No 1, Jalan Bahagia, 43000 Kajang, Selangor", height=80)
    venue_city    = st.text_input("Bandar / Negeri (ringkas)", placeholder="Kajang, Selangor")
    col7, col8 = st.columns(2)
    with col7:
        waze_custom = st.text_input("Link Waze (kosong = auto)", placeholder="https://waze.com/ul?...")
    with col8:
        gmap_custom = st.text_input("Link Google Maps (kosong = auto)", placeholder="https://maps.google.com/...")
    waze_link = waze_custom if waze_custom else (get_waze_link(venue_name, venue_address) if venue_name else "")
    gmap_link = gmap_custom if gmap_custom else (get_gmap_link(venue_name, venue_address) if venue_name else "")
    st.markdown("---")

    # STEP 6: CONTACT
    st.markdown("## 6️⃣ Contact Person")
    col9, col10 = st.columns(2)
    with col9:
        contact_name  = st.text_input("Nama Contact Person", placeholder="Abdullah bin Salleh")
        contact_phone = st.text_input("No Telefon", placeholder="011-12345678")
    with col10:
        wa_num = get_whatsapp_number(contact_phone) if contact_phone else ""
        if contact_phone:
            st.markdown(f"<div class='info-box'>📱 WhatsApp: <b>{wa_num}</b></div>", unsafe_allow_html=True)
    st.markdown("---")

    # STEP 7: LAGU
    st.markdown("## 7️⃣ Lagu Latar")
    st.markdown("<div class='info-box'>💡 Host MP3 di GitHub → guna jsDelivr: <code>https://cdn.jsdelivr.net/gh/USERNAME/REPO@main/lagu.mp3</code></div>", unsafe_allow_html=True)
    music_url   = st.text_input("Link Direct MP3", placeholder="https://cdn.jsdelivr.net/gh/...")
    music_label = st.text_input("Nama Lagu", placeholder="Beautiful In White — Westlife")
    st.markdown("---")

    # STEP 8: GAMBAR
    hero_url = photo1_url = photo2_url = photo3_url = opening_url = ""
    if selected_tmpl.get("has_photo"):
        st.markdown("## 8️⃣ Gambar Pengantin")
        photo_method = st.radio("Cara masukkan gambar", ["📎 Upload File", "🔗 Paste Link URL"], horizontal=True)
        if photo_method == "📎 Upload File":
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                hero_file    = st.file_uploader("🖼️ Hero Background", type=["jpg","jpeg","png","webp"], key="hero")
                photo1_file  = st.file_uploader("📸 Gallery Foto 1", type=["jpg","jpeg","png","webp"], key="p1")
                opening_file = st.file_uploader("🎴 Opening Photo", type=["jpg","jpeg","png","webp"], key="op")
            with col_p2:
                photo2_file = st.file_uploader("📸 Gallery Foto 2", type=["jpg","jpeg","png","webp"], key="p2")
                photo3_file = st.file_uploader("📸 Gallery Foto 3", type=["jpg","jpeg","png","webp"], key="p3")
            if hero_file:    hero_url    = file_to_data_url(hero_file)
            if photo1_file:  photo1_url  = file_to_data_url(photo1_file)
            if photo2_file:  photo2_url  = file_to_data_url(photo2_file)
            if photo3_file:  photo3_url  = file_to_data_url(photo3_file)
            if opening_file: opening_url = file_to_data_url(opening_file)
        else:
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                hero_url    = st.text_input("🖼️ Hero URL",      placeholder="https://...")
                photo1_url  = st.text_input("📸 Gallery 1 URL", placeholder="https://...")
                opening_url = st.text_input("🎴 Opening URL",   placeholder="https://...")
            with col_p2:
                photo2_url = st.text_input("📸 Gallery 2 URL", placeholder="https://...")
                photo3_url = st.text_input("📸 Gallery 3 URL", placeholder="https://...")
        st.markdown("---")

    # VIDEO
    video_url = ""
    if selected_tmpl.get("has_video"):
        st.markdown("## 🎬 Video Pengantin")
        st.markdown("<div class='info-box'>💡 Upload ke Google Drive → Get link → Anyone with the link</div>", unsafe_allow_html=True)
        video_url = st.text_input("Link Google Drive Video", placeholder="https://drive.google.com/file/d/xxx/view")
        st.markdown("---")

    # GALLERY
    gallery1_url = gallery2_url = gallery3_url = gallery4_url = gallery5_url = ""
    if selected_tmpl.get("has_gallery"):
        st.markdown("## 🖼️ Gallery Gambar")
        col_g1, col_g2 = st.columns(2)
        with col_g1:
            gallery1_url = st.text_input("Gallery 1", placeholder="https://drive.google.com/...")
            gallery2_url = st.text_input("Gallery 2", placeholder="https://drive.google.com/...")
            gallery3_url = st.text_input("Gallery 3", placeholder="https://drive.google.com/...")
        with col_g2:
            gallery4_url = st.text_input("Gallery 4", placeholder="https://drive.google.com/...")
            gallery5_url = st.text_input("Gallery 5", placeholder="https://drive.google.com/...")
        st.markdown("---")

    # STEP 9: JANA
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

    if github_ready:
        deploy_mode = st.radio("Mode Deploy",
            ["🚀 Jana + Deploy ke GitHub Pages", "⬇️ Jana + Download sahaja"], horizontal=True)
    else:
        deploy_mode = "⬇️ Jana + Download sahaja"
        st.info("💡 Setup GitHub untuk enable auto-deploy.")

    if st.button("✨ Jana Kad Sekarang!", disabled=bool(missing)):
        template_html = load_template(selected_tmpl["file"])
        if template_html is None:
            st.error(f"❌ Template fail tidak dijumpai: `templates/{selected_tmpl['file']}`")
        else:
            order_id = generate_order_id()

            # ── REPLACEMENTS — format {{CURLY}} selaras dengan templates ──
            replacements = {
                "{{GROOM_NAME}}":       groom_name,
                "{{BRIDE_NAME}}":       bride_name,
                "{{FATHER_NAME}}":      host_father,
                "{{MOTHER_NAME}}":      host_mother,
                # Tarikh
                "{{DATE_DISPLAY}}":     date_display,
                "{{DATE_DAY}}":         day_name,
                "{{DATE_HIJRI}}":       hijri_date,
                "{{DATE_ISO}}":         date_iso,
                "{{DATE_DD}}":          str(event_date.day).zfill(2),
                "{{DATE_MM}}":          str(event_date.month).zfill(2),
                "{{DATE_YYYY}}":        str(event_date.year),
                # Masa
                "{{TIME_DISPLAY}}":     time_display,
                # Venue
                "{{VENUE_NAME}}":       venue_name,
                "{{VENUE_ADDRESS}}":    venue_address,
                "{{VENUE_CITY}}":       venue_city or venue_name,
                "{{WAZE_LINK}}":        waze_link,
                "{{GMAP_LINK}}":        gmap_link,
                # Contact
                "{{CONTACT_PHONE}}":    contact_phone,
                "{{CONTACT_PHONE_WA}}": wa_num,
                # Lagu
                "{{MUSIC_URL}}":        music_url,
                "{{MUSIC_LABEL}}":      music_label,
                # Media
                "{{HERO_PHOTO_URL}}":   hero_url,
                "{{PHOTO1_URL}}":       photo1_url,
                "{{PHOTO2_URL}}":       photo2_url,
                "{{PHOTO3_URL}}":       photo3_url,
                "{{OPENING_PHOTO_URL}}":opening_url,
                "{{VIDEO_URL}}":        video_url,
                "{{GALLERY1_URL}}":     gallery1_url,
                "{{GALLERY2_URL}}":     gallery2_url,
                "{{GALLERY3_URL}}":     gallery3_url,
                "{{GALLERY4_URL}}":     gallery4_url,
                "{{GALLERY5_URL}}":     gallery5_url,
            }

            final_html = apply_replacements(template_html, replacements)
            html_bytes = final_html.encode("utf-8")
            g = sanitize_filename(groom_name)
            b = sanitize_filename(bride_name)
            filename = f"kad-{g}-{b}-{order_id.lower()}.html"

            if "Deploy ke GitHub" in deploy_mode and github_ready:
                with st.spinner("🚀 Deploying ke GitHub Pages..."):
                    result = github_upload_file(gh_token, gh_repo, f"cards/{filename}", final_html,
                        f"Add kad: {groom_name} & {bride_name} [{order_id}]")
                if result["success"]:
                    pages_url = result["pages_url"]
                    st.markdown(f"""
                    <div class='success-box'>
                        <h3 style='color:#4CAF50;margin:0 0 .5rem'>✅ Kad Berjaya Dijana & Deployed!</h3>
                        <span class='order-id'>Order ID: {order_id}</span><br><br>
                        <b>Customer:</b> {groom_name} & {bride_name}<br>
                        <b>Tarikh:</b> {date_display}<br>
                        <b>Template:</b> {selected_tmpl['name']}
                    </div>
                    """, unsafe_allow_html=True)
                    st.markdown(f"""
                    <div class='link-box'>
                        <b style='color:#C9A96E;font-size:0.85rem'>🔗 LINK KAD CUSTOMER</b><br>
                        <a href='{pages_url}' target='_blank' style='color:#4ade80;font-size:1.1rem;font-weight:600;text-decoration:none'>{pages_url}</a><br><br>
                        <small style='color:#666'>⚠️ GitHub Pages ambik 1-2 minit kali pertama. Kalau 404, tunggu dan refresh.</small>
                    </div>
                    """, unsafe_allow_html=True)
                    st.code(pages_url, language=None)
                else:
                    st.error(f"❌ Deploy gagal: {result['error']}")
            else:
                st.markdown(f"""
                <div class='success-box'>
                    <h3 style='color:#4CAF50;margin:0 0 .5rem'>✅ Kad Berjaya Dijana!</h3>
                    <span class='order-id'>Order ID: {order_id}</span><br><br>
                    <b>Customer:</b> {groom_name} & {bride_name}<br>
                    <b>Tarikh:</b> {date_display}
                </div>
                """, unsafe_allow_html=True)

            st.download_button("⬇️ Download HTML Kad", data=html_bytes,
                file_name=filename, mime="text/html", use_container_width=True)

            with st.expander("👁️ Preview HTML (raw)"):
                st.code(final_html[:3000] + "\n\n... [truncated]", language="html")

# ─────────────────────────────────────────
#  PAGE: TEMPLATE CONVERTER
# ─────────────────────────────────────────
elif "🔧 Template Converter" in page:
    st.markdown("# 🔧 Template Converter")
    st.markdown("Upload HTML template, map nilai hardcoded ke placeholders `{{CURLY}}`, auto-upload ke GitHub.")
    st.markdown("---")

    st.markdown("## 1️⃣ Upload HTML Template")
    uploaded_html = st.file_uploader("Upload fail HTML", type=["html","htm"])

    if uploaded_html:
        raw_html = uploaded_html.read().decode("utf-8")
        st.success(f"✅ Fail dibaca — {len(raw_html):,} characters")
        st.markdown("---")

        st.markdown("## 2️⃣ Map Nilai → Placeholder")
        st.markdown(
            "<div class='info-box'>Masukkan nilai hardcoded dalam template "
            "(eg: <b>Eqmal</b>), kemudian pilih placeholder <b>{{CURLY}}</b> yang sesuai.</div>",
            unsafe_allow_html=True
        )

        if "converter_rows" not in st.session_state:
            st.session_state.converter_rows = [{"value": "", "placeholder": ""}]

        col_add, col_remove, _ = st.columns([1, 1, 4])
        with col_add:
            if st.button("➕ Tambah baris"):
                st.session_state.converter_rows.append({"value": "", "placeholder": ""})
                st.rerun()
        with col_remove:
            if st.button("➖ Buang baris") and len(st.session_state.converter_rows) > 1:
                st.session_state.converter_rows.pop()
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        col_h1, col_h2, col_h3 = st.columns([2, 3, 1])
        with col_h1: st.markdown("**Nilai dalam HTML**")
        with col_h2: st.markdown("**Ganti dengan Placeholder**")
        with col_h3: st.markdown("**Jumpa?**")

        for i, row in enumerate(st.session_state.converter_rows):
            col1, col2, col3 = st.columns([2, 3, 1])
            with col1:
                val = st.text_input(f"Nilai {i+1}", value=row["value"],
                    placeholder="cth: Eqmal", key=f"conv_val_{i}", label_visibility="collapsed")
                st.session_state.converter_rows[i]["value"] = val
            with col2:
                ph_label = st.selectbox(f"Placeholder {i+1}", list(PLACEHOLDER_OPTIONS.keys()),
                    key=f"conv_ph_{i}", label_visibility="collapsed")
                st.session_state.converter_rows[i]["placeholder"] = PLACEHOLDER_OPTIONS[ph_label]
            with col3:
                if val and val in raw_html:
                    count = raw_html.count(val)
                    st.markdown(f"<div style='color:#4CAF50;padding-top:8px'>✅ {count}x</div>", unsafe_allow_html=True)
                elif val:
                    st.markdown("<div style='color:#ff6b6b;padding-top:8px'>❌ Tak jumpa</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='color:#666;padding-top:8px'>—</div>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("## 3️⃣ Preview Conversion")

        valid_mappings = [r for r in st.session_state.converter_rows
            if r["value"] and r["placeholder"] and r["value"] in raw_html]
        not_found = [r for r in st.session_state.converter_rows
            if r["value"] and r["placeholder"] and r["value"] not in raw_html]

        if valid_mappings:
            st.markdown(
                f"<div class='info-box'>✅ <b>{len(valid_mappings)} replacement</b> akan dibuat"
                f"{'<br>⚠️ ' + str(len(not_found)) + ' nilai tidak dijumpai' if not_found else ''}"
                f"</div>", unsafe_allow_html=True
            )
            for m in valid_mappings:
                count = raw_html.count(m['value'])
                st.markdown(f"- `{m['value']}` → `{m['placeholder']}` ({count} tempat)")
        else:
            st.warning("⚠️ Belum ada mapping yang valid. Pastikan nilai yang dimasukkan tepat sama seperti dalam HTML.")

        st.markdown("---")
        st.markdown("## 4️⃣ Info Template Baru")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            tmpl_category = st.selectbox("Category", ["Essential","Portrait","Cinematic","Prestige"])
            tmpl_name     = st.text_input("Nama Template", placeholder="cth: Sakura — Tema Bunga Jepun")
            tmpl_emoji    = st.text_input("Emoji", placeholder="🌸", max_chars=2)
        with col_t2:
            tmpl_desc     = st.text_input("Penerangan Ringkas", placeholder="cth: Tema minimalis, pink & white")
            tmpl_filename = st.text_input("Nama Fail (tanpa .html)", placeholder="cth: v5_sakura")
            if tmpl_filename:
                safe_name = re.sub(r'[^a-z0-9_]', '_', tmpl_filename.lower().strip())
                if safe_name != tmpl_filename:
                    st.caption(f"✏️ Akan disimpan sebagai: `{safe_name}.html`")
                    tmpl_filename = safe_name

        st.markdown("---")
        st.markdown("## 5️⃣ Convert & Upload ke GitHub")

        gh_token = st.session_state.get("gh_token", "") or st.secrets.get("GH_TOKEN", "")
        gh_repo  = st.session_state.get("gh_repo",  "") or st.secrets.get("GH_REPO",  "")

        if not gh_token or not gh_repo:
            st.markdown("<div class='warning-box'>⚠️ GitHub belum setup. Pergi <b>⚙️ GitHub Settings</b>.</div>", unsafe_allow_html=True)

        can_convert = bool(valid_mappings and tmpl_name and tmpl_filename and gh_token and gh_repo)
        if not can_convert:
            missing_things = []
            if not valid_mappings: missing_things.append("mapping values")
            if not tmpl_name: missing_things.append("nama template")
            if not tmpl_filename: missing_things.append("nama fail")
            if not gh_token or not gh_repo: missing_things.append("GitHub settings")
            st.warning(f"⚠️ Sila lengkapkan: {', '.join(missing_things)}")

        if st.button("🚀 Convert & Upload Template!", disabled=not can_convert):
            converted_html = raw_html
            for mapping in sorted(valid_mappings, key=lambda x: len(x["value"]), reverse=True):
                converted_html = converted_html.replace(mapping["value"], mapping["placeholder"])

            final_filename = f"{tmpl_filename}.html"
            with st.spinner("📤 Uploading template ke GitHub..."):
                result = github_upload_file(gh_token, gh_repo,
                    f"eqstudio_admin_new/templates/{final_filename}",
                    converted_html, f"Add template: {tmpl_name} [{final_filename}]")

            if result["success"]:
                has_photo_val   = tmpl_category in ["Portrait","Cinematic","Prestige"]
                has_video_val   = tmpl_category in ["Cinematic","Prestige"]
                has_gallery_val = tmpl_category == "Prestige"

                code  = f'        "{tmpl_filename}": {{\n'
                code += f'            "name": "{tmpl_name}",\n'
                code += f'            "file": "{final_filename}",\n'
                code += f'            "has_photo": {has_photo_val},\n'
                if has_video_val:   code += f'            "has_video": True,\n'
                if has_gallery_val: code += f'            "has_gallery": True,\n'
                code += f'            "preview_emoji": "{tmpl_emoji or "✨"}",\n'
                code += f'            "desc": "{tmpl_desc}",\n'
                code += f'        }},'

                st.markdown(f"""
                <div class='success-box'>
                    <h3 style='color:#4CAF50;margin:0 0 .5rem'>✅ Template Berjaya Diupload!</h3>
                    <b>Nama:</b> {tmpl_name}<br>
                    <b>Fail:</b> {final_filename}<br>
                    <b>Replacements:</b> {len(valid_mappings)}
                </div>
                """, unsafe_allow_html=True)
                st.markdown("### 📋 Tambah dalam TEMPLATES dict:")
                st.code(f'# Letak dalam "{tmpl_category}" section:\n{code}', language="python")
                st.session_state.converter_rows = [{"value": "", "placeholder": ""}]
            else:
                st.error(f"❌ Upload gagal: {result['error']}")

        if valid_mappings:
            with st.expander("👁️ Preview HTML selepas conversion"):
                preview = raw_html
                for m in sorted(valid_mappings, key=lambda x: len(x["value"]), reverse=True):
                    preview = preview.replace(m["value"], m["placeholder"])
                st.code(preview[:3000] + "\n\n... [truncated]", language="html")

# ─────────────────────────────────────────
#  PAGE: CARA GUNA
# ─────────────────────────────────────────
elif "📋 Cara Guna" in page:
    st.markdown("# 📋 Cara Guna Admin Dashboard")
    st.markdown("---")
    st.markdown("""
    ## 🔄 Workflow Lengkap

    ### 1. Setup GitHub (sekali je)
    Pergi **⚙️ GitHub Settings** → ikut langkah setup.

    ### 2. Tambah Template Baru
    - Buat HTML template dengan placeholders format `{{GROOM_NAME}}` dll
    - Atau gunakan **🔧 Template Converter** kalau template masih hardcoded
    - Upload ke folder `templates/` dalam repo Streamlit
    - Daftar dalam `TEMPLATES` dict dalam `app.py`

    ### 3. Terima Order
    Customer order via WhatsApp dengan maklumat: nama, tarikh, venue, lagu, gambar.

    ### 4. Jana Kad
    - Pergi **🆕 Jana Kad Baru**
    - Isi semua maklumat
    - Klik **Jana + Deploy ke GitHub Pages**
    - Copy link → hantar ke customer

    ---

    ## 📋 Senarai Placeholder `{{CURLY}}` yang Disokong
    """)
    for ph, val in PLACEHOLDER_OPTIONS.items():
        if val:
            st.markdown(f"- `{val}` — {ph.split(' — ')[1] if ' — ' in ph else ''}")

# ─────────────────────────────────────────
#  PAGE: TEMPLATE INFO
# ─────────────────────────────────────────
elif "🗂️ Template Info" in page:
    st.markdown("# 🗂️ Senarai Template")
    st.markdown("---")
    for category, templates in TEMPLATES.items():
        emoji = '⭐' if category=='Essential' else '📸' if category=='Portrait' else '🎬' if category=='Cinematic' else '💎'
        st.markdown(f"## {emoji} {category}")
        for key, info in templates.items():
            file_exists = (BASE_DIR / "templates" / info['file']).exists()
            status = "✅ Fail ada" if file_exists else "❌ Fail tidak jumpa"
            st.markdown(f"""
            <div class='template-card'>
                <span class='category-badge'>{category}</span>
                <b style='color:#f0e8d8;font-size:1.05rem'>{info['preview_emoji']} {info['name']}</b><br>
                <small style='color:#888'>{info['desc']}</small><br><br>
                <small>📁 <code>{info['file']}</code> — {status}<br>
                {'📸 Perlu gambar' if info.get('has_photo') else '🎨 Tanpa gambar'}
                {'· 🎬 Ada video' if info.get('has_video') else ''}
                {'· 🖼️ Ada gallery' if info.get('has_gallery') else ''}</small>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("")
    st.markdown("---")
    st.markdown("""
    ### ➕ Cara Tambah Template Baru
    ```python
    "NamaCategory": {
        "template_key": {
            "name": "Nama Template",
            "file": "nama_fail.html",
            "has_photo": False,
            "preview_emoji": "✨",
            "desc": "Penerangan ringkas",
        },
    },
    ```
    """)
