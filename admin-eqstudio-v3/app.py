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
    .metric-card {
        background: #1a1a1a; border: 1px solid #333; border-radius: 10px;
        padding: 1.2rem; text-align: center;
    }
    .metric-num { font-size: 2rem; font-weight: 700; color: #C9A96E; }
    .metric-lbl { font-size: 0.65rem; letter-spacing: 0.2em; text-transform: uppercase; color: #666; }
    .rsvp-row {
        display: flex; align-items: center; padding: 0.6rem 0;
        border-bottom: 1px solid #222; font-size: 0.82rem;
    }
    .badge-hadir { background: rgba(80,160,80,0.15); color: #80c080; border: 1px solid rgba(80,160,80,0.2); border-radius: 12px; padding: 2px 8px; font-size: 0.65rem; }
    .badge-tidak { background: rgba(196,80,80,0.15); color: #e08080; border: 1px solid rgba(196,80,80,0.2); border-radius: 12px; padding: 2px 8px; font-size: 0.65rem; }
    .doa-card-dash { background: #1e1e1e; border: 1px solid #2a2a2a; border-radius: 8px; padding: 0.8rem; margin-bottom: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  FIREBASE CONFIG
# ─────────────────────────────────────────
FIREBASE_DB_URL = "https://eqstudio-6225d-default-rtdb.asia-southeast1.firebasedatabase.app"

def firebase_get(path):
    """GET dari Firebase REST API"""
    try:
        r = requests.get(f"{FIREBASE_DB_URL}/{path}.json", timeout=8)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return None

def firebase_delete(path):
    """DELETE dari Firebase REST API"""
    try:
        r = requests.delete(f"{FIREBASE_DB_URL}/{path}.json", timeout=8)
        return r.status_code == 200
    except Exception:
        return False

# ─────────────────────────────────────────
#  TEMPLATE REGISTRY
# ─────────────────────────────────────────
TEMPLATES_DEFAULT = {
    "Essential": {
        "es_rosegold": {
            "name": "Rose Gold",
            "file": "Es Rose Gold.html",
            "has_photo": False,
            "has_portrait_photo": False,
            "preview_emoji": "🌹",
            "desc": "Tema rose gold & blush, warm parchment envelope",
        },
        "es_sage": {
            "name": "Sage Green",
            "file": "Es Sage Green.html",
            "has_photo": False,
            "has_portrait_photo": False,
            "preview_emoji": "🌿",
            "desc": "Tema sage green & warm cream",
        },
        "es_champagne": {
            "name": "Champagne Gold",
            "file": "Es Champagne Gold.html",
            "has_photo": False,
            "has_portrait_photo": False,
            "preview_emoji": "🥂",
            "desc": "Tema champagne gold & ivory",
        },
        "es_darkolive": {
            "name": "Dark Olive",
            "file": "Es Dark Olive.html",
            "has_photo": False,
            "has_portrait_photo": False,
            "preview_emoji": "🫒",
            "desc": "Tema dark olive & warm cream",
        },
        "es_dustyblue": {
            "name": "Dusty Blue",
            "file": "Es Dusty Blue.html",
            "has_photo": False,
            "has_portrait_photo": False,
            "preview_emoji": "🔵",
            "desc": "Tema dusty blue & warm sand",
        },
        "es_emerald": {
            "name": "Emerald Green",
            "file": "Es Emerald Green.html",
            "has_photo": False,
            "has_portrait_photo": False,
            "preview_emoji": "💎",
            "desc": "Tema emerald green & gold",
        },
        "es_navy": {
            "name": "Navy",
            "file": "Es Navy.html",
            "has_photo": False,
            "has_portrait_photo": False,
            "preview_emoji": "🫐",
            "desc": "Tema navy & silver",
        },
        "es_terracotta": {
            "name": "Terracotta",
            "file": "Es Terracotta.html",
            "has_photo": False,
            "has_portrait_photo": False,
            "preview_emoji": "🏺",
            "desc": "Tema terracotta & warm linen",
        },
        "es_blush": {
            "name": "Blush Pink",
            "file": "Es Blush Pink.html",
            "has_photo": False,
            "has_portrait_photo": False,
            "preview_emoji": "🌸",
            "desc": "Tema blush pink & ivory",
        },
        "es_mauve": {
            "name": "Mauve",
            "file": "Es Mauve.html",
            "has_photo": False,
            "has_portrait_photo": False,
            "preview_emoji": "💜",
            "desc": "Tema mauve & soft lilac",
        },
        "es_charcoal": {
            "name": "Charcoal",
            "file": "Es Charcoal.html",
            "has_photo": False,
            "has_portrait_photo": False,
            "preview_emoji": "⚫",
            "desc": "Tema charcoal & gold",
        },
        "es_darkbrown": {
            "name": "Dark Brown",
            "file": "Es Dark Brown.html",
            "has_photo": False,
            "has_portrait_photo": False,
            "preview_emoji": "🤎",
            "desc": "Tema dark brown & warm cream",
        },
        "es_chocolate": {
            "name": "Chocolate Brown",
            "file": "Es Chocolate Brown.html",
            "has_photo": False,
            "has_portrait_photo": False,
            "preview_emoji": "🍫",
            "desc": "Tema chocolate brown & caramel",
        },
    },
    "Portrait": {
        "pt_dustyblue": {
            "name": "Dusty Blue Portrait",
            "file": "Es Portrait Dusty Blue.html",
            "has_photo": False,
            "has_portrait_photo": True,
            "preview_emoji": "📸",
            "desc": "Split hero + cinematic banner. 2 slot gambar.",
        },
    },
    "Light": {
        "lt_rosegold": {
            "name": "Rose Gold Light",
            "file": "Es Light Rose Gold.html",
            "has_photo": False,
            "has_portrait_photo": False,
            "preview_emoji": "☀️",
            "desc": "Versi cerah warm parchment + soft glow",
        },
    },
}

REGISTRY_PATH = "templates/registry.json"
HISTORY_PATH  = "cards/history.json"

@st.cache_data(ttl=30)
def load_history(token, repo):
    if not token or not repo: return []
    try:
        url = f"https://api.github.com/repos/{repo}/contents/{HISTORY_PATH}"
        r = requests.get(url, headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}, timeout=8)
        if r.status_code == 200:
            import json, base64 as b64
            return json.loads(b64.b64decode(r.json()["content"]).decode("utf-8"))
        return []
    except Exception: return []

def save_history(token, repo, history):
    import json
    content = json.dumps(history, indent=2, ensure_ascii=False)
    result = github_upload_file(token, repo, HISTORY_PATH, content, "Update kad history")
    return result["success"]

def add_to_history(token, repo, entry):
    history = load_history(token, repo)
    history = [h for h in history if h.get("order_id") != entry["order_id"]]
    history.insert(0, entry)
    return save_history(token, repo, history[:100])

def delete_github_file(token, repo, filepath):
    api_url = f"https://api.github.com/repos/{repo}/contents/{filepath}"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    r = requests.get(api_url, headers=headers, timeout=10)
    if r.status_code != 200: return False, f"Fail tidak jumpa ({r.status_code})"
    sha = r.json().get("sha")
    r = requests.delete(api_url, headers=headers, json={"message": f"Delete kad: {filepath}", "sha": sha}, timeout=15)
    return (True, "OK") if r.status_code == 200 else (False, r.json().get("message", r.text))

@st.cache_data(ttl=60)
def load_registry(token, repo):
    if not token or not repo: return TEMPLATES_DEFAULT
    try:
        url = f"https://api.github.com/repos/{repo}/contents/{REGISTRY_PATH}"
        r = requests.get(url, headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}, timeout=8)
        if r.status_code == 200:
            import json, base64 as b64
            return json.loads(b64.b64decode(r.json()["content"]).decode("utf-8"))
        return TEMPLATES_DEFAULT
    except Exception: return TEMPLATES_DEFAULT

def save_registry(token, repo, registry):
    import json
    content = json.dumps(registry, indent=2, ensure_ascii=False)
    return github_upload_file(token, repo, REGISTRY_PATH, content, "Update template registry")["success"]

# ─────────────────────────────────────────
#  DETECT FORMAT & BUILD REPLACEMENTS
# ─────────────────────────────────────────
def detect_format(html):
    curly  = len(re.findall(r'\{\{[A-Z_]+\}\}', html))
    square = len(re.findall(r'\[[A-Za-z][^\]]{2,50}\]', html))
    return "curly" if curly >= square else "square"

def build_replacements(data):
    d = data
    r = {}
    def s(key): return str(d.get(key) or "")
    r["{{GROOM_NAME}}"]             = s("groom_name")
    r["{{BRIDE_NAME}}"]             = s("bride_name")
    r["{{GROOM_FULL_NAME}}"]        = s("groom_full") or s("groom_name")
    r["{{BRIDE_FULL_NAME}}"]        = s("bride_full") or s("bride_name")
    r["{{GROOM_FATHER}}"]           = s("groom_father")
    r["{{GROOM_MOTHER}}"]           = s("groom_mother")
    r["{{BRIDE_FATHER}}"]           = s("bride_father")
    r["{{BRIDE_MOTHER}}"]           = s("bride_mother")
    r["{{HOST_FAMILY}}"]            = s("host_family")
    r["{{HOST_FAMILY_FULL}}"]       = s("host_family_full") or s("host_family")
    r["{{HOST_MESSAGE_BM}}"]        = s("host_message_bm")
    r["{{HOST_MESSAGE_EN}}"]        = s("host_message_en")
    r["{{DATE_DISPLAY}}"]           = s("date_display")
    r["{{DATE_DAY}}"]               = s("date_day")
    r["{{DATE_HIJRI}}"]             = s("date_hijri")
    r["{{DATE_ISO}}"]               = s("date_iso")
    r["{{DATE_DD}}"]                = s("date_dd")
    r["{{DATE_MM}}"]                = s("date_mm")
    r["{{DATE_YYYY}}"]              = s("date_yyyy")
    r["{{DATE_YYYYMMDD}}"]          = s("date_yyyymmdd")
    r["{{TIME_START}}"]             = s("time_start")
    r["{{TIME_END}}"]               = s("time_end")
    r["{{TIME_START_SHORT}}"]       = s("time_start")
    r["{{TIME_END_SHORT}}"]         = s("time_end")
    r["{{TIME_START_HHMM}}"]        = s("time_start_hhmm")
    r["{{TIME_END_HHMM}}"]          = s("time_end_hhmm")
    r["{{TIME_ARRIVAL}}"]           = s("time_arrival")
    r["{{TIME_AKAD}}"]              = s("time_akad")
    r["{{TIME_BERSANDING}}"]        = s("time_bersanding")
    r["{{TIME_MAKAN}}"]             = s("time_makan")
    r["{{TIME_BERSURAI}}"]          = s("time_bersurai")
    r["{{VENUE_NAME}}"]             = s("venue_name")
    r["{{VENUE_FULLNAME}}"]         = s("venue_fullname") or s("venue_name")
    r["{{VENUE_ADDRESS}}"]          = s("venue_address")
    r["{{VENUE_CITY}}"]             = s("venue_city")
    r["{{VENUE_WAZE_QUERY}}"]       = s("venue_waze_query")
    r["{{VENUE_GMAPS_QUERY}}"]      = s("venue_gmaps_query")
    r["{{VENUE_NAME_URL}}"]         = s("venue_name").replace(" ", "+")
    r["{{GROOM_NAME_URL}}"]         = s("groom_name").replace(" ", "+")
    r["{{BRIDE_NAME_URL}}"]         = s("bride_name").replace(" ", "+")
    r["{{WAZE_LINK}}"]              = s("waze_link")
    r["{{GMAP_LINK}}"]              = s("gmap_link")
    r["{{CONTACT1_NAME}}"]          = s("contact1_name")
    r["{{CONTACT1_PHONE_DISPLAY}}"] = s("contact1_phone_display")
    r["{{CONTACT1_PHONE_WA}}"]      = s("contact1_phone_wa")
    r["{{CONTACT2_NAME}}"]          = s("contact2_name")
    r["{{CONTACT2_PHONE_DISPLAY}}"] = s("contact2_phone_display")
    r["{{CONTACT2_PHONE_WA}}"]      = s("contact2_phone_wa")
    r["{{MUSIC_URL}}"]              = s("music_url")
    r["{{MUSIC_LABEL}}"]            = s("music_label")
    r["{{LOVE_YEAR_1}}"]            = s("love_year_1")
    r["{{LOVE_STORY_1}}"]           = s("love_story_1")
    r["{{LOVE_YEAR_2}}"]            = s("love_year_2")
    r["{{LOVE_STORY_2}}"]           = s("love_story_2")
    r["{{LOVE_YEAR_3}}"]            = s("love_year_3")
    r["{{LOVE_STORY_3}}"]           = s("love_story_3")
    r["{{LOVE_YEAR_4}}"]            = s("love_year_4")
    r["{{DRESSCODE_THEME}}"]        = s("dresscode_theme")
    r["{{DRESSCODE_THEME_EN}}"]     = s("dresscode_theme_en")
    r["{{DRESSCODE_NOTE}}"]         = s("dresscode_note")
    r["{{DRESSCODE_NOTE_EN}}"]      = s("dresscode_note") # same for now
    r["{{COLOR1_HEX}}"]             = s("color1_hex")
    r["{{COLOR1_NAME}}"]            = s("color1_name")
    r["{{COLOR2_HEX}}"]             = s("color2_hex")
    r["{{COLOR2_NAME}}"]            = s("color2_name")
    r["{{COLOR3_HEX}}"]             = s("color3_hex")
    r["{{COLOR3_NAME}}"]            = s("color3_name")
    r["{{COLOR4_HEX}}"]             = s("color4_hex")
    r["{{COLOR4_NAME}}"]            = s("color4_name")
    r["{{COLOR5_HEX}}"]             = s("color5_hex")
    r["{{COLOR5_NAME}}"]            = s("color5_name")
    r["{{DOA_SAMPLE1_NAME}}"]       = s("doa_sample1_name")
    r["{{DOA_SAMPLE1_MSG}}"]        = s("doa_sample1_msg")
    r["{{DOA_SAMPLE2_NAME}}"]       = s("doa_sample2_name")
    r["{{DOA_SAMPLE2_MSG}}"]        = s("doa_sample2_msg")
    r["{{QR_CODE_URL}}"]            = s("qr_code_url")
    r["{{HERO_PHOTO_URL}}"]         = s("hero_url")
    r["{{PHOTO1_URL}}"]             = s("photo1_url")   # portrait split
    r["{{PHOTO2_URL}}"]             = s("photo2_url")   # portrait cinematic
    r["{{PHOTO3_URL}}"]             = s("photo3_url")
    r["{{OPENING_PHOTO_URL}}"]      = s("opening_url")
    r["{{VIDEO_URL}}"]              = s("video_url")
    r["{{GALLERY1_URL}}"]           = s("gallery1_url")
    r["{{GALLERY2_URL}}"]           = s("gallery2_url")
    r["{{GALLERY3_URL}}"]           = s("gallery3_url")
    r["{{GALLERY4_URL}}"]           = s("gallery4_url")
    r["{{GALLERY5_URL}}"]           = s("gallery5_url")

    # Calendar
    import calendar as _cal
    yyyymmdd = s("date_yyyymmdd")
    if yyyymmdd and len(yyyymmdd) == 8:
        _yr  = int(yyyymmdd[:4])
        _mo  = int(yyyymmdd[4:6])
        _day = int(yyyymmdd[6:8])
        _months_ms = ["","Januari","Februari","Mac","April","Mei","Jun","Julai","Ogos","September","Oktober","November","Disember"]
        _months_en = ["","January","February","March","April","May","June","July","August","September","October","November","December"]
        r["{{CAL_MONTH_LABEL}}"] = f"{_months_ms[_mo]} {_yr}"
        r["{{CAL_YEAR_LABEL}}"]  = f"{_months_en[_mo]} {_yr}"
        _first_weekday = _cal.weekday(_yr, _mo, 1)
        _offset = (_first_weekday + 1) % 7
        _total_days = _cal.monthrange(_yr, _mo)[1]
        _cells = ""
        for _ in range(_offset):
            _cells += '<div class="cdd em"></div>'
        for _d in range(1, _total_days + 1):
            _hl = " hl" if _d == _day else ""
            _cells += f'<div class="cdd{_hl}">{_d}</div>'
        r["{{CAL_GRID_CELLS}}"] = _cells

    # Countdown
    hhmm = s("time_start_hhmm")
    if yyyymmdd and hhmm:
        iso_date = f"{yyyymmdd[:4]}-{yyyymmdd[4:6]}-{yyyymmdd[6:8]}"
        iso_time = f"{hhmm[:2]}:{hhmm[2:]}:00"
        r["'{{DATE_YYYYMMDD}}T{{TIME_START_HHMM}}:00'"] = f"'{iso_date}T{iso_time}'"
        r["{{DATE_YYYYMMDD}}T{{TIME_START_HHMM}}:00"]   = f"{iso_date}T{iso_time}"

    return {k: v for k, v in r.items() if v}

def apply_replacements(html, replacements):
    for key, val in sorted(replacements.items(), key=lambda x: len(x[0]), reverse=True):
        if val:
            html = html.replace(key, val)
    return html

# ─────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────
def load_template(filename, token="", repo=""):
    if token and repo:
        try:
            url = f"https://api.github.com/repos/{repo}/contents/templates/{filename}"
            r = requests.get(url, headers={"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}, timeout=10)
            if r.status_code == 200:
                import base64 as b64
                return b64.b64decode(r.json()["content"]).decode("utf-8")
        except Exception: pass
    path = BASE_DIR / "templates" / filename
    if path.exists():
        return path.read_text(encoding="utf-8")
    return None

def generate_order_id():
    return f"EQ{datetime.now().strftime('%y%m%d%H%M%S')}"

def file_to_data_url(uploaded_file):
    b64 = base64.b64encode(uploaded_file.read()).decode()
    return f"data:{uploaded_file.type};base64,{b64}"

def get_whatsapp_number(phone):
    phone = re.sub(r'\D', '', phone)
    if phone.startswith('0'): phone = '60' + phone[1:]
    elif not phone.startswith('60'): phone = '60' + phone
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
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json", "X-GitHub-Api-Version": "2022-11-28"}
    sha = None
    r = requests.get(api_url, headers=headers, timeout=15)
    if r.status_code == 200:
        sha = r.json().get("sha")
    content_b64 = base64.b64encode(content.encode("utf-8")).decode("utf-8")
    payload = {"message": commit_msg, "content": content_b64}
    if sha: payload["sha"] = sha
    r = requests.put(api_url, headers=headers, json=payload, timeout=30)
    if r.status_code in (200, 201):
        data = r.json()
        raw_url = data["content"]["download_url"]
        parts = raw_url.replace("https://raw.githubusercontent.com/", "").split("/")
        user, repo_name = parts[0], parts[1]
        file_path = "/".join(parts[3:])
        return {"success": True, "pages_url": f"https://{user}.github.io/{repo_name}/{file_path}", "raw_url": raw_url}
    try: err = r.json().get("message", r.text)
    except Exception: err = r.text
    return {"success": False, "error": f"GitHub API error {r.status_code}: {err}"}

def validate_github_token(token, repo):
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}
    r = requests.get(f"https://api.github.com/repos/{repo}", headers=headers, timeout=10)
    if r.status_code == 200: return True, "ok" if r.json().get("has_pages") else "no_pages"
    elif r.status_code == 401: return False, "Token tidak valid atau expired."
    elif r.status_code == 404: return False, f"Repo `{repo}` tidak jumpa."
    return False, f"Error {r.status_code}"

# ─────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## 💍 EQStudio Admin")
    st.markdown("---")
    page = st.radio(
        "Navigation",
        ["🆕 Jana Kad Baru", "📊 RSVP & Doa", "🔧 Template Converter", "📜 History", "⚙️ GitHub Settings", "📋 Cara Guna", "🗂️ Template Info"],
        label_visibility="collapsed"
    )
    st.markdown("---")
    gh_token = st.session_state.get("gh_token", "") or st.secrets.get("GH_TOKEN", "")
    gh_repo  = st.session_state.get("gh_repo",  "") or st.secrets.get("GH_REPO",  "")
    if gh_token and gh_repo:
        st.markdown(f"<div style='font-size:0.75rem;color:#4CAF50'>✅ <b style='color:#C9A96E'>GitHub</b> Connected</div>", unsafe_allow_html=True)
        st.markdown(f"<div style='font-size:0.7rem;color:#666;margin-top:2px'>📁 {gh_repo}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-size:0.75rem;color:#888'>⚠️ GitHub belum setup</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<div style='font-size:0.75rem;color:#666'><b style='color:#C9A96E'>EQStudio</b><br>Admin v4.0</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────
#  PAGE: GITHUB SETTINGS
# ─────────────────────────────────────────
if "⚙️ GitHub Settings" in page:
    st.markdown("# ⚙️ GitHub Settings")
    with st.expander("📋 Langkah setup", expanded=True):
        st.markdown("""
        **1.** Buat repo Public di [github.com/new](https://github.com/new) — tick "Add a README"
        **2.** Aktifkan GitHub Pages → Settings → Pages → Branch: main → Save
        **3.** Jana token di [github.com/settings/tokens/new](https://github.com/settings/tokens/new) → scope: `repo`
        """)
    col1, col2 = st.columns(2)
    with col1:
        input_token = st.text_input("GitHub Token", type="password", value=st.session_state.get("gh_token", ""), placeholder="ghp_xxxxxxxxxxxx")
    with col2:
        input_repo = st.text_input("Repo (username/repo)", value=st.session_state.get("gh_repo", ""), placeholder="nureqmal/eqstudio-cards")
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
#  PAGE: RSVP & DOA DASHBOARD
# ─────────────────────────────────────────
elif "📊 RSVP & Doa" in page:
    st.markdown("# 📊 RSVP & Doa Dashboard")
    st.markdown("Data realtime dari Firebase. Refresh page untuk update terbaru.")
    st.markdown("---")

    gh_token = st.session_state.get("gh_token", "") or st.secrets.get("GH_TOKEN", "")
    gh_repo  = st.session_state.get("gh_repo",  "") or st.secrets.get("GH_REPO",  "")

    # Load history to get list of generated kads
    history = load_history(gh_token, gh_repo) if (gh_token and gh_repo) else []

    if not history:
        st.info("Belum ada kad yang di-deploy. Jana kad dulu melalui 🆕 Jana Kad Baru.")
    else:
        # Kad selector
        kad_options = {f"{h['groom']} & {h['bride']} [{h['order_id']}]": h['order_id'] for h in history}
        selected_label = st.selectbox("Pilih Kad", list(kad_options.keys()))
        selected_order_id = kad_options[selected_label]
        selected_entry = next((h for h in history if h['order_id'] == selected_order_id), {})

        st.markdown(f"""
        <div class='info-box'>
            <b>{selected_entry.get('groom','')} & {selected_entry.get('bride','')}</b><br>
            📅 {selected_entry.get('date','')} &nbsp;·&nbsp;
            🎨 {selected_entry.get('template','')} &nbsp;·&nbsp;
            <span class='order-id'>{selected_order_id}</span>
        </div>""", unsafe_allow_html=True)

        if st.button("🔄 Refresh Data"):
            st.rerun()

        st.markdown("---")

        # Load data dari Firebase
        kad_path = f"kads/{selected_order_id}"
        with st.spinner("Memuatkan data Firebase..."):
            rsvp_data     = firebase_get(f"{kad_path}/rsvp") or {}
            doa_data      = firebase_get(f"{kad_path}/doa") or {}
            registry_data = firebase_get(f"{kad_path}/registry") or {}

        rsvp_list     = sorted(rsvp_data.values(),     key=lambda x: x.get('t',0), reverse=True) if rsvp_data else []
        doa_list      = sorted(doa_data.values(),      key=lambda x: x.get('t',0), reverse=True) if doa_data else []
        registry_list = sorted(registry_data.values(), key=lambda x: x.get('t',0), reverse=True) if registry_data else []

        hadir_list = [r for r in rsvp_list if r.get('s') == 'hadir']
        tidak_list = [r for r in rsvp_list if r.get('s') != 'hadir']
        total_pax  = sum(int(r.get('c', 0)) for r in hadir_list)

        # Stats
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"<div class='metric-card'><div class='metric-num'>{len(rsvp_list)}</div><div class='metric-lbl'>Jumlah RSVP</div></div>", unsafe_allow_html=True)
        with c2:
            st.markdown(f"<div class='metric-card'><div class='metric-num' style='color:#80c080'>{len(hadir_list)}</div><div class='metric-lbl'>Hadir</div></div>", unsafe_allow_html=True)
        with c3:
            st.markdown(f"<div class='metric-card'><div class='metric-num'>{total_pax}</div><div class='metric-lbl'>Jumlah Pax</div></div>", unsafe_allow_html=True)
        with c4:
            st.markdown(f"<div class='metric-card'><div class='metric-num'>{len(doa_list)}</div><div class='metric-lbl'>Ucapan & Doa</div></div>", unsafe_allow_html=True)

        st.markdown("---")

        # Tabs
        tab1, tab2, tab3 = st.tabs(["📋 Senarai RSVP", "💬 Ucapan & Doa", "🎁 Salam Kaut"])

        # ── TAB 1: RSVP ──
        with tab1:
            if not rsvp_list:
                st.info("Belum ada RSVP lagi.")
            else:
                # Export CSV
                import io, csv
                buf = io.StringIO()
                writer = csv.writer(buf)
                writer.writerow(["No","Nama","Pax","Status","Masa"])
                for i, r in enumerate(rsvp_list, 1):
                    t = datetime.fromtimestamp(r.get('t',0)/1000).strftime('%d/%m/%Y %H:%M') if r.get('t') else ''
                    writer.writerow([i, r.get('n',''), r.get('c',''), 'Hadir' if r.get('s')=='hadir' else 'Tidak Hadir', t])
                st.download_button("⬇️ Export CSV", buf.getvalue().encode('utf-8-sig'), f"rsvp-{selected_order_id}.csv", "text/csv")

                st.markdown(f"**{len(rsvp_list)} RSVP** · Hadir: {len(hadir_list)} · Tidak: {len(tidak_list)} · Pax: {total_pax}")
                st.markdown("---")
                for i, r in enumerate(rsvp_list, 1):
                    t = datetime.fromtimestamp(r.get('t',0)/1000).strftime('%d/%m %H:%M') if r.get('t') else ''
                    badge = f"<span class='badge-hadir'>Hadir</span>" if r.get('s')=='hadir' else f"<span class='badge-tidak'>Tidak</span>"
                    st.markdown(f"<div class='rsvp-row'><span style='color:#555;width:28px'>{i}.</span><span style='flex:1;color:#f0e8d8'>{r.get('n','')}</span><span style='width:50px;color:#888'>{r.get('c','')} pax</span>{badge}<span style='width:90px;font-size:0.65rem;color:#555;text-align:right'>{t}</span></div>", unsafe_allow_html=True)

        # ── TAB 2: DOA ──
        with tab2:
            if not doa_list:
                st.info("Belum ada ucapan lagi.")
            else:
                # Export CSV
                buf2 = io.StringIO()
                writer2 = csv.writer(buf2)
                writer2.writerow(["No","Nama","Ucapan","Masa"])
                for i, d in enumerate(doa_list, 1):
                    t = datetime.fromtimestamp(d.get('t',0)/1000).strftime('%d/%m/%Y %H:%M') if d.get('t') else ''
                    writer2.writerow([i, d.get('n',''), d.get('m',''), t])
                st.download_button("⬇️ Export CSV", buf2.getvalue().encode('utf-8-sig'), f"doa-{selected_order_id}.csv", "text/csv")

                st.markdown(f"**{len(doa_list)} ucapan**")
                st.markdown("---")
                for d in doa_list:
                    t = datetime.fromtimestamp(d.get('t',0)/1000).strftime('%d/%m %H:%M') if d.get('t') else ''
                    st.markdown(f"<div class='doa-card-dash'><div style='color:#C9A96E;font-size:0.7rem;margin-bottom:0.3rem'>✦ {d.get('n','')} <span style='color:#555;float:right'>{t}</span></div><div style='color:#e0d8d0;font-size:0.82rem'>{d.get('m','')}</div></div>", unsafe_allow_html=True)

        # ── TAB 3: SALAM KAUT ──
        with tab3:
            if not registry_list:
                st.info("Belum ada salam kaut lagi.")
            else:
                buf3 = io.StringIO()
                writer3 = csv.writer(buf3)
                writer3.writerow(["No","Nama","Masa"])
                for i, r in enumerate(registry_list, 1):
                    t = datetime.fromtimestamp(r.get('t',0)/1000).strftime('%d/%m/%Y %H:%M') if r.get('t') else ''
                    writer3.writerow([i, r.get('n',''), t])
                st.download_button("⬇️ Export CSV", buf3.getvalue().encode('utf-8-sig'), f"registry-{selected_order_id}.csv", "text/csv")

                st.markdown(f"**{len(registry_list)} nama**")
                st.markdown("---")
                for i, r in enumerate(registry_list, 1):
                    t = datetime.fromtimestamp(r.get('t',0)/1000).strftime('%d/%m %H:%M') if r.get('t') else ''
                    st.markdown(f"<div class='rsvp-row'><span style='color:#555;width:28px'>{i}.</span><span style='flex:1;color:#f0e8d8'>{r.get('n','')}</span><span style='font-size:0.65rem;color:#555'>{t}</span></div>", unsafe_allow_html=True)

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
    if st.button("🔄 Refresh senarai template"): st.cache_data.clear(); st.rerun()
    cat_sel = st.selectbox("Category", list(TEMPLATES.keys()))
    tmpl_opts = TEMPLATES[cat_sel]
    tmpl_key = st.selectbox("Template", list(tmpl_opts.keys()), format_func=lambda k: f"{tmpl_opts[k]['preview_emoji']}  {tmpl_opts[k]['name']}")
    sel = tmpl_opts[tmpl_key]
    tmpl_html_check = load_template(sel["file"], gh_token, gh_repo)
    tmpl_fmt = detect_format(tmpl_html_check) if tmpl_html_check else "curly"
    st.markdown(f"<div class='info-box'>{sel['preview_emoji']} <b>{sel['name']}</b> — {sel['desc']}</div>", unsafe_allow_html=True)
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
        if parent_side == "Lelaki": host_family = f"Keluarga {groom_father}" if groom_father else ""
        elif parent_side == "Perempuan": host_family = f"Keluarga {bride_father}" if bride_father else ""
        else:
            gf = groom_father.split()[1] if groom_father and len(groom_father.split()) > 1 else groom_father
            bf = bride_father.split()[1] if bride_father and len(bride_father.split()) > 1 else bride_father
            host_family = f"Keluarga {gf} & Keluarga {bf}" if (gf and bf) else f"Keluarga {gf or bf}"
        host_family_custom = st.text_input("Nama Keluarga Tuan Rumah", value=host_family)
        host_family_full   = st.text_input("Nama Penuh (footer)", placeholder="Keluarga Haji Ahmad & Keluarga Haji Ibrahim")
    with c2:
        host_message_bm = st.text_area("Mesej Tuan Rumah (BM)", height=100, placeholder="Dengan penuh kerendahan hati...")
        host_message_en = st.text_area("Mesej Tuan Rumah (EN)", height=100, placeholder="With heartfelt gratitude...")
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
        _hm = re.search(r'(\d{1,2}):(\d{2})', time_start)
        time_start_hhmm = f"{int(_hm.group(1)):02d}{int(_hm.group(2)):02d}" if _hm else "1100"
        _hm2 = re.search(r'(\d{1,2}):(\d{2})', time_end)
        time_end_hhmm = f"{int(_hm2.group(1)):02d}{int(_hm2.group(2)):02d}" if _hm2 else "1600"
        date_iso = f"{event_date.isoformat()}T{time_start_hhmm[:2]}:{time_start_hhmm[2:]}:00"
        st.markdown(f"<div class='info-box'>📅 {day_name}, {date_display}<br>🕐 {time_start} — {time_end}<br>🗓️ {hijri_date or '—'}</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("## 5️⃣ Aturcara")
    c1, c2 = st.columns(2)
    with c1:
        time_arrival    = st.text_input("🌅 Ketibaan Tetamu", value=time_start)
        time_akad       = st.text_input("🌸 Akad Nikah", placeholder="11:30 PG")
        time_bersanding = st.text_input("👑 Persandingan", placeholder="12:30 TG")
    with c2:
        time_makan    = st.text_input("🍽️ Jamuan Makan", placeholder="1:00 PTG")
        time_bersurai = st.text_input("🌙 Majlis Bersurai", value=time_end)
    st.markdown("---")
    st.markdown("## 6️⃣ Lokasi")
    venue_name     = st.text_input("Nama Dewan / Tempat")
    venue_fullname = st.text_input("Nama Penuh Venue")
    venue_address  = st.text_area("Alamat Penuh", height=70)
    venue_city     = st.text_input("Bandar / Negeri")
    c1, c2 = st.columns(2)
    with c1: waze_custom = st.text_input("Link Waze (kosong = auto)")
    with c2: gmap_custom = st.text_input("Link Google Maps (kosong = auto)")
    venue_waze_query  = venue_name.replace(" ", "+") if venue_name else ""
    venue_gmaps_query = venue_name.replace(" ", "+") if venue_name else ""
    waze_link = waze_custom or (get_waze_link(venue_name, venue_address) if venue_name else "")
    gmap_link = gmap_custom or (get_gmap_link(venue_name, venue_address) if venue_name else "")
    st.markdown("---")
    st.markdown("## 7️⃣ Contact Person")
    c1, c2 = st.columns(2)
    with c1:
        contact1_name  = st.text_input("Nama", key="c1n")
        contact1_phone = st.text_input("No Telefon", key="c1p")
        contact1_wa    = get_whatsapp_number(contact1_phone) if contact1_phone else ""
    with c2:
        contact2_name  = st.text_input("Nama", key="c2n")
        contact2_phone = st.text_input("No Telefon", key="c2p")
        contact2_wa    = get_whatsapp_number(contact2_phone) if contact2_phone else ""
    st.markdown("---")
    st.markdown("## 8️⃣ Lagu Latar")
    c1, c2 = st.columns(2)
    with c1: music_url   = st.text_input("Link Direct MP3 (Dropbox)")
    with c2: music_label = st.text_input("Nama Lagu", placeholder="Beautiful In White — Westlife")
    st.markdown("---")
    st.markdown("## 9️⃣ QR Code Salam Kaut")
    qr_method = st.radio("Cara QR Code", ["📎 Upload Gambar", "🔗 URL"], horizontal=True)
    qr_code_url = ""
    if qr_method == "📎 Upload Gambar":
        qr_file = st.file_uploader("Upload QR Code", type=["png","jpg","jpeg","webp"])
        if qr_file:
            qr_code_url = file_to_data_url(qr_file)
            st.image(qr_file, width=160)
    else:
        qr_code_url = st.text_input("URL QR Code")
    st.markdown("---")
    st.markdown("## 🔟 Kisah Cinta")
    c1, c2 = st.columns(2)
    with c1:
        love_year_1  = st.text_input("Tahun 1", key="ly1")
        love_story_1 = st.text_area("Kisah 1 — Pertemuan", height=80, key="ls1")
        love_year_2  = st.text_input("Tahun 2", key="ly2")
        love_story_2 = st.text_area("Kisah 2 — Bercinta", height=80, key="ls2")
    with c2:
        love_year_3  = st.text_input("Tahun 3", key="ly3")
        love_story_3 = st.text_area("Kisah 3 — Bertunang", height=80, key="ls3")
    love_year_4 = str(event_date.year)
    st.markdown("---")
    st.markdown("## 🎨 Dress Code")
    c1, c2 = st.columns(2)
    with c1:
        dresscode_theme    = st.text_input("Tema (BM)", placeholder="Sage Green & Warm Cream")
        dresscode_theme_en = st.text_input("Tema (EN)", placeholder="Sage Green & Warm Cream")
        dresscode_note     = st.text_input("Nota", value="Elakkan warna putih tulen — reserved untuk pengantin")
    with c2:
        st.markdown("<small style='color:#888'>Warna Swatch</small>", unsafe_allow_html=True)
    SWATCH_DEFAULTS = [("#7d9b76","Sage"),("#a8c5a0","Mist"),("#f0ede6","Ivory"),("#d4a574","Champagne"),("#4a6741","Forest")]
    swatch_cols = st.columns(5)
    swatches = []
    for i, col in enumerate(swatch_cols):
        with col:
            hex_val  = st.color_picker(f"W{i+1}", value=SWATCH_DEFAULTS[i][0], key=f"sw_hex_{i}")
            name_val = st.text_input(f"N{i+1}", value=SWATCH_DEFAULTS[i][1], key=f"sw_name_{i}", label_visibility="collapsed")
            swatches.append((hex_val, name_val))
    color1_hex,color1_name = swatches[0]; color2_hex,color2_name = swatches[1]
    color3_hex,color3_name = swatches[2]; color4_hex,color4_name = swatches[3]
    color5_hex,color5_name = swatches[4]
    st.markdown("---")
    st.markdown("## 💬 Contoh Ucapan Doa")
    c1, c2 = st.columns(2)
    with c1:
        doa1_name = st.text_input("Nama 1", placeholder="Kak Lina & Family", key="d1n")
        doa1_msg  = st.text_area("Ucapan 1", height=70, key="d1m")
    with c2:
        doa2_name = st.text_input("Nama 2", placeholder="Pak Long", key="d2n")
        doa2_msg  = st.text_area("Ucapan 2", height=70, key="d2m")
    st.markdown("---")

    # Photos
    hero_url = photo1_url = photo2_url = photo3_url = opening_url = video_url = ""
    g1=g2=g3=g4=g5=""
    is_portrait = sel.get("has_portrait_photo", False)
    if not is_portrait and tmpl_html_check:
        is_portrait = "{{PHOTO1_URL}}" in tmpl_html_check and "{{PHOTO2_URL}}" in tmpl_html_check

    if is_portrait:
        st.markdown("## 📸 Gambar Portrait (2 slot)")
        pm = st.radio("Cara gambar", ["📎 Upload", "🔗 URL"], horizontal=True, key="portrait_pm")
        if pm == "📎 Upload":
            c1, c2 = st.columns(2)
            with c1:
                st.caption("🖼️ Hero (kiri) — potret")
                ph = st.file_uploader("Hero", type=["jpg","jpeg","png","webp"], key="ph")
                if ph: photo1_url = file_to_data_url(ph); st.image(ph, width=120)
            with c2:
                st.caption("🎬 Cinematic (banner) — landscape")
                pc = st.file_uploader("Cinematic", type=["jpg","jpeg","png","webp"], key="pc")
                if pc: photo2_url = file_to_data_url(pc); st.image(pc, width=120)
        else:
            c1, c2 = st.columns(2)
            with c1: photo1_url = st.text_input("Hero URL")
            with c2: photo2_url = st.text_input("Cinematic URL")
        st.markdown("---")

    elif sel.get("has_photo"):
        st.markdown("## 🖼️ Gambar")
        pm = st.radio("Cara gambar", ["📎 Upload", "🔗 URL"], horizontal=True)
        if pm == "📎 Upload":
            c1, c2 = st.columns(2)
            with c1:
                hf = st.file_uploader("Hero", type=["jpg","jpeg","png","webp"], key="hero")
                p1 = st.file_uploader("Gallery 1", type=["jpg","jpeg","png","webp"], key="p1")
            with c2:
                p2 = st.file_uploader("Gallery 2", type=["jpg","jpeg","png","webp"], key="p2")
                p3 = st.file_uploader("Gallery 3", type=["jpg","jpeg","png","webp"], key="p3")
            if hf: hero_url   = file_to_data_url(hf)
            if p1: photo1_url = file_to_data_url(p1)
            if p2: photo2_url = file_to_data_url(p2)
            if p3: photo3_url = file_to_data_url(p3)
        else:
            hero_url   = st.text_input("Hero URL")
            photo1_url = st.text_input("Gallery 1 URL")
            photo2_url = st.text_input("Gallery 2 URL")
            photo3_url = st.text_input("Gallery 3 URL")
        st.markdown("---")

    st.markdown("---")
    st.markdown("## 🚀 Jana & Deploy")
    required = {"Nama pengantin lelaki": groom_name, "Nama pengantin perempuan": bride_name, "Nama dewan": venue_name}
    missing = [k for k, v in required.items() if not v]
    if missing: st.warning(f"⚠️ Sila lengkapkan: **{', '.join(missing)}**")
    if github_ready:
        deploy_mode = st.radio("Mode", ["🚀 Deploy ke GitHub Pages", "⬇️ Download sahaja"], horizontal=True)
    else:
        deploy_mode = "⬇️ Download sahaja"

    if st.button("✨ Jana Kad Sekarang!", disabled=bool(missing)):
        template_html = load_template(sel["file"], gh_token, gh_repo)
        if template_html is None:
            st.error(f"❌ Template tidak jumpa: `templates/{sel['file']}`")
        else:
            # ── GENERATE UNIQUE KAD_ID FROM ORDER_ID ──
            order_id = generate_order_id()
            kad_id   = order_id.lower()  # eg: eq260603143022

            # Replace KAD_ID in template with unique order-based ID
            template_html = re.sub(
                r"const KAD_ID\s*=\s*'[^']*'",
                f"const KAD_ID='{kad_id}'",
                template_html
            )

            data = {
                "groom_name": groom_name, "bride_name": bride_name,
                "groom_full": groom_full, "bride_full": bride_full,
                "groom_father": groom_father, "groom_mother": groom_mother,
                "bride_father": bride_father, "bride_mother": bride_mother,
                "host_family": host_family_custom, "host_family_full": host_family_full,
                "host_message_bm": host_message_bm, "host_message_en": host_message_en,
                "date_display": date_display, "date_day": day_name, "date_hijri": hijri_date,
                "date_iso": date_iso, "date_dd": str(event_date.day).zfill(2),
                "date_mm": str(event_date.month).zfill(2), "date_yyyy": str(event_date.year),
                "date_yyyymmdd": date_yyyymmdd,
                "time_start": time_start, "time_end": time_end,
                "time_start_hhmm": time_start_hhmm, "time_end_hhmm": time_end_hhmm,
                "time_arrival": time_arrival, "time_akad": time_akad,
                "time_bersanding": time_bersanding, "time_makan": time_makan,
                "time_bersurai": time_bersurai,
                "venue_name": venue_name, "venue_fullname": venue_fullname,
                "venue_address": venue_address, "venue_city": venue_city,
                "venue_waze_query": venue_waze_query, "venue_gmaps_query": venue_gmaps_query,
                "waze_link": waze_link, "gmap_link": gmap_link,
                "contact1_name": contact1_name, "contact1_phone_display": contact1_phone,
                "contact1_phone_wa": contact1_wa, "contact2_name": contact2_name,
                "contact2_phone_display": contact2_phone, "contact2_phone_wa": contact2_wa,
                "music_url": music_url, "music_label": music_label,
                "love_year_1": love_year_1, "love_story_1": love_story_1,
                "love_year_2": love_year_2, "love_story_2": love_story_2,
                "love_year_3": love_year_3, "love_story_3": love_story_3,
                "love_year_4": love_year_4,
                "dresscode_theme": dresscode_theme, "dresscode_theme_en": dresscode_theme_en,
                "dresscode_note": dresscode_note,
                "color1_hex": color1_hex, "color1_name": color1_name,
                "color2_hex": color2_hex, "color2_name": color2_name,
                "color3_hex": color3_hex, "color3_name": color3_name,
                "color4_hex": color4_hex, "color4_name": color4_name,
                "color5_hex": color5_hex, "color5_name": color5_name,
                "doa_sample1_name": doa1_name, "doa_sample1_msg": doa1_msg,
                "doa_sample2_name": doa2_name, "doa_sample2_msg": doa2_msg,
                "qr_code_url": qr_code_url, "hero_url": hero_url,
                "photo1_url": photo1_url, "photo2_url": photo2_url,
                "photo3_url": photo3_url, "opening_url": opening_url,
                "video_url": video_url, "gallery1_url": g1, "gallery2_url": g2,
                "gallery3_url": g3, "gallery4_url": g4, "gallery5_url": g5,
            }

            replacements = build_replacements(data)
            final_html   = apply_replacements(template_html, replacements)
            filename     = f"kad-{sanitize_filename(groom_name)}-{sanitize_filename(bride_name)}-{order_id.lower()}.html"

            # Fix monogram
            if "function initMonogram()" in final_html and groom_name and bride_name:
                gi = groom_name.strip()[0].upper()
                bi = bride_name.strip()[0].upper()
                final_html = re.sub(
                    r'function initMonogram\(\)\{[^}]*\}',
                    f"function initMonogram(){{const el=document.getElementById('sealInitials');if(el)el.textContent='{gi}&{bi}';}}",
                    final_html
                )

            if "Deploy" in deploy_mode and github_ready:
                with st.spinner("🚀 Deploying..."):
                    result = github_upload_file(gh_token, gh_repo, f"cards/{filename}", final_html,
                        f"Add kad: {groom_name} & {bride_name} [{order_id}]")
                if result["success"]:
                    _entry = {
                        "order_id": order_id, "kad_id": kad_id,
                        "groom": groom_name, "bride": bride_name,
                        "date": date_display, "template": sel["name"],
                        "filename": f"cards/{filename}", "url": result["pages_url"],
                        "created_at": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    }
                    add_to_history(gh_token, gh_repo, _entry)
                    st.cache_data.clear()
                    st.markdown(f"""
                    <div class='success-box'>
                        <h3 style='color:#4CAF50;margin:0 0 .5rem'>✅ Deployed!</h3>
                        <span class='order-id'>{order_id}</span>
                        <span style='font-family:monospace;background:#1a1a1a;padding:4px 10px;border-radius:6px;color:#80c0ff;font-size:0.8rem;margin-left:0.5rem'>KAD_ID: {kad_id}</span><br><br>
                        <b>{groom_name} & {bride_name}</b> · {date_display}<br>
                        <small style='color:#666'>Data RSVP & Doa akan tersimpan dalam Firebase path: <code>kads/{kad_id}/</code></small>
                    </div>""", unsafe_allow_html=True)
                    st.markdown(f"<div class='link-box'><b style='color:#C9A96E'>🔗 Link Kad</b><br><a href='{result['pages_url']}' target='_blank' style='color:#4ade80;font-weight:600'>{result['pages_url']}</a><br><small style='color:#666'>⚠️ Ambik 1-2 minit pertama kali</small></div>", unsafe_allow_html=True)
                    st.code(result["pages_url"], language=None)
                else:
                    st.error(f"❌ {result['error']}")
            else:
                st.markdown(f"<div class='success-box'><h3 style='color:#4CAF50;margin:0 0 .5rem'>✅ Kad Siap!</h3><span class='order-id'>{order_id}</span></div>", unsafe_allow_html=True)

            st.download_button("⬇️ Download HTML", data=final_html.encode("utf-8"), file_name=filename, mime="text/html", use_container_width=True)

# ─────────────────────────────────────────
#  PAGE: HISTORY
# ─────────────────────────────────────────
elif "📜 History" in page:
    st.markdown("# 📜 History Kad Deployed")
    gh_token = st.session_state.get("gh_token", "") or st.secrets.get("GH_TOKEN", "")
    gh_repo  = st.session_state.get("gh_repo",  "") or st.secrets.get("GH_REPO",  "")
    if not gh_token or not gh_repo:
        st.warning("⚠️ Setup GitHub dulu di ⚙️ GitHub Settings")
    else:
        if st.button("🔄 Refresh"): st.cache_data.clear(); st.rerun()
        history = load_history(gh_token, gh_repo)
        if not history:
            st.info("Belum ada kad yang di-deploy.")
        else:
            st.markdown(f"<div class='info-box'>📊 Jumlah kad: <b>{len(history)}</b></div>", unsafe_allow_html=True)
            for i, entry in enumerate(history):
                col_info, col_link, col_del = st.columns([3, 2, 1])
                with col_info:
                    kad_id_display = entry.get('kad_id', entry.get('order_id','').lower())
                    st.markdown(f"""
                    <div class='template-card'>
                        <span class='order-id'>{entry.get('order_id','—')}</span>
                        <span style='font-size:0.65rem;color:#666;margin-left:0.5rem'>{entry.get('created_at','')}</span><br>
                        <b style='color:#f0e8d8'>{entry.get('groom','?')} & {entry.get('bride','?')}</b><br>
                        <small style='color:#888'>📅 {entry.get('date','')} · 🎨 {entry.get('template','')}</small><br>
                        <small style='color:#555;font-family:monospace'>Firebase: kads/{kad_id_display}/</small>
                    </div>""", unsafe_allow_html=True)
                with col_link:
                    url = entry.get("url", "")
                    if url:
                        st.markdown(f"<div style='padding-top:1.1rem'><a href='{url}' target='_blank' style='font-size:0.68rem;color:#4ade80'>🔗 Buka Kad</a></div>", unsafe_allow_html=True)
                with col_del:
                    if st.button("🗑️", key=f"hdel_{i}"):
                        st.session_state[f"confirm_hdel_{i}"] = True
                if st.session_state.get(f"confirm_hdel_{i}"):
                    fname = entry.get("filename","")
                    cc1, cc2, _ = st.columns([1,1,4])
                    with cc1:
                        if st.button("✅ Ya", key=f"hyes_{i}"):
                            ok, err = delete_github_file(gh_token, gh_repo, fname)
                            if ok:
                                new_hist = [h for h in history if h.get("order_id") != entry.get("order_id")]
                                save_history(gh_token, gh_repo, new_hist)
                                st.cache_data.clear()
                                del st.session_state[f"confirm_hdel_{i}"]
                                st.success("✅ Dipadam."); st.rerun()
                            else:
                                st.error(f"❌ {err}")
                    with cc2:
                        if st.button("❌ Batal", key=f"hno_{i}"):
                            del st.session_state[f"confirm_hdel_{i}"]
                            st.rerun()

# ─────────────────────────────────────────
#  PAGE: TEMPLATE CONVERTER (unchanged from original)
# ─────────────────────────────────────────
elif "🔧 Template Converter" in page:
    st.markdown("# 🔧 Template Converter")
    st.markdown("Upload HTML → map nilai → convert jadi template dengan placeholders → upload ke GitHub.")
    st.markdown("---")
    uploaded = st.file_uploader("Upload fail HTML", type=["html","htm"])
    if uploaded:
        raw_html = uploaded.read().decode("utf-8")
        fmt = detect_format(raw_html)
        st.success(f"✅ {len(raw_html):,} chars — Format: {'{{CURLY}}' if fmt=='curly' else '[Square]'}")
        found_phs = sorted(set(re.findall(r'\{\{[A-Z_]+\}\}', raw_html) if fmt=='curly' else [p for p in re.findall(r'\[[A-Za-z][^\]]{2,60}\]', raw_html) if not any(c in p for c in ['(',')','{','}','.','=','0','1','2','3','4','5','6','7','8','9'])]))
        if found_phs:
            tags = " ".join(f"<span class='ph-tag'>{p}</span>" for p in found_phs)
            st.markdown(tags, unsafe_allow_html=True)
        st.markdown("---")
        mode = st.radio("Jenis:", ["✅ Dah ada placeholders — terus upload", "🔧 Masih hardcoded"], horizontal=True)
        ready = False
        valid = []
        if mode.startswith("✅"):
            ready = True
        else:
            all_phs = ["{{GROOM_NAME}}","{{BRIDE_NAME}}","{{DATE_DISPLAY}}","{{DATE_DAY}}","{{DATE_HIJRI}}","{{DATE_DD}}","{{DATE_MM}}","{{DATE_YYYY}}","{{DATE_YYYYMMDD}}","{{TIME_START}}","{{TIME_END}}","{{TIME_START_HHMM}}","{{TIME_END_HHMM}}","{{TIME_ARRIVAL}}","{{TIME_AKAD}}","{{TIME_BERSANDING}}","{{TIME_MAKAN}}","{{TIME_BERSURAI}}","{{VENUE_NAME}}","{{VENUE_FULLNAME}}","{{VENUE_ADDRESS}}","{{VENUE_CITY}}","{{VENUE_WAZE_QUERY}}","{{VENUE_GMAPS_QUERY}}","{{CONTACT1_NAME}}","{{CONTACT1_PHONE_WA}}","{{CONTACT2_NAME}}","{{CONTACT2_PHONE_WA}}","{{MUSIC_URL}}","{{LOVE_YEAR_1}}","{{LOVE_STORY_1}}","{{LOVE_YEAR_2}}","{{LOVE_STORY_2}}","{{LOVE_YEAR_3}}","{{LOVE_STORY_3}}","{{DRESSCODE_THEME}}","{{DRESSCODE_NOTE}}","{{COLOR1_HEX}}","{{COLOR1_NAME}}","{{COLOR2_HEX}}","{{COLOR2_NAME}}","{{COLOR3_HEX}}","{{COLOR3_NAME}}","{{COLOR4_HEX}}","{{COLOR4_NAME}}","{{COLOR5_HEX}}","{{COLOR5_NAME}}","{{QR_CODE_URL}}","{{PHOTO1_URL}}","{{PHOTO2_URL}}","{{GROOM_FATHER}}","{{GROOM_MOTHER}}","{{BRIDE_FATHER}}","{{BRIDE_MOTHER}}","{{HOST_FAMILY}}","{{HOST_MESSAGE_BM}}"]
            if "converter_rows" not in st.session_state:
                st.session_state.converter_rows = [{"value":"","placeholder":""}]
            c1,c2,_ = st.columns([1,1,4])
            with c1:
                if st.button("➕"): st.session_state.converter_rows.append({"value":"","placeholder":""}); st.rerun()
            with c2:
                if st.button("➖") and len(st.session_state.converter_rows)>1: st.session_state.converter_rows.pop(); st.rerun()
            ph_options = {"-- Pilih --":""} | {ph:ph for ph in all_phs}
            for i, row in enumerate(st.session_state.converter_rows):
                c1,c2,c3 = st.columns([2,3,1])
                with c1: val = st.text_input(f"val{i}", value=row["value"], key=f"cv_{i}", label_visibility="collapsed"); st.session_state.converter_rows[i]["value"]=val
                with c2: sp = st.selectbox(f"ph{i}", list(ph_options.keys()), key=f"cp_{i}", label_visibility="collapsed"); st.session_state.converter_rows[i]["placeholder"]=ph_options[sp]
                with c3:
                    if val:
                        n = raw_html.count(val)
                        st.markdown(f"<div style='color:{'#4CAF50' if n>0 else '#ff6b6b'};padding-top:8px'>{'✅ '+str(n)+'x' if n>0 else '❌'}</div>", unsafe_allow_html=True)
            valid = [r for r in st.session_state.converter_rows if r["value"] and r["placeholder"] and r["value"] in raw_html]
            if valid: ready=True; st.success(f"✅ {len(valid)} replacement")
        st.markdown("---")
        c1,c2 = st.columns(2)
        with c1: t_cat=st.selectbox("Category",["Essential","Portrait","Light","Cinematic","Prestige"]); t_name=st.text_input("Nama Template"); t_emoji=st.text_input("Emoji",max_chars=2)
        with c2: t_desc=st.text_input("Penerangan"); t_file=st.text_input("Nama Fail (tanpa .html)")
        gh_token2 = st.session_state.get("gh_token","") or st.secrets.get("GH_TOKEN","")
        gh_repo2  = st.session_state.get("gh_repo", "") or st.secrets.get("GH_REPO", "")
        can = bool(ready and t_name and t_file and gh_token2 and gh_repo2)
        if st.button("🚀 Upload Template!", disabled=not can):
            converted = raw_html
            for m in sorted(valid, key=lambda x: len(x["value"]), reverse=True):
                converted = converted.replace(m["value"], m["placeholder"])
            final_fn = f"{re.sub(r'[^a-z0-9_]','_',t_file.lower().strip())}.html"
            res = github_upload_file(gh_token2, gh_repo2, f"templates/{final_fn}", converted, f"Add template: {t_name}")
            if res["success"]:
                new_entry = {"name":t_name,"file":final_fn,"has_photo":t_cat in ["Portrait","Cinematic","Prestige"],"has_portrait_photo":"{{PHOTO1_URL}}" in converted and "{{PHOTO2_URL}}" in converted,"preview_emoji":t_emoji or "✨","desc":t_desc}
                registry = load_registry(gh_token2, gh_repo2)
                if t_cat not in registry: registry[t_cat]={}
                registry[t_cat][t_file] = new_entry
                save_registry(gh_token2, gh_repo2, registry)
                st.cache_data.clear()
                st.success(f"✅ Template `{t_name}` berjaya ditambah!")
                st.session_state.converter_rows = [{"value":"","placeholder":""}]
            else:
                st.error(f"❌ {res['error']}")

    # ── PREVIEW IMAGE UPLOAD (standalone — boleh guna lepas template dah upload) ──
    st.markdown("---")
    st.markdown("### 🖼️ Upload / Kemaskini Preview Image")
    st.markdown("<div class='info-box'>Upload screenshot template sebagai gambar preview dalam katalog website utama. Pastikan nama fail sama dengan nama template yang dah upload.</div>", unsafe_allow_html=True)

    col_prev1, col_prev2 = st.columns(2)
    with col_prev1:
        # Pilih template dari registry untuk update preview
        gh_token3 = st.session_state.get("gh_token","") or st.secrets.get("GH_TOKEN","")
        gh_repo3  = st.session_state.get("gh_repo", "") or st.secrets.get("GH_REPO", "")
        registry_for_prev = load_registry(gh_token3, gh_repo3)
        
        # Flatten registry jadi senarai pilihan
        tmpl_choices = {}
        for _cat, _tmpls in registry_for_prev.items():
            for _key, _info in _tmpls.items():
                label = f"{_info.get('preview_emoji','✨')} [{_cat}] {_info['name']}"
                tmpl_choices[label] = (_cat, _key, _info)
        
        if tmpl_choices:
            selected_prev_label = st.selectbox("Pilih Template", list(tmpl_choices.keys()), key="prev_tmpl_sel")
            sel_cat, sel_key, sel_info = tmpl_choices[selected_prev_label]
            
            # Tunjuk status preview sekarang
            curr_prev = sel_info.get('preview_img', '')
            if curr_prev:
                st.markdown(f"<div class='info-box'>✅ Preview sedia ada: <code>{curr_prev}</code></div>", unsafe_allow_html=True)
            else:
                st.markdown("<div class='warning-box'>⚠️ Belum ada preview image untuk template ini.</div>", unsafe_allow_html=True)
        else:
            st.info("Tiada template dalam registry.")
            selected_prev_label = None

    with col_prev2:
        prev_file = st.file_uploader("Upload Screenshot (JPG/PNG, nisbah 3:4 portrait)", type=["jpg","jpeg","png","webp"], key="preview_uploader")
        if prev_file:
            st.image(prev_file, caption="Preview", use_column_width=True)

    if prev_file and selected_prev_label and tmpl_choices and gh_token3 and gh_repo3:
        # Auto-generate nama fail berdasarkan template key
        _cat_sel, _key_sel, _info_sel = tmpl_choices[selected_prev_label]
        base_name = re.sub(r'[^a-z0-9_]', '_', _key_sel.lower().strip())
        ext = prev_file.name.rsplit('.', 1)[-1].lower()
        if ext == 'jpeg': ext = 'jpg'
        preview_filename = f"previews/{base_name}.{ext}"
        
        st.markdown(f"<div class='info-box'>📁 Akan disimpan sebagai: <code>{preview_filename}</code></div>", unsafe_allow_html=True)
        
        if st.button("📤 Upload Preview Image", key="btn_upload_preview"):
            prev_bytes = prev_file.getvalue()
            prev_b64   = base64.b64encode(prev_bytes).decode()
            api_url    = f"https://api.github.com/repos/{gh_repo3}/contents/{preview_filename}"
            headers    = {"Authorization": f"token {gh_token3}", "Accept": "application/vnd.github.v3+json"}
            
            with st.spinner("Uploading..."):
                # Check SHA kalau dah ada
                r_check = requests.get(api_url, headers=headers, timeout=10)
                payload = {"message": f"Add preview: {_info_sel['name']}", "content": prev_b64}
                if r_check.status_code == 200:
                    payload["sha"] = r_check.json().get("sha")
                    payload["message"] = f"Update preview: {_info_sel['name']}"
                
                r_up = requests.put(api_url, headers=headers, json=payload, timeout=30)
            
            if r_up.status_code in (200, 201):
                # Update registry dengan preview_img field
                registry_upd = load_registry(gh_token3, gh_repo3)
                if _cat_sel in registry_upd and _key_sel in registry_upd[_cat_sel]:
                    registry_upd[_cat_sel][_key_sel]["preview_img"] = preview_filename
                    if save_registry(gh_token3, gh_repo3, registry_upd):
                        st.cache_data.clear()
                        st.success(f"✅ Preview uploaded & registry dikemaskini! → `{preview_filename}`")
                        st.markdown(f"<div class='info-box'>🌐 Preview URL: <code>https://nureqmal.github.io/eqstudio-cards/{preview_filename}</code><br><small style='color:#666'>⚠️ GitHub Pages ambik 1-2 minit untuk update</small></div>", unsafe_allow_html=True)
                    else:
                        st.warning("⚠️ Gambar uploaded tapi registry gagal dikemaskini.")
                else:
                    st.warning("⚠️ Template tidak jumpa dalam registry.")
            else:
                try: err_msg = r_up.json().get("message", r_up.text)
                except: err_msg = r_up.text
                st.error(f"❌ Upload gagal: {err_msg}")

# ─────────────────────────────────────────
#  PAGE: CARA GUNA
# ─────────────────────────────────────────
elif "📋 Cara Guna" in page:
    st.markdown("# 📋 Cara Guna")
    st.markdown("""
    ## Flow Lengkap
    1. **⚙️ GitHub Settings** — setup token + repo sekali je
    2. **🔧 Template Converter** — upload template HTML kau, akan auto-upload ke GitHub
    3. **🆕 Jana Kad Baru** — isi maklumat client, generate & deploy
    4. **📊 RSVP & Doa** — tengok data realtime dari Firebase
    5. **📜 History** — semua kad yang dah deploy, ada link terus

    ## KAD_ID System
    Setiap kad yang di-generate dapat **KAD_ID unik** berdasarkan order ID.
    Contoh: Order `EQ260603143022` → KAD_ID `eq260603143022`

    Data Firebase disimpan dalam path: `kads/eq260603143022/rsvp`, `kads/eq260603143022/doa`

    Ini bermakna **setiap kad ada data tersendiri** — tak campur antara client.

    ## Template Files
    Templates kena ada dalam `templates/` folder dalam GitHub repo kau.
    Upload menggunakan 🔧 Template Converter atau terus commit ke GitHub.
    """)

# ─────────────────────────────────────────
#  PAGE: TEMPLATE INFO
# ─────────────────────────────────────────
elif "🗂️ Template Info" in page:
    st.markdown("# 🗂️ Senarai Template")
    gh_token = st.session_state.get("gh_token", "") or st.secrets.get("GH_TOKEN", "")
    gh_repo  = st.session_state.get("gh_repo",  "") or st.secrets.get("GH_REPO",  "")
    TEMPLATES = load_registry(gh_token, gh_repo)
    if st.button("🔄 Refresh"): st.cache_data.clear(); st.rerun()
    st.markdown("---")
    for category, templates in TEMPLATES.items():
        emoji = "⭐" if category=="Essential" else "📸" if category=="Portrait" else "☀️" if category=="Light" else "🎬" if category=="Cinematic" else "💎"
        st.markdown(f"## {emoji} {category}")
        for key, info in templates.items():
            tmpl_html = load_template(info["file"], gh_token, gh_repo)
            status = "✅ Ada" if tmpl_html else "❌ Fail tidak jumpa"
            col_info, col_del = st.columns([5,1])
            with col_info:
                st.markdown(f"<div class='template-card'><b>{info.get('preview_emoji','✨')} {info['name']}</b><br><small style='color:#888'>{info.get('desc','')}</small><br><small>📁 <code>{info['file']}</code> — {status}</small></div>", unsafe_allow_html=True)
            with col_del:
                if st.button("🗑️", key=f"del_{key}"):
                    st.session_state[f"confirm_del_{key}"] = True
            if st.session_state.get(f"confirm_del_{key}"):
                c1,c2,_ = st.columns([1,1,4])
                with c1:
                    if st.button("✅ Ya", key=f"yes_{key}"):
                        registry = load_registry(gh_token, gh_repo)
                        if category in registry and key in registry[category]:
                            del registry[category][key]
                            save_registry(gh_token, gh_repo, registry)
                            st.cache_data.clear()
                            del st.session_state[f"confirm_del_{key}"]
                            st.success("✅ Dipadam."); st.rerun()
                with c2:
                    if st.button("❌ Batal", key=f"no_{key}"):
                        del st.session_state[f"confirm_del_{key}"]
                        st.rerun()
