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
#  APPLY REPLACEMENTS — direct {{CURLY}} dict
# ─────────────────────────────────────────
def detect_format(html):
    """Detect sama ada template guna {{CURLY}} atau [Square Bracket]."""
    curly  = len(re.findall(r'\{\{[A-Z_]+\}\}', html))
    square = len(re.findall(r'\[[A-Za-z][^\]]{2,50}\]', html))
    return "curly" if curly >= square else "square"

def build_replacements(data):
    """
    Bina dict {{{placeholder}}}: nilai} terus dari data dict.
    Semua placeholder guna format {{CURLY}}.
    """
    d = data
    r = {}

    def s(key): return str(d.get(key) or "")

    # ── Pengantin ────────────────────────────────────────
    r["{{GROOM_NAME}}"]             = s("groom_name")
    r["{{BRIDE_NAME}}"]             = s("bride_name")
    r["{{GROOM_FULL_NAME}}"]        = s("groom_full") or s("groom_name")
    r["{{BRIDE_FULL_NAME}}"]        = s("bride_full") or s("bride_name")
    r["{{GROOM_FATHER}}"]           = s("groom_father")
    r["{{GROOM_MOTHER}}"]           = s("groom_mother")
    r["{{BRIDE_FATHER}}"]           = s("bride_father")
    r["{{BRIDE_MOTHER}}"]           = s("bride_mother")

    # ── Tuan Rumah ───────────────────────────────────────
    r["{{HOST_FAMILY}}"]            = s("host_family")
    r["{{HOST_FAMILY_FULL}}"]       = s("host_family_full") or s("host_family")
    r["{{HOST_MESSAGE_BM}}"]        = s("host_message_bm")
    r["{{HOST_MESSAGE_EN}}"]        = s("host_message_en")

    # ── Tarikh ───────────────────────────────────────────
    r["{{DATE_DISPLAY}}"]           = s("date_display")
    r["{{DATE_DAY}}"]               = s("date_day")
    r["{{DATE_HIJRI}}"]             = s("date_hijri")
    r["{{DATE_ISO}}"]               = s("date_iso")
    r["{{DATE_DD}}"]                = s("date_dd")
    r["{{DATE_MM}}"]                = s("date_mm")
    r["{{DATE_YYYY}}"]              = s("date_yyyy")
    r["{{DATE_YYYYMMDD}}"]          = s("date_yyyymmdd")

    # ── Masa ─────────────────────────────────────────────
    r["{{TIME_START}}"]             = s("time_start")
    r["{{TIME_END}}"]               = s("time_end")
    r["{{TIME_START_SHORT}}"]       = s("time_start")        # sama
    r["{{TIME_END_SHORT}}"]         = s("time_end")          # sama
    r["{{TIME_START_HHMM}}"]        = s("time_start_hhmm")
    r["{{TIME_END_HHMM}}"]          = s("time_end_hhmm")

    # ── Aturcara ─────────────────────────────────────────
    r["{{TIME_ARRIVAL}}"]           = s("time_arrival")
    r["{{TIME_AKAD}}"]              = s("time_akad")
    r["{{TIME_BERSANDING}}"]        = s("time_bersanding")
    r["{{TIME_MAKAN}}"]             = s("time_makan")
    r["{{TIME_BERSURAI}}"]          = s("time_bersurai")

    # ── Venue ────────────────────────────────────────────
    r["{{VENUE_NAME}}"]             = s("venue_name")
    r["{{VENUE_FULLNAME}}"]         = s("venue_fullname") or s("venue_name")
    r["{{VENUE_ADDRESS}}"]          = s("venue_address")
    r["{{VENUE_CITY}}"]             = s("venue_city")
    r["{{VENUE_WAZE_QUERY}}"]       = s("venue_waze_query")
    r["{{VENUE_GMAPS_QUERY}}"]      = s("venue_gmaps_query")
    r["{{VENUE_NAME_URL}}"]         = s("venue_name").replace(" ", "+") if s("venue_name") else ""
    r["{{GROOM_NAME_URL}}"]         = s("groom_name").replace(" ", "+") if s("groom_name") else ""
    r["{{BRIDE_NAME_URL}}"]         = s("bride_name").replace(" ", "+") if s("bride_name") else ""

    # ── Waze & Maps full link ────────────────────────────
    r["{{WAZE_LINK}}"]              = s("waze_link")
    r["{{GMAP_LINK}}"]              = s("gmap_link")

    # ── Contact 1 ────────────────────────────────────────
    r["{{CONTACT1_NAME}}"]          = s("contact1_name")
    r["{{CONTACT1_PHONE_DISPLAY}}"] = s("contact1_phone_display")
    r["{{CONTACT1_PHONE_WA}}"]      = s("contact1_phone_wa")

    # ── Contact 2 ────────────────────────────────────────
    r["{{CONTACT2_NAME}}"]          = s("contact2_name")
    r["{{CONTACT2_PHONE_DISPLAY}}"] = s("contact2_phone_display")
    r["{{CONTACT2_PHONE_WA}}"]      = s("contact2_phone_wa")

    # ── Lagu ─────────────────────────────────────────────
    r["{{MUSIC_URL}}"]              = s("music_url")
    r["{{MUSIC_LABEL}}"]            = s("music_label")

    # ── Kisah Cinta ──────────────────────────────────────
    r["{{LOVE_YEAR_1}}"]            = s("love_year_1")
    r["{{LOVE_STORY_1}}"]           = s("love_story_1")
    r["{{LOVE_YEAR_2}}"]            = s("love_year_2")
    r["{{LOVE_STORY_2}}"]           = s("love_story_2")
    r["{{LOVE_YEAR_3}}"]            = s("love_year_3")
    r["{{LOVE_STORY_3}}"]           = s("love_story_3")

    # ── Dress Code ───────────────────────────────────────
    r["{{DRESSCODE_THEME}}"]        = s("dresscode_theme")
    r["{{DRESSCODE_THEME_EN}}"]     = s("dresscode_theme_en")

    # ── Doa sample ───────────────────────────────────────
    r["{{DOA_SAMPLE1_NAME}}"]       = s("doa_sample1_name")
    r["{{DOA_SAMPLE1_MSG}}"]        = s("doa_sample1_msg")
    r["{{DOA_SAMPLE2_NAME}}"]       = s("doa_sample2_name")
    r["{{DOA_SAMPLE2_MSG}}"]        = s("doa_sample2_msg")

    # ── Countdown JS ─────────────────────────────────────
    # Template guna: new Date('{{DATE_YYYYMMDD}}T{{TIME_START_HHMM}}:00')
    # dah covered oleh replacements atas

    # ── Gambar & Video ───────────────────────────────────
    r["{{HERO_PHOTO_URL}}"]         = s("hero_url")
    r["{{PHOTO1_URL}}"]             = s("photo1_url")
    r["{{PHOTO2_URL}}"]             = s("photo2_url")
    r["{{PHOTO3_URL}}"]             = s("photo3_url")
    r["{{OPENING_PHOTO_URL}}"]      = s("opening_url")
    r["{{VIDEO_URL}}"]              = s("video_url")
    r["{{GALLERY1_URL}}"]           = s("gallery1_url")
    r["{{GALLERY2_URL}}"]           = s("gallery2_url")
    r["{{GALLERY3_URL}}"]           = s("gallery3_url")
    r["{{GALLERY4_URL}}"]           = s("gallery4_url")
    r["{{GALLERY5_URL}}"]           = s("gallery5_url")

    # Buang entries yang kosong
    return {k: v for k, v in r.items() if v}

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
        groom_name   = st.text_input("Nama Panggilan", placeholder="Ahmad", key="groom")
        groom_full   = st.text_input("Nama Penuh", placeholder="Ahmad bin Abdullah", key="groom_full")
        groom_father = st.text_input("Nama Bapa", placeholder="Abdullah bin Salleh", key="gf")
        groom_mother = st.text_input("Nama Ibu", placeholder="Siti binti Ahmad", key="gm")
    with c2:
        st.markdown("**👰 Pengantin Perempuan**")
        bride_name   = st.text_input("Nama Panggilan", placeholder="Sarah", key="bride")
        bride_full   = st.text_input("Nama Penuh", placeholder="Sarah binti Ibrahim", key="bride_full")
        bride_father = st.text_input("Nama Bapa", placeholder="Ibrahim bin Hassan", key="bf")
        bride_mother = st.text_input("Nama Ibu", placeholder="Aminah binti Yusof", key="bm")

    st.markdown("---")
    st.markdown("## 3️⃣ Tuan Rumah & Mesej")
    c1, c2 = st.columns(2)
    with c1:
        parent_side = st.selectbox("Pihak Tuan Rumah", ["Perempuan", "Lelaki", "Perempuan & Lelaki"])
        if parent_side == "Lelaki":
            host_family = f"Keluarga {groom_father}" if groom_father else ""
        elif parent_side == "Perempuan":
            host_family = f"Keluarga {bride_father}" if bride_father else ""
        else:
            gf = groom_father.split()[1] if groom_father and len(groom_father.split()) > 1 else groom_father
            bf = bride_father.split()[1] if bride_father and len(bride_father.split()) > 1 else bride_father
            host_family = f"Keluarga {gf} & Keluarga {bf}" if (gf and bf) else f"Keluarga {gf or bf}"
        host_family_custom = st.text_input("Nama Keluarga Tuan Rumah", value=host_family, placeholder="Keluarga Ahmad & Keluarga Ibrahim")
        host_family_full   = st.text_input("Nama Penuh (footer)", placeholder="Keluarga Haji Ahmad & Keluarga Haji Ibrahim")
    with c2:
        host_message_bm = st.text_area("Mesej Tuan Rumah (BM)", height=100,
            placeholder="Dengan penuh kerendahan hati dan rasa syukur ke hadrat Ilahi...")
        host_message_en = st.text_area("Mesej Tuan Rumah (EN)", height=100,
            placeholder="With heartfelt gratitude, we welcome you...")

    st.markdown("---")
    st.markdown("## 4️⃣ Tarikh & Masa")
    c1, c2 = st.columns(2)
    with c1:
        event_date = st.date_input("Tarikh Majlis")
        hijri_date = st.text_input("Tarikh Hijri", placeholder="15 Safar 1448H")
        time_start = st.text_input("Masa Mula", placeholder="11:00 PG", value="11:00 PG")
        time_end   = st.text_input("Masa Tamat", placeholder="4:00 PTG", value="4:00 PTG")
    with c2:
        days_ms   = ["Isnin","Selasa","Rabu","Khamis","Jumaat","Sabtu","Ahad"]
        months_ms = ["","Januari","Februari","Mac","April","Mei","Jun","Julai","Ogos","September","Oktober","November","Disember"]
        day_name     = days_ms[event_date.weekday()]
        date_display = f"{event_date.day} {months_ms[event_date.month]} {event_date.year}"
        date_yyyymmdd = event_date.strftime('%Y%m%d')
        # parse masa mula untuk countdown & calendar
        import re as _re
        _hm = _re.search(r'(\d{1,2}):(\d{2})', time_start)
        if _hm:
            _h, _m = int(_hm.group(1)), int(_hm.group(2))
            time_start_hhmm = f"{_h:02d}{_m:02d}"
        else:
            time_start_hhmm = "1100"
        _hm2 = _re.search(r'(\d{1,2}):(\d{2})', time_end)
        time_end_hhmm = f"{int(_hm2.group(1)):02d}{int(_hm2.group(2)):02d}" if _hm2 else "1600"
        date_iso = f"{event_date.isoformat()}T{time_start_hhmm[:2]}:{time_start_hhmm[2:]}:00"
        st.markdown(f"""
        <div class='info-box'>
            📅 {day_name}, {date_display}<br>
            🕐 {time_start} — {time_end}<br>
            🗓️ {hijri_date or '—'}
        </div>""", unsafe_allow_html=True)

    st.markdown("---")
    st.markdown("## 5️⃣ Aturcara Majlis")
    c1, c2 = st.columns(2)
    with c1:
        time_arrival   = st.text_input("🌅 Ketibaan Tetamu", value=time_start, placeholder="11:00 PG")
        time_akad      = st.text_input("🌸 Akad Nikah", placeholder="11:30 PG")
        time_bersanding = st.text_input("👑 Persandingan", placeholder="12:30 TG")
    with c2:
        time_makan     = st.text_input("🍽️ Jamuan Makan", placeholder="1:00 PTG")
        time_bersurai  = st.text_input("🌙 Majlis Bersurai", value=time_end, placeholder="4:00 PTG")

    st.markdown("---")
    st.markdown("## 6️⃣ Lokasi")
    venue_name    = st.text_input("Nama Dewan / Tempat", placeholder="Dewan Seri Kenangan")
    venue_fullname = st.text_input("Nama Penuh Venue (untuk footer/map)", placeholder="Dewan Seri Kenangan Kajang")
    venue_address = st.text_area("Alamat Penuh", placeholder="No 1, Jalan Bahagia, 43000 Kajang, Selangor", height=70)
    venue_city    = st.text_input("Bandar / Negeri (ringkas)", placeholder="Kajang, Selangor")
    c1, c2 = st.columns(2)
    with c1:
        waze_custom = st.text_input("Link Waze (kosong = auto)")
    with c2:
        gmap_custom = st.text_input("Link Google Maps (kosong = auto)")
    venue_waze_query = venue_name.replace(" ", "+") if venue_name else ""
    venue_gmaps_query = venue_name.replace(" ", "+") if venue_name else ""
    waze_link = waze_custom or (get_waze_link(venue_name, venue_address) if venue_name else "")
    gmap_link = gmap_custom or (get_gmap_link(venue_name, venue_address) if venue_name else "")

    st.markdown("---")
    st.markdown("## 7️⃣ Contact Person")
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Contact 1**")
        contact1_name  = st.text_input("Nama", placeholder="Ahmad bin Abdullah", key="c1n")
        contact1_phone = st.text_input("No Telefon", placeholder="011-12345678", key="c1p")
        contact1_wa    = get_whatsapp_number(contact1_phone) if contact1_phone else ""
        if contact1_phone: st.caption(f"📱 WA: {contact1_wa}")
    with c2:
        st.markdown("**Contact 2**")
        contact2_name  = st.text_input("Nama", placeholder="Siti binti Ibrahim", key="c2n")
        contact2_phone = st.text_input("No Telefon", placeholder="019-8765432", key="c2p")
        contact2_wa    = get_whatsapp_number(contact2_phone) if contact2_phone else ""
        if contact2_phone: st.caption(f"📱 WA: {contact2_wa}")

    st.markdown("---")
    st.markdown("## 8️⃣ Lagu Latar")
    c1, c2 = st.columns(2)
    with c1:
        music_url   = st.text_input("Link Direct MP3", placeholder="https://cdn.jsdelivr.net/gh/...")
    with c2:
        music_label = st.text_input("Nama Lagu", placeholder="Beautiful In White — Westlife")

    st.markdown("---")
    st.markdown("## 9️⃣ Kisah Cinta")
    c1, c2 = st.columns(2)
    with c1:
        love_year_1  = st.text_input("Tahun 1", placeholder="2022", key="ly1")
        love_story_1 = st.text_area("Kisah 1 — Pertemuan", height=80, key="ls1",
            placeholder="Kami mula berkenalan melalui...")
        love_year_2  = st.text_input("Tahun 2", placeholder="2023", key="ly2")
        love_story_2 = st.text_area("Kisah 2 — Bercinta", height=80, key="ls2",
            placeholder="Dengan restu keluarga...")
    with c2:
        love_year_3  = st.text_input("Tahun 3", placeholder="2025", key="ly3")
        love_story_3 = st.text_area("Kisah 3 — Bertunang", height=80, key="ls3",
            placeholder="Pada malam yang penuh bintang...")
    
    st.markdown("---")
    st.markdown("## 🎨 Dress Code")
    c1, c2 = st.columns(2)
    with c1:
        dresscode_theme    = st.text_input("Tema (BM)", placeholder="Dusty Blue & Gold")
    with c2:
        dresscode_theme_en = st.text_input("Tema (EN)", placeholder="Dusty Blue & Gold")

    st.markdown("---")
    st.markdown("## 💬 Contoh Ucapan Doa")
    st.caption("Ini ucapan sample yang akan dipapar dalam wall doa. Boleh kosongkan.")
    c1, c2 = st.columns(2)
    with c1:
        doa1_name = st.text_input("Nama Ucapan 1", placeholder="Kak Lina & Family", key="d1n")
        doa1_msg  = st.text_area("Ucapan 1", height=70, key="d1m",
            placeholder="Barakallahu lakuma...")
    with c2:
        doa2_name = st.text_input("Nama Ucapan 2", placeholder="Pak Long & Mak Long", key="d2n")
        doa2_msg  = st.text_area("Ucapan 2", height=70, key="d2m",
            placeholder="Tahniah! Semoga bahagia...")

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

    st.markdown("---")
    st.markdown("## 🚀 Jana & Deploy")
    required = {
        "Nama pengantin lelaki": groom_name,
        "Nama pengantin perempuan": bride_name,
        "Nama dewan": venue_name,
        "Alamat majlis": venue_address,
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

            data = {
                # Pengantin
                "groom_name":           groom_name,
                "bride_name":           bride_name,
                "groom_full":           groom_full,
                "bride_full":           bride_full,
                "groom_father":         groom_father,
                "groom_mother":         groom_mother,
                "bride_father":         bride_father,
                "bride_mother":         bride_mother,
                # Tuan Rumah
                "host_family":          host_family_custom,
                "host_family_full":     host_family_full,
                "host_message_bm":      host_message_bm,
                "host_message_en":      host_message_en,
                # Tarikh
                "date_display":         date_display,
                "date_day":             day_name,
                "date_hijri":           hijri_date,
                "date_iso":             date_iso,
                "date_dd":              str(event_date.day).zfill(2),
                "date_mm":              str(event_date.month).zfill(2),
                "date_yyyy":            str(event_date.year),
                "date_yyyymmdd":        date_yyyymmdd,
                # Masa
                "time_start":           time_start,
                "time_end":             time_end,
                "time_start_hhmm":      time_start_hhmm,
                "time_end_hhmm":        time_end_hhmm,
                # Aturcara
                "time_arrival":         time_arrival,
                "time_akad":            time_akad,
                "time_bersanding":      time_bersanding,
                "time_makan":           time_makan,
                "time_bersurai":        time_bersurai,
                # Venue
                "venue_name":           venue_name,
                "venue_fullname":       venue_fullname,
                "venue_address":        venue_address,
                "venue_city":           venue_city,
                "venue_waze_query":     venue_waze_query,
                "venue_gmaps_query":    venue_gmaps_query,
                "waze_link":            waze_link,
                "gmap_link":            gmap_link,
                # Contact
                "contact1_name":        contact1_name,
                "contact1_phone_display": contact1_phone,
                "contact1_phone_wa":    contact1_wa,
                "contact2_name":        contact2_name,
                "contact2_phone_display": contact2_phone,
                "contact2_phone_wa":    contact2_wa,
                # Lagu
                "music_url":            music_url,
                "music_label":          music_label,
                # Kisah
                "love_year_1":          love_year_1,
                "love_story_1":         love_story_1,
                "love_year_2":          love_year_2,
                "love_story_2":         love_story_2,
                "love_year_3":          love_year_3,
                "love_story_3":         love_story_3,
                # Dress Code
                "dresscode_theme":      dresscode_theme,
                "dresscode_theme_en":   dresscode_theme_en,
                # Doa sample
                "doa_sample1_name":     doa1_name,
                "doa_sample1_msg":      doa1_msg,
                "doa_sample2_name":     doa2_name,
                "doa_sample2_msg":      doa2_msg,
                # Media
                "hero_url":             hero_url,
                "photo1_url":           photo1_url,
                "photo2_url":           photo2_url,
                "photo3_url":           photo3_url,
                "opening_url":          opening_url,
                "video_url":            video_url,
                "gallery1_url":         g1,
                "gallery2_url":         g2,
                "gallery3_url":         g3,
                "gallery4_url":         g4,
                "gallery5_url":         g5,
            }

            replacements = build_replacements(data)
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

        # ── Toggle: template dah ada placeholder atau masih hardcoded? ──
        mode = st.radio(
            "Jenis template:",
            ["✅ Dah ada placeholders — terus upload",
             "🔧 Masih hardcoded — nak buat mapping dulu"],
            horizontal=True,
            key="conv_mode"
        )
        ready_to_upload = False  # flag: boleh terus ke bahagian upload?

        if mode.startswith("✅"):
            # ── FLOW A: Template dah siap, terus upload ──
            if found_phs:
                st.markdown(f"<div class='info-box'>✅ Dijumpai <b>{len(found_phs)} placeholder</b> dalam template — sedia untuk upload.</div>", unsafe_allow_html=True)
            else:
                st.warning("⚠️ Tiada placeholder dijumpai dalam template. Pastikan template ada `[Nama Pengantin Lelaki]` atau `{{GROOM_NAME}}`.")
            valid = []          # tak perlu mapping
            ready_to_upload = True

        else:
            # ── FLOW B: Template ada nama hardcoded, buat mapping ──
            st.markdown("## 2️⃣ Map Nilai Hardcoded → Placeholder")
            st.markdown(
                "<div class='info-box'>"
                "Taip nilai yang <b>ada dalam HTML</b> (eg: nama pengantin sebenar), "
                "pastu pilih placeholder yang nak digantikan."
                "</div>",
                unsafe_allow_html=True
            )

            all_phs = [
                "{{GROOM_NAME}}","{{BRIDE_NAME}}","{{GROOM_FULL_NAME}}","{{BRIDE_FULL_NAME}}",
                "{{GROOM_FATHER}}","{{GROOM_MOTHER}}","{{BRIDE_FATHER}}","{{BRIDE_MOTHER}}",
                "{{HOST_FAMILY}}","{{HOST_FAMILY_FULL}}","{{HOST_MESSAGE_BM}}","{{HOST_MESSAGE_EN}}",
                "{{DATE_DISPLAY}}","{{DATE_DAY}}","{{DATE_HIJRI}}","{{DATE_ISO}}",
                "{{DATE_DD}}","{{DATE_MM}}","{{DATE_YYYY}}","{{DATE_YYYYMMDD}}",
                "{{TIME_START}}","{{TIME_END}}","{{TIME_START_HHMM}}","{{TIME_END_HHMM}}",
                "{{TIME_ARRIVAL}}","{{TIME_AKAD}}","{{TIME_BERSANDING}}","{{TIME_MAKAN}}","{{TIME_BERSURAI}}",
                "{{VENUE_NAME}}","{{VENUE_FULLNAME}}","{{VENUE_ADDRESS}}","{{VENUE_CITY}}",
                "{{VENUE_WAZE_QUERY}}","{{VENUE_GMAPS_QUERY}}","{{WAZE_LINK}}","{{GMAP_LINK}}",
                "{{CONTACT1_NAME}}","{{CONTACT1_PHONE_DISPLAY}}","{{CONTACT1_PHONE_WA}}",
                "{{CONTACT2_NAME}}","{{CONTACT2_PHONE_DISPLAY}}","{{CONTACT2_PHONE_WA}}",
                "{{MUSIC_URL}}","{{MUSIC_LABEL}}",
                "{{LOVE_YEAR_1}}","{{LOVE_STORY_1}}","{{LOVE_YEAR_2}}","{{LOVE_STORY_2}}",
                "{{LOVE_YEAR_3}}","{{LOVE_STORY_3}}",
                "{{DRESSCODE_THEME}}","{{DRESSCODE_THEME_EN}}",
                "{{DOA_SAMPLE1_NAME}}","{{DOA_SAMPLE1_MSG}}","{{DOA_SAMPLE2_NAME}}","{{DOA_SAMPLE2_MSG}}",
                "{{HERO_PHOTO_URL}}","{{PHOTO1_URL}}","{{PHOTO2_URL}}","{{PHOTO3_URL}}",
                "{{OPENING_PHOTO_URL}}","{{VIDEO_URL}}",
            ]
            ph_options = {"-- Pilih --": ""}
            for ph in all_phs:
                ph_options[ph] = ph

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
            st.markdown("## 3️⃣ Preview Mapping")
            if valid:
                st.markdown(f"<div class='info-box'>✅ <b>{len(valid)} replacement</b> akan dibuat{'<br>⚠️ ' + str(len(not_found)) + ' nilai tidak jumpa' if not_found else ''}</div>", unsafe_allow_html=True)
                for m in valid:
                    st.markdown(f"- `{m['value']}` → `{m['placeholder']}` ({raw_html.count(m['value'])}x)")
                ready_to_upload = True
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
        can = bool(ready_to_upload and t_name and t_file and gh_token and gh_repo)
        if not can:
            miss = []
            if not ready_to_upload: miss.append("mapping values")
            if not t_name: miss.append("nama template")
            if not t_file: miss.append("nama fail")
            if not gh_token or not gh_repo: miss.append("GitHub settings")
            if miss: st.warning(f"⚠️ Lengkapkan: {', '.join(miss)}")

        if st.button("🚀 Upload Template!", disabled=not can):
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
    placeholders = [
        ("{{GROOM_NAME}}", "Nama panggilan pengantin lelaki"),
        ("{{BRIDE_NAME}}", "Nama panggilan pengantin perempuan"),
        ("{{GROOM_FULL_NAME}}", "Nama penuh pengantin lelaki"),
        ("{{BRIDE_FULL_NAME}}", "Nama penuh pengantin perempuan"),
        ("{{GROOM_FATHER}}", "Nama bapa pengantin lelaki"),
        ("{{GROOM_MOTHER}}", "Nama ibu pengantin lelaki"),
        ("{{BRIDE_FATHER}}", "Nama bapa pengantin perempuan"),
        ("{{BRIDE_MOTHER}}", "Nama ibu pengantin perempuan"),
        ("{{HOST_FAMILY}}", "Nama keluarga tuan rumah (ringkas)"),
        ("{{HOST_FAMILY_FULL}}", "Nama keluarga tuan rumah (penuh)"),
        ("{{HOST_MESSAGE_BM}}", "Mesej tuan rumah dalam BM"),
        ("{{HOST_MESSAGE_EN}}", "Mesej tuan rumah dalam EN"),
        ("{{DATE_DISPLAY}}", "Tarikh papar (eg: 20 September 2026)"),
        ("{{DATE_DAY}}", "Hari majlis (eg: Ahad)"),
        ("{{DATE_HIJRI}}", "Tarikh Hijri"),
        ("{{DATE_ISO}}", "Tarikh ISO"),
        ("{{DATE_DD}}", "Nombor hari"),
        ("{{DATE_MM}}", "Nombor bulan"),
        ("{{DATE_YYYY}}", "Tahun"),
        ("{{DATE_YYYYMMDD}}", "Tarikh format YYYYMMDD"),
        ("{{TIME_START}}", "Masa mula (eg: 11:00 PG)"),
        ("{{TIME_END}}", "Masa tamat (eg: 4:00 PTG)"),
        ("{{TIME_START_HHMM}}", "Masa mula format HHMM"),
        ("{{TIME_END_HHMM}}", "Masa tamat format HHMM"),
        ("{{TIME_ARRIVAL}}", "Masa ketibaan tetamu"),
        ("{{TIME_AKAD}}", "Masa akad nikah"),
        ("{{TIME_BERSANDING}}", "Masa persandingan"),
        ("{{TIME_MAKAN}}", "Masa jamuan makan"),
        ("{{TIME_BERSURAI}}", "Masa majlis bersurai"),
        ("{{VENUE_NAME}}", "Nama dewan / tempat"),
        ("{{VENUE_FULLNAME}}", "Nama penuh venue"),
        ("{{VENUE_ADDRESS}}", "Alamat penuh venue"),
        ("{{VENUE_CITY}}", "Bandar / negeri"),
        ("{{VENUE_WAZE_QUERY}}", "Query nama venue untuk Waze URL"),
        ("{{VENUE_GMAPS_QUERY}}", "Query nama venue untuk Google Maps URL"),
        ("{{WAZE_LINK}}", "Link Waze penuh"),
        ("{{GMAP_LINK}}", "Link Google Maps penuh"),
        ("{{CONTACT1_NAME}}", "Nama contact person 1"),
        ("{{CONTACT1_PHONE_DISPLAY}}", "No telefon contact 1 (display)"),
        ("{{CONTACT1_PHONE_WA}}", "No WhatsApp contact 1"),
        ("{{CONTACT2_NAME}}", "Nama contact person 2"),
        ("{{CONTACT2_PHONE_DISPLAY}}", "No telefon contact 2 (display)"),
        ("{{CONTACT2_PHONE_WA}}", "No WhatsApp contact 2"),
        ("{{MUSIC_URL}}", "Link direct MP3"),
        ("{{MUSIC_LABEL}}", "Nama lagu"),
        ("{{LOVE_YEAR_1}}", "Tahun kisah 1"),
        ("{{LOVE_STORY_1}}", "Cerita kisah 1 — pertemuan"),
        ("{{LOVE_YEAR_2}}", "Tahun kisah 2"),
        ("{{LOVE_STORY_2}}", "Cerita kisah 2 — bercinta"),
        ("{{LOVE_YEAR_3}}", "Tahun kisah 3"),
        ("{{LOVE_STORY_3}}", "Cerita kisah 3 — bertunang"),
        ("{{DRESSCODE_THEME}}", "Tema dress code (BM)"),
        ("{{DRESSCODE_THEME_EN}}", "Tema dress code (EN)"),
        ("{{DOA_SAMPLE1_NAME}}", "Nama contoh ucapan 1"),
        ("{{DOA_SAMPLE1_MSG}}", "Mesej contoh ucapan 1"),
        ("{{DOA_SAMPLE2_NAME}}", "Nama contoh ucapan 2"),
        ("{{DOA_SAMPLE2_MSG}}", "Mesej contoh ucapan 2"),
        ("{{HERO_PHOTO_URL}}", "Link gambar hero"),
        ("{{PHOTO1_URL}}", "Link gallery gambar 1"),
        ("{{PHOTO2_URL}}", "Link gallery gambar 2"),
        ("{{PHOTO3_URL}}", "Link gallery gambar 3"),
    ]
    for ph, label in placeholders:
        st.markdown(f"- `{ph}` — {label}")

# ─────────────────────────────────────────
#  PAGE: TEMPLATE INFO
# ─────────────────────────────────────────
elif "🗂️ Template Info" in page:
    st.markdown("# 🗂️ Senarai Template")

    gh_token = st.session_state.get("gh_token", "") or st.secrets.get("GH_TOKEN", "")
    gh_repo  = st.session_state.get("gh_repo",  "") or st.secrets.get("GH_REPO",  "")

    TEMPLATES = load_registry(gh_token, gh_repo)

    if st.button("🔄 Refresh"):
        st.cache_data.clear()
        st.rerun()

    st.markdown("---")

    if not TEMPLATES:
        st.info("Tiada template lagi. Upload template baru melalui 🔧 Template Converter.")
    else:
        for category, templates in TEMPLATES.items():
            emoji = "⭐" if category=="Essential" else "📸" if category=="Portrait" else "🎬" if category=="Cinematic" else "💎"
            st.markdown(f"## {emoji} {category}")
            for key, info in templates.items():
                # Fetch HTML untuk detect format
                tmpl_html = load_template(info["file"], gh_token, gh_repo)
                if tmpl_html:
                    fmt = detect_format(tmpl_html)
                    fmt_badge = "🟢 CURLY" if fmt == "curly" else "🔵 Square"
                    status = f"✅ Ada · {fmt_badge}"
                else:
                    status = "❌ Fail tidak jumpa"

                col_info, col_del = st.columns([5, 1])
                with col_info:
                    st.markdown(f"""
                    <div class='template-card'>
                        <span class='category-badge'>{category}</span>
                        <b style='color:#f0e8d8'>{info.get("preview_emoji","✨")} {info["name"]}</b><br>
                        <small style='color:#888'>{info.get("desc","")}</small><br>
                        <small>📁 <code>{info["file"]}</code> — {status}</small>
                    </div>""", unsafe_allow_html=True)
                with col_del:
                    st.markdown("<div style='padding-top:1.2rem'>", unsafe_allow_html=True)
                    if st.button("🗑️", key=f"del_{key}", help=f"Padam {info['name']}"):
                        st.session_state[f"confirm_del_{key}"] = True
                    st.markdown("</div>", unsafe_allow_html=True)

                # Confirm delete
                if st.session_state.get(f"confirm_del_{key}"):
                    st.warning(f"⚠️ Confirm padam **{info['name']}**? Ini akan remove dari registry.")
                    c1, c2, _ = st.columns([1, 1, 4])
                    with c1:
                        if st.button("✅ Ya, padam", key=f"yes_del_{key}"):
                            registry = load_registry(gh_token, gh_repo)
                            if category in registry and key in registry[category]:
                                del registry[category][key]
                                # Buang category kalau kosong
                                if not registry[category]:
                                    del registry[category]
                                ok = save_registry(gh_token, gh_repo, registry)
                                st.cache_data.clear()
                                del st.session_state[f"confirm_del_{key}"]
                                if ok:
                                    st.success(f"✅ {info['name']} dipadam dari registry.")
                                    st.rerun()
                                else:
                                    st.error("❌ Gagal update registry.")
                    with c2:
                        if st.button("❌ Batal", key=f"no_del_{key}"):
                            del st.session_state[f"confirm_del_{key}"]
                            st.rerun()

            st.markdown("")
