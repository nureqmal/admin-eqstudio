import streamlit as st
import base64
import re
import requests
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).parent

st.set_page_config(
    page_title="EQStudio Admin — Kad Kahwin Digital",
    page_icon="💍",
    layout="wide",
    initial_sidebar_state="expanded",
)

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
    .ph-tag {
        display: inline-block; background: #1a2e1a; border: 1px solid #2d5a2d;
        border-radius: 4px; padding: 1px 6px; font-family: monospace;
        font-size: 0.78rem; color: #4ade80; margin: 1px;
    }
    .ph-tag-sq {
        display: inline-block; background: #1a1a2e; border: 1px solid #2d2d5a;
        border-radius: 4px; padding: 1px 6px; font-family: monospace;
        font-size: 0.78rem; color: #7ab3ff; margin: 1px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  TEMPLATE REGISTRY
# ─────────────────────────────────────────
# ─────────────────────────────────────────
#  REGISTRY — load dari GitHub JSON
#  File: templates/registry.json dalam repo kau
#
#  Fallback kepada TEMPLATES_DEFAULT kalau
#  GitHub belum setup atau JSON belum ada.
# ─────────────────────────────────────────
TEMPLATES_DEFAULT = {
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
}

REGISTRY_PATH = "templates/registry.json"  # path dalam GitHub repo kau

@st.cache_data(ttl=60)  # cache 60 saat — refresh bila ada template baru
def load_registry(token, repo):
    """Load registry.json dari GitHub. Return TEMPLATES_DEFAULT kalau gagal."""
    if not token or not repo:
        return TEMPLATES_DEFAULT
    try:
        url = f"https://api.github.com/repos/{repo}/contents/{REGISTRY_PATH}"
        r = requests.get(url,
            headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"},
            timeout=8)
        if r.status_code == 200:
            import json, base64 as b64
            content = b64.b64decode(r.json()["content"]).decode("utf-8")
            return json.loads(content)
        # 404 = registry belum wujud, guna default
        return TEMPLATES_DEFAULT
    except Exception:
        return TEMPLATES_DEFAULT

def save_registry(token, repo, registry):
    """Simpan registry.json ke GitHub. Return True kalau berjaya."""
    import json
    content = json.dumps(registry, indent=2, ensure_ascii=False)
    result = github_upload_file(token, repo, REGISTRY_PATH, content,
        "Update template registry")
    return result["success"]

# ─────────────────────────────────────────
#  PLACEHOLDER MASTER MAP
#
#  Setiap entry:  "nama_field" : {
#      "curly": "{{TOKEN}}",          ← format dalam templates lama (v2_celestial dll)
#      "square": "[Square Bracket]",  ← format dalam templates baru
#      "label": "Nama mesra untuk UI",
#  }
#
#  apply_replacements() akan detect format mana yang ada dalam HTML
#  dan guna yang betul secara automatik.
# ─────────────────────────────────────────
PLACEHOLDER_MAP = {
    "groom_name":    {"curly": "{{GROOM_NAME}}",        "square": "[Nama Pengantin Lelaki]",         "label": "Nama Pengantin Lelaki"},
    "bride_name":    {"curly": "{{BRIDE_NAME}}",         "square": "[Nama Pengantin Perempuan]",      "label": "Nama Pengantin Perempuan"},
    "father_name":   {"curly": "{{FATHER_NAME}}",        "square": "[Nama Tuan Rumah]",               "label": "Nama Bapa / Tuan Rumah"},
    "mother_name":   {"curly": "{{MOTHER_NAME}}",        "square": None,                              "label": "Nama Ibu / Tuan Rumah"},
    "groom_father":  {"curly": None,                     "square": "[Nama Bapa Pengantin Lelaki]",    "label": "Nama Bapa Pengantin Lelaki"},
    "groom_mother":  {"curly": None,                     "square": "[Nama Ibu Pengantin Lelaki]",     "label": "Nama Ibu Pengantin Lelaki"},
    "bride_father":  {"curly": None,                     "square": "[Nama Bapa Pengantin Perempuan]", "label": "Nama Bapa Pengantin Perempuan"},
    "bride_mother":  {"curly": None,                     "square": "[Nama Ibu Pengantin Perempuan]",  "label": "Nama Ibu Pengantin Perempuan"},
    "date_display":  {"curly": "{{DATE_DISPLAY}}",       "square": "[Tarikh Majlis]",                 "label": "Tarikh papar (eg: 10 Ogos 2026)"},
    "date_day":      {"curly": "{{DATE_DAY}}",           "square": "[Hari]",                          "label": "Hari majlis (eg: Isnin)"},
    "date_hijri":    {"curly": "{{DATE_HIJRI}}",         "square": "[Tarikh Hijri]",                  "label": "Tarikh Hijri"},
    "date_iso":      {"curly": "{{DATE_ISO}}",           "square": "[YYYY-MM-DD]T11:00:00",           "label": "Tarikh ISO (countdown)"},
    "date_dd":       {"curly": "{{DATE_DD}}",            "square": "[DD]",                            "label": "Nombor hari (DD)"},
    "date_mm":       {"curly": "{{DATE_MM}}",            "square": "[MM]",                            "label": "Nombor bulan (MM)"},
    "date_yyyy":     {"curly": "{{DATE_YYYY}}",          "square": "[YYYY]",                          "label": "Tahun (YYYY)"},
    "time_display":  {"curly": "{{TIME_DISPLAY}}",       "square": "[Masa Mula — Tamat]",             "label": "Masa majlis"},
    "venue_name":    {"curly": "{{VENUE_NAME}}",         "square": "[Nama Venue]",                    "label": "Nama dewan / tempat"},
    "venue_address": {"curly": "{{VENUE_ADDRESS}}",      "square": "[Alamat penuh venue majlis]",     "label": "Alamat penuh venue"},
    "venue_city":    {"curly": "{{VENUE_CITY}}",         "square": "[Bandar / Negeri]",               "label": "Bandar / Negeri"},
    "venue_locasi":  {"curly": None,                     "square": "[Lokasi]",                        "label": "Lokasi ringkas"},
    "waze_link":     {"curly": "{{WAZE_LINK}}",          "square": "https://waze.com/ul?q=[Alamat+Venue]", "label": "Link Waze"},
    "gmap_link":     {"curly": "{{GMAP_LINK}}",          "square": "https://maps.google.com/?q=[Alamat+Venue]", "label": "Link Google Maps"},
    "contact_phone": {"curly": "{{CONTACT_PHONE}}",      "square": "+601X-XXXXXXX",                  "label": "No telefon display"},
    "contact_wa":    {"curly": "{{CONTACT_PHONE_WA}}",   "square": "https://wa.me/601XXXXXXXXX",      "label": "No WhatsApp / WA link"},
    "music_url":     {"curly": "{{MUSIC_URL}}",          "square": "PLACEHOLDER_AUDIO_URL",           "label": "Link MP3 lagu"},
    "music_label":   {"curly": "{{MUSIC_LABEL}}",        "square": None,                              "label": "Nama lagu"},
    "hero_url":      {"curly": "{{HERO_PHOTO_URL}}",     "square": "[HERO_PHOTO_URL]",                "label": "Gambar hero"},
    "photo1_url":    {"curly": "{{PHOTO1_URL}}",         "square": "[PHOTO1_URL]",                    "label": "Gallery gambar 1"},
    "photo2_url":    {"curly": "{{PHOTO2_URL}}",         "square": "[PHOTO2_URL]",                    "label": "Gallery gambar 2"},
    "photo3_url":    {"curly": "{{PHOTO3_URL}}",         "square": "[PHOTO3_URL]",                    "label": "Gallery gambar 3"},
    "opening_url":   {"curly": "{{OPENING_PHOTO_URL}}",  "square": "[OPENING_PHOTO_URL]",             "label": "Gambar opening"},
    "video_url":     {"curly": "{{VIDEO_URL}}",          "square": "[VIDEO_URL]",                     "label": "Link video"},
    "gallery1_url":  {"curly": "{{GALLERY1_URL}}",       "square": "[GALLERY1_URL]",                  "label": "Gallery 1"},
    "gallery2_url":  {"curly": "{{GALLERY2_URL}}",       "square": "[GALLERY2_URL]",                  "label": "Gallery 2"},
    "gallery3_url":  {"curly": "{{GALLERY3_URL}}",       "square": "[GALLERY3_URL]",                  "label": "Gallery 3"},
    "gallery4_url":  {"curly": "{{GALLERY4_URL}}",       "square": "[GALLERY4_URL]",                  "label": "Gallery 4"},
    "gallery5_url":  {"curly": "{{GALLERY5_URL}}",       "square": "[GALLERY5_URL]",                  "label": "Gallery 5"},
}

# ─────────────────────────────────────────
#  DETECT FORMAT & BUILD REPLACEMENTS
# ─────────────────────────────────────────
def detect_format(html):
    """Detect sama ada template guna {{CURLY}} atau [Square Bracket]."""
    curly_count  = len(re.findall(r'\{\{[A-Z_]+\}\}', html))
    square_count = len(re.findall(r'\[[A-Za-z][^\]]{2,50}\]', html))
    if curly_count >= square_count:
        return "curly"
    return "square"

def build_replacements(fmt, data):
    """
    Bina dict {placeholder: nilai} ikut format template.
    fmt = "curly" atau "square"
    data = dict {field_key: nilai}  (sama keys macam PLACEHOLDER_MAP)
    """
    result = {}
    key = "curly" if fmt == "curly" else "square"

    # Sort panjang DESC supaya replace yang spesifik dulu
    for field, ph_info in PLACEHOLDER_MAP.items():
        ph = ph_info.get(key)
        if ph and field in data and data[field]:
            result[ph] = str(data[field])

    # Square bracket format perlukan extra replacements untuk composite patterns
    if fmt == "square":
        # [Hari], [Tarikh Majlis] — composite
        if data.get("date_day") and data.get("date_display"):
            result[f"[Hari], [Tarikh Majlis]"] = f"{data['date_day']}, {data['date_display']}"
        # [HH:MM] — [HH:MM] — masa range dalam clock widget
        if data.get("time_display"):
            result["[HH:MM] — [HH:MM]"] = data["time_display"]
        # [DD.MM.YYYY]
        if data.get("date_dd") and data.get("date_mm") and data.get("date_yyyy"):
            result["[DD.MM.YYYY]"] = f"{data['date_dd']}.{data['date_mm']}.{data['date_yyyy']}"
        # [Tarikh Majlis] · [Nama Venue] — footer
        if data.get("date_display") and data.get("venue_name"):
            result[f"[Tarikh Majlis] · [Nama Venue]"] = f"{data['date_display']} · {data['venue_name']}"
        # Countdown JS date
        if data.get("date_iso"):
            result["'[YYYY-MM-DD]T11:00:00'"] = f"'{data['date_iso']}'"
        # Alamat+Venue dalam Waze/Maps URL
        if data.get("venue_name"):
            venue_url = data["venue_name"].replace(' ', '+')
            result["[Alamat+Venue]"] = venue_url
            result["[Nama+Pengantin]"] = f"{data.get('groom_name','')}&{data.get('bride_name','')}".replace(' ','+')\
                if data.get('groom_name') else ""

    return result

def apply_replacements(html, replacements):
    """Replace semua placeholder, string panjang dulu."""
    for key, val in sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True):
        if val:
            html = html.replace(key, val)
    return html

# ─────────────────────────────────────────
#  HELPER FUNCTIONS
# ─────────────────────────────────────────
def load_template(filename, token="", repo=""):
    """
    Cuba fetch template dari GitHub dulu.
    Fallback ke local disk kalau takde GitHub.
    """
    if token and repo:
        try:
            url = f"https://api.github.com/repos/{repo}/contents/templates/{filename}"
            r = requests.get(url,
                headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"},
                timeout=10)
            if r.status_code == 200:
                import base64 as b64
                return b64.b64decode(r.json()["content"]).decode("utf-8")
        except Exception:
            pass
    # Fallback: local disk
    path = BASE_DIR / "templates" / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None

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
        user, repo_name = parts[0], parts[1]
        file_path = "/".join(parts[3:])
        return {"success": True, "pages_url": f"https://{user}.github.io/{repo_name}/{file_path}", "raw_url": raw_url}
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
        return True, "ok" if r.json().get("has_pages") else "no_pages"
    elif r.status_code == 401:
        return False, "Token tidak valid atau expired."
    elif r.status_code == 404:
        return False, f"Repo `{repo}` tidak jumpa atau token tiada access."
    else:
        return False, f"Error {r.status_code}"

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
    st.markdown("<div style='font-size:0.75rem;color:#666'><b style='color:#C9A96E'>EQStudio</b><br>Admin Dashboard v3.0<br>Kad Kahwin Digital</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  PAGE: GITHUB SETTINGS
# ─────────────────────────────────────────
if "⚙️ GitHub Settings" in page:
    st.markdown("# ⚙️ GitHub Settings")
    st.markdown("Setup sekali, guna selama-lamanya.")
    st.markdown("---")
    with st.expander("📋 Langkah setup", expanded=True):
        st.markdown("""
        **1.** Buat repo Public di [github.com/new](https://github.com/new) — tick "Add a README"

        **2.** Aktifkan GitHub Pages → Settings → Pages → Branch: main → Save

        **3.** Jana token di [github.com/settings/tokens/new](https://github.com/settings/tokens/new) → scope: `repo`
        """)
    col1, col2 = st.columns(2)
    with col1:
        input_token = st.text_input("GitHub Token", type="password",
            value=st.session_state.get("gh_token", ""), placeholder="ghp_xxxxxxxxxxxx")
    with col2:
        input_repo = st.text_input("Repo (username/repo)",
            value=st.session_state.get("gh_repo", ""), placeholder="nureqmal/eqstudio-cards")
    c1, c2 = st.columns([1, 3])
    with c1:
        if st.button("🔍 Test"):
            if input_token and input_repo:
                with st.spinner("Checking..."):
                    valid, msg = validate_github_token(input_token, input_repo)
                if valid:
                    st.session_state["gh_token"] = input_token
                    st.session_state["gh_repo"] = input_repo
                    st.success("✅ Connected!" if msg == "ok" else "✅ Token OK — aktifkan Pages dulu")
                else:
                    st.error(f"❌ {msg}")
    with c2:
        if st.button("💾 Simpan"):
            if input_token and input_repo:
                st.session_state["gh_token"] = input_token
                st.session_state["gh_repo"] = input_repo
                st.success("✅ Disimpan.")

# ─────────────────────────────────────────
#  PAGE: JANA KAD BARU
# ─────────────────────────────────────────
elif "🆕 Jana Kad Baru" in page:
    st.markdown("# 🆕 Jana Kad Kahwin Digital")

    gh_token = st.session_state.get("gh_token", "") or st.secrets.get("GH_TOKEN", "")
    gh_repo  = st.session_state.get("gh_repo",  "") or st.secrets.get("GH_REPO",  "")
    github_ready = bool(gh_token and gh_repo)

    if not github_ready:
        st.markdown("<div class='warning-box'>⚠️ GitHub belum setup — pergi ⚙️ GitHub Settings</div>", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 1️⃣ Pilih Template")

    TEMPLATES = load_registry(gh_token, gh_repo)

    if st.button("🔄 Refresh senarai template"):
        st.cache_data.clear()
        st.rerun()

    cat_sel = st.selectbox("Category", list(TEMPLATES.keys()),
        format_func=lambda x: f"{'⭐' if x=='Essential' else '📸' if x=='Portrait' else '🎬' if x=='Cinematic' else '💎'} {x}")
    tmpl_opts = TEMPLATES[cat_sel]
    tmpl_key = st.selectbox("Template", list(tmpl_opts.keys()),
        format_func=lambda k: f"{tmpl_opts[k]['preview_emoji']}  {tmpl_opts[k]['name']}")
    sel = tmpl_opts[tmpl_key]

    # Detect format template
    tmpl_html_check = load_template(sel["file"], gh_token, gh_repo)
    tmpl_fmt = detect_format(tmpl_html_check) if tmpl_html_check else "curly"
    fmt_badge = "🟢 `{{CURLY}}`" if tmpl_fmt == "curly" else "🔵 `[Square Bracket]`"
    st.markdown(f"<div class='info-box'>{sel['preview_emoji']} <b>{sel['name']}</b> — {sel['desc']}<br>Format: {fmt_badge}</div>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("## 2️⃣ Maklumat Pengantin")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**🤵 Pengantin Lelaki**")
        groom_name  = st.text_input("Nama Panggilan", placeholder="Ahmad", key="groom")
        groom_full  = st.text_input("Nama Penuh", placeholder="Ahmad bin Abdullah", key="groom_full")
        groom_father = st.text_input("Nama Bapa", placeholder="Abdullah bin Salleh", key="gf")
        groom_mother = st.text_input("Nama Ibu", placeholder="Siti binti Ahmad", key="gm")
    with c2:
        st.markdown("**👰 Pengantin Perempuan**")
        bride_name  = st.text_input("Nama Panggilan", placeholder="Sarah", key="bride")
        bride_full  = st.text_input("Nama Penuh", placeholder="Sarah binti Ibrahim", key="bride_full")
        bride_father = st.text_input("Nama Bapa", placeholder="Ibrahim bin Hassan", key="bf")
        bride_mother = st.text_input("Nama Ibu", placeholder="Aminah binti Yusof", key="bm")

    st.markdown("---")
    st.markdown("## 3️⃣ Tuan Rumah")
    parent_side = st.selectbox("Pihak Tuan Rumah", ["Perempuan", "Lelaki", "Perempuan & Lelaki"])
    if parent_side == "Lelaki":
        host_father = groom_father
        host_mother = groom_mother
    elif parent_side == "Perempuan":
        host_father = bride_father or groom_father
        host_mother = bride_mother or groom_mother
    else:
        host_father = f"{groom_father} & {bride_father}" if bride_father else groom_father
        host_mother = f"{groom_mother} & {bride_mother}" if bride_mother else groom_mother

    st.markdown("---")
    st.markdown("## 4️⃣ Tarikh & Masa")
    c1, c2 = st.columns(2)
    with c1:
        event_date = st.date_input("Tarikh Majlis")
        event_time = st.time_input("Masa Majlis")
        hijri_date = st.text_input("Tarikh Hijri", placeholder="15 Safar 1448H")
    with c2:
        days_ms   = ["Isnin","Selasa","Rabu","Khamis","Jumaat","Sabtu","Ahad"]
        months_ms = ["","Januari","Februari","Mac","April","Mei","Jun","Julai","Ogos","September","Oktober","November","Disember"]
        day_name     = days_ms[event_date.weekday()]
        date_display = f"{event_date.day} {months_ms[event_date.month]} {event_date.year}"
        date_iso     = f"{event_date.isoformat()}T{event_time.strftime('%H:%M:%S')}+08:00"
        time_display = event_time.strftime('%H:%M')
        st.markdown(f"""
        <div class='info-box'>
            📅 {day_name}, {date_display}<br>
            🕐 {time_display} &nbsp;|&nbsp; 🗓️ {hijri_date or '—'}<br>
            <small style='opacity:0.5'>ISO: {date_iso}</small>
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 5️⃣ Lokasi")
    venue_name    = st.text_input("Nama Dewan / Tempat", placeholder="Dewan Seri Kenangan")
    venue_address = st.text_area("Alamat Penuh", placeholder="No 1, Jalan Bahagia, 43000 Kajang, Selangor", height=70)
    venue_city    = st.text_input("Bandar / Negeri (ringkas)", placeholder="Kajang, Selangor")
    c1, c2 = st.columns(2)
    with c1:
        waze_custom = st.text_input("Link Waze (kosong = auto)")
    with c2:
        gmap_custom = st.text_input("Link Google Maps (kosong = auto)")
    waze_link = waze_custom or (get_waze_link(venue_name, venue_address) if venue_name else "")
    gmap_link = gmap_custom or (get_gmap_link(venue_name, venue_address) if venue_name else "")

    st.markdown("---")
    st.markdown("## 6️⃣ Contact & Lagu")
    c1, c2 = st.columns(2)
    with c1:
        contact_name  = st.text_input("Nama Contact Person", placeholder="Abdullah bin Salleh")
        contact_phone = st.text_input("No Telefon", placeholder="011-12345678")
        wa_num = get_whatsapp_number(contact_phone) if contact_phone else ""
        if contact_phone:
            st.caption(f"📱 WhatsApp: {wa_num}")
    with c2:
        music_url   = st.text_input("Link MP3", placeholder="https://cdn.jsdelivr.net/gh/...")
        music_label = st.text_input("Nama Lagu", placeholder="Beautiful In White")

    st.markdown("---")
    hero_url = photo1_url = photo2_url = photo3_url = opening_url = ""
    if sel.get("has_photo"):
        st.markdown("## 7️⃣ Gambar")
        pm = st.radio("Cara gambar", ["📎 Upload", "🔗 URL"], horizontal=True)
        if pm == "📎 Upload":
            c1, c2 = st.columns(2)
            with c1:
                hf = st.file_uploader("Hero", type=["jpg","jpeg","png","webp"], key="hero")
                p1 = st.file_uploader("Gallery 1", type=["jpg","jpeg","png","webp"], key="p1")
                op = st.file_uploader("Opening", type=["jpg","jpeg","png","webp"], key="op")
            with c2:
                p2 = st.file_uploader("Gallery 2", type=["jpg","jpeg","png","webp"], key="p2")
                p3 = st.file_uploader("Gallery 3", type=["jpg","jpeg","png","webp"], key="p3")
            if hf: hero_url    = file_to_data_url(hf)
            if p1: photo1_url  = file_to_data_url(p1)
            if p2: photo2_url  = file_to_data_url(p2)
            if p3: photo3_url  = file_to_data_url(p3)
            if op: opening_url = file_to_data_url(op)
        else:
            c1, c2 = st.columns(2)
            with c1:
                hero_url    = st.text_input("Hero URL")
                photo1_url  = st.text_input("Gallery 1 URL")
                opening_url = st.text_input("Opening URL")
            with c2:
                photo2_url = st.text_input("Gallery 2 URL")
                photo3_url = st.text_input("Gallery 3 URL")
        st.markdown("---")

    video_url = ""
    if sel.get("has_video"):
        st.markdown("## 🎬 Video")
        video_url = st.text_input("Link Google Drive Video")
        st.markdown("---")

    g1=g2=g3=g4=g5=""
    if sel.get("has_gallery"):
        st.markdown("## 🖼️ Gallery")
        c1, c2 = st.columns(2)
        with c1:
            g1 = st.text_input("Gallery 1"); g2 = st.text_input("Gallery 2"); g3 = st.text_input("Gallery 3")
        with c2:
            g4 = st.text_input("Gallery 4"); g5 = st.text_input("Gallery 5")
        st.markdown("---")

    st.markdown("## 8️⃣ Jana & Deploy")
    required = {
        "Nama pengantin lelaki": groom_name,
        "Nama pengantin perempuan": bride_name,
        "Nama bapa": groom_father,
        "Nama dewan": venue_name,
        "Alamat majlis": venue_address,
        "No telefon": contact_phone,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        st.warning(f"⚠️ Sila lengkapkan: **{', '.join(missing)}**")

    if github_ready:
        deploy_mode = st.radio("Mode", ["🚀 Deploy ke GitHub Pages", "⬇️ Download sahaja"], horizontal=True)
    else:
        deploy_mode = "⬇️ Download sahaja"
        st.info("Setup GitHub untuk auto-deploy.")

    if st.button("✨ Jana Kad Sekarang!", disabled=bool(missing)):
        template_html = load_template(sel["file"], gh_token, gh_repo)
        if template_html is None:
            st.error(f"❌ Template tidak jumpa: `templates/{sel['file']}`")
        else:
            fmt = detect_format(template_html)

            # Data dict — keys sama dengan PLACEHOLDER_MAP
            data = {
                "groom_name":    groom_name,
                "bride_name":    bride_name,
                "father_name":   host_father,
                "mother_name":   host_mother,
                "groom_father":  groom_father,
                "groom_mother":  groom_mother,
                "bride_father":  bride_father,
                "bride_mother":  bride_mother,
                "date_display":  date_display,
                "date_day":      day_name,
                "date_hijri":    hijri_date,
                "date_iso":      date_iso,
                "date_dd":       str(event_date.day).zfill(2),
                "date_mm":       str(event_date.month).zfill(2),
                "date_yyyy":     str(event_date.year),
                "time_display":  time_display,
                "venue_name":    venue_name,
                "venue_address": venue_address,
                "venue_city":    venue_city or venue_name,
                "venue_locasi":  venue_city or venue_name,
                "waze_link":     waze_link,
                "gmap_link":     gmap_link,
                "contact_phone": contact_phone,
                "contact_wa":    wa_num,
                "music_url":     music_url,
                "music_label":   music_label,
                "hero_url":      hero_url,
                "photo1_url":    photo1_url,
                "photo2_url":    photo2_url,
                "photo3_url":    photo3_url,
                "opening_url":   opening_url,
                "video_url":     video_url,
                "gallery1_url":  g1,
                "gallery2_url":  g2,
                "gallery3_url":  g3,
                "gallery4_url":  g4,
                "gallery5_url":  g5,
            }

            replacements = build_replacements(fmt, data)
            final_html   = apply_replacements(template_html, replacements)
            html_bytes   = final_html.encode("utf-8")
            order_id     = generate_order_id()
            filename     = f"kad-{sanitize_filename(groom_name)}-{sanitize_filename(bride_name)}-{order_id.lower()}.html"

            if "Deploy" in deploy_mode and github_ready:
                with st.spinner("🚀 Deploying..."):
                    result = github_upload_file(gh_token, gh_repo, f"cards/{filename}", final_html,
                        f"Add kad: {groom_name} & {bride_name} [{order_id}]")
                if result["success"]:
                    st.markdown(f"""
                    <div class='success-box'>
                        <h3 style='color:#4CAF50;margin:0 0 .5rem'>✅ Deployed!</h3>
                        <span class='order-id'>{order_id}</span><br><br>
                        <b>{groom_name} & {bride_name}</b> · {date_display}
                    </div>""", unsafe_allow_html=True)
                    st.markdown(f"<div class='link-box'><b style='color:#C9A96E'>🔗 Link Kad</b><br><a href='{result['pages_url']}' target='_blank' style='color:#4ade80;font-weight:600'>{result['pages_url']}</a><br><small style='color:#666'>⚠️ Ambik 1-2 minit pertama kali</small></div>", unsafe_allow_html=True)
                    st.code(result["pages_url"], language=None)
                else:
                    st.error(f"❌ {result['error']}")
            else:
                st.markdown(f"<div class='success-box'><h3 style='color:#4CAF50;margin:0 0 .5rem'>✅ Kad Siap!</h3><span class='order-id'>{order_id}</span><br><b>{groom_name} & {bride_name}</b> · {date_display}</div>", unsafe_allow_html=True)

            st.download_button("⬇️ Download HTML", data=html_bytes, file_name=filename, mime="text/html", use_container_width=True)

            with st.expander("👁️ Preview"):
                st.code(final_html[:3000] + "\n... [truncated]", language="html")

# ─────────────────────────────────────────
#  PAGE: TEMPLATE CONVERTER
# ─────────────────────────────────────────
elif "🔧 Template Converter" in page:
    st.markdown("# 🔧 Template Converter")
    st.markdown("Upload HTML template baru → map nilai hardcoded → convert jadi template dengan placeholders → upload ke GitHub.")
    st.markdown("---")

    st.markdown("## 1️⃣ Upload HTML Template")
    uploaded = st.file_uploader("Upload fail HTML", type=["html","htm"])

    if uploaded:
        raw_html = uploaded.read().decode("utf-8")
        fmt = detect_format(raw_html)
        fmt_label = "**`{{CURLY}}`** (template lama)" if fmt == "curly" else "**`[Square Bracket]`** (template baru)"
        st.success(f"✅ Fail dibaca — {len(raw_html):,} chars")
        st.markdown(f"<div class='info-box'>🔍 Format dikesan: {fmt_label}</div>", unsafe_allow_html=True)

        # Auto-detect placeholders dalam HTML
        if fmt == "square":
            found_phs = sorted(set(re.findall(r'\[[A-Za-z][^\]]{2,60}\]', raw_html)))
            # Tapis keluar yang bukan placeholder (JS array, CSS selectors dll)
            found_phs = [p for p in found_phs if not any(c in p for c in ['(', ')', '{', '}', '.', '=', '0','1','2','3','4','5','6','7','8','9'])]
        else:
            found_phs = sorted(set(re.findall(r'\{\{[A-Z_]+\}\}', raw_html)))

        if found_phs:
            st.markdown("---")
            st.markdown("## 📋 Placeholders yang Dikesan dalam Template")
            st.markdown("<div class='info-box'>Ini semua placeholder yang dijumpai dalam HTML kau:</div>", unsafe_allow_html=True)
            tag_class = "ph-tag-sq" if fmt == "square" else "ph-tag"
            tags_html = " ".join(f"<span class='{tag_class}'>{p}</span>" for p in found_phs)
            st.markdown(tags_html, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("## 2️⃣ Map Nilai Hardcoded → Placeholder")
        st.markdown(
            "<div class='info-box'>"
            "Taip nilai yang <b>ada dalam HTML</b> (eg: nama pengantin sebenar), "
            "pastu pilih placeholder yang nak digantikan."
            "<br>Kolum <b>Jumpa?</b> akan tunjuk berapa kali nilai tu ada dalam HTML."
            "</div>",
            unsafe_allow_html=True
        )

        # Build dropdown options dari PLACEHOLDER_MAP ikut format
        ph_key = "square" if fmt == "square" else "curly"
        ph_options = {"-- Pilih --": ""}
        for field, info in PLACEHOLDER_MAP.items():
            ph = info.get(ph_key)
            if ph:
                ph_options[f"{ph}  —  {info['label']}"] = ph

        if "converter_rows" not in st.session_state:
            st.session_state.converter_rows = [{"value": "", "placeholder": ""}]

        c1, c2, _ = st.columns([1, 1, 4])
        with c1:
            if st.button("➕ Tambah"):
                st.session_state.converter_rows.append({"value": "", "placeholder": ""})
                st.rerun()
        with c2:
            if st.button("➖ Buang") and len(st.session_state.converter_rows) > 1:
                st.session_state.converter_rows.pop()
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        ch1, ch2, ch3 = st.columns([2, 3, 1])
        with ch1: st.markdown("**Nilai dalam HTML**")
        with ch2: st.markdown("**Ganti dengan Placeholder**")
        with ch3: st.markdown("**Jumpa?**")

        for i, row in enumerate(st.session_state.converter_rows):
            c1, c2, c3 = st.columns([2, 3, 1])
            with c1:
                val = st.text_input(f"val{i}", value=row["value"],
                    placeholder="eg: Ahmad Nazmi", key=f"cv_{i}", label_visibility="collapsed")
                st.session_state.converter_rows[i]["value"] = val
            with c2:
                sel_ph = st.selectbox(f"ph{i}", list(ph_options.keys()),
                    key=f"cp_{i}", label_visibility="collapsed")
                st.session_state.converter_rows[i]["placeholder"] = ph_options[sel_ph]
            with c3:
                if val:
                    n = raw_html.count(val)
                    if n > 0:
                        st.markdown(f"<div style='color:#4CAF50;padding-top:8px'>✅ {n}x</div>", unsafe_allow_html=True)
                    else:
                        st.markdown("<div style='color:#ff6b6b;padding-top:8px'>❌</div>", unsafe_allow_html=True)
                else:
                    st.markdown("<div style='color:#666;padding-top:8px'>—</div>", unsafe_allow_html=True)

        valid = [r for r in st.session_state.converter_rows if r["value"] and r["placeholder"] and r["value"] in raw_html]
        not_found = [r for r in st.session_state.converter_rows if r["value"] and r["placeholder"] and r["value"] not in raw_html]

        st.markdown("---")
        st.markdown("## 3️⃣ Preview & Convert")
        if valid:
            st.markdown(f"<div class='info-box'>✅ <b>{len(valid)} replacement</b> akan dibuat{'<br>⚠️ ' + str(len(not_found)) + ' nilai tidak jumpa' if not_found else ''}</div>", unsafe_allow_html=True)
            for m in valid:
                st.markdown(f"- `{m['value']}` → `{m['placeholder']}` ({raw_html.count(m['value'])}x)")
        else:
            st.warning("Belum ada mapping yang valid.")

        st.markdown("---")
        st.markdown("## 4️⃣ Info Template & Upload")
        c1, c2 = st.columns(2)
        with c1:
            t_cat  = st.selectbox("Category", ["Essential","Portrait","Cinematic","Prestige"])
            t_name = st.text_input("Nama Template", placeholder="Garden v2 — Hijau Sage")
            t_emoji = st.text_input("Emoji", placeholder="🌿", max_chars=2)
        with c2:
            t_desc = st.text_input("Penerangan", placeholder="Tema hijau sage & dusty rose")
            t_file = st.text_input("Nama Fail (tanpa .html)", placeholder="v5_garden")
            if t_file:
                safe = re.sub(r'[^a-z0-9_]', '_', t_file.lower().strip())
                if safe != t_file:
                    st.caption(f"→ `{safe}.html`")
                    t_file = safe

        gh_token = st.session_state.get("gh_token","") or st.secrets.get("GH_TOKEN","")
        gh_repo  = st.session_state.get("gh_repo", "") or st.secrets.get("GH_REPO", "")
        can = bool(valid and t_name and t_file and gh_token and gh_repo)
        if not can:
            miss = []
            if not valid: miss.append("mapping values")
            if not t_name: miss.append("nama template")
            if not t_file: miss.append("nama fail")
            if not gh_token or not gh_repo: miss.append("GitHub settings")
            if miss: st.warning(f"⚠️ Lengkapkan: {', '.join(miss)}")

        if st.button("🚀 Convert & Upload!", disabled=not can):
            converted = raw_html
            for m in sorted(valid, key=lambda x: len(x["value"]), reverse=True):
                converted = converted.replace(m["value"], m["placeholder"])
            final_fn = f"{t_file}.html"

            # Step 1: Upload HTML template ke GitHub
            with st.spinner("📤 Upload template..."):
                res = github_upload_file(gh_token, gh_repo,
                    f"templates/{final_fn}",
                    converted, f"Add template: {t_name}")

            if res["success"]:
                # Step 2: Update registry.json
                new_entry = {
                    "name": t_name,
                    "file": final_fn,
                    "has_photo": t_cat in ["Portrait", "Cinematic", "Prestige"],
                    "has_video": t_cat in ["Cinematic", "Prestige"],
                    "has_gallery": t_cat == "Prestige",
                    "preview_emoji": t_emoji or "✨",
                    "desc": t_desc,
                }
                with st.spinner("📋 Update registry..."):
                    registry = load_registry(gh_token, gh_repo)
                    if t_cat not in registry:
                        registry[t_cat] = {}
                    registry[t_cat][t_file] = new_entry
                    reg_ok = save_registry(gh_token, gh_repo, registry)

                st.cache_data.clear()  # force refresh supaya template baru muncul

                st.markdown(f"""
                <div class='success-box'>
                    <h3 style='color:#4CAF50;margin:0 0 .5rem'>✅ Template berjaya ditambah!</h3>
                    <b>Nama:</b> {t_name}<br>
                    <b>Fail:</b> {final_fn}<br>
                    <b>Registry:</b> {"✅ Updated" if reg_ok else "⚠️ Gagal update — cuba refresh manual"}<br><br>
                    Pergi <b>🆕 Jana Kad Baru</b> → template kau dah ada dalam senarai!
                </div>""", unsafe_allow_html=True)
                st.session_state.converter_rows = [{"value":"","placeholder":""}]
            else:
                st.error(f"❌ {res['error']}")

        if valid:
            with st.expander("👁️ Preview selepas convert"):
                prev = raw_html
                for m in sorted(valid, key=lambda x: len(x["value"]), reverse=True):
                    prev = prev.replace(m["value"], m["placeholder"])
                st.code(prev[:3000] + "\n... [truncated]", language="html")

# ─────────────────────────────────────────
#  PAGE: CARA GUNA
# ─────────────────────────────────────────
elif "📋 Cara Guna" in page:
    st.markdown("# 📋 Cara Guna")
    st.markdown("---")
    st.markdown("""
    ## Dua jenis template yang disokong

    | Format | Contoh | Keterangan |
    |--------|--------|------------|
    | `{{CURLY}}` | `{{GROOM_NAME}}` | Templates lama (v2_celestial, v3_garden, dll) |
    | `[Square]` | `[Nama Pengantin Lelaki]` | Templates baru yang kau design sendiri |

    App akan **auto-detect** format mana digunakan — kau tak perlu buat apa-apa.

    ## Workflow

    **Jana Kad Baru** — untuk template yang dah ada dalam folder `templates/`.
    Isi borang → klik Jana → download atau deploy ke GitHub Pages.

    **Template Converter** — untuk HTML baru yang masih ada nama hardcoded.
    Upload HTML → taip nilai lama → pilih placeholder → upload ke GitHub.

    ## Placeholders [Square Bracket] yang disokong
    """)
    sq_phs = [(info["square"], info["label"]) for info in PLACEHOLDER_MAP.values() if info.get("square")]
    for ph, label in sq_phs:
        st.markdown(f"- `{ph}` — {label}")

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
            path = BASE_DIR / "templates" / info['file']
            exists = path.exists()
            if exists:
                html = path.read_text(encoding="utf-8")
                fmt = detect_format(html)
                fmt_badge = "🟢 `{{CURLY}}`" if fmt == "curly" else "🔵 `[Square]`"
                status = f"✅ Ada · {fmt_badge}"
            else:
                status = "❌ Fail tidak jumpa"
            st.markdown(f"""
            <div class='template-card'>
                <span class='category-badge'>{category}</span>
                <b style='color:#f0e8d8'>{info['preview_emoji']} {info['name']}</b><br>
                <small style='color:#888'>{info['desc']}</small><br>
                <small>📁 <code>{info['file']}</code> — {status}</small>
            </div>""", unsafe_allow_html=True)
        st.markdown("")
