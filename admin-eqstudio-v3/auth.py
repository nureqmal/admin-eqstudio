# auth.py
import streamlit as st
from datetime import datetime, timedelta
import requests

# ─────────────────────────────────────────
#  CONFIG
# ─────────────────────────────────────────
SESSION_TIMEOUT_MINUTES = 30
FIREBASE_DB_URL = "https://eqstudio-6225d-default-rtdb.asia-southeast1.firebasedatabase.app"

# ─────────────────────────────────────────
#  FIREBASE ACTIVITY LOG
# ─────────────────────────────────────────
def log_activity(username, role, action, detail=""):
    """Log activity ke Firebase."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        entry = {
            "username": username,
            "role": role,
            "action": action,
            "detail": detail,
            "timestamp": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
            "unix": int(datetime.now().timestamp() * 1000),
        }
        url = f"{FIREBASE_DB_URL}/activity_log/{timestamp}_{username}.json"
        requests.put(url, json=entry, timeout=5)
    except Exception:
        pass  # Jangan crash app kalau Firebase fail


def get_activity_log(limit=50, username_filter=None):
    """Ambil activity log dari Firebase."""
    try:
        url = f"{FIREBASE_DB_URL}/activity_log.json?orderBy=\"unix\"&limitToLast={limit}"
        r = requests.get(url, timeout=8)
        if r.status_code == 200 and r.json():
            logs = list(r.json().values())
            logs.sort(key=lambda x: x.get("unix", 0), reverse=True)
            if username_filter:
                logs = [l for l in logs if l.get("username") == username_filter]
            return logs
    except Exception:
        pass
    return []


# ─────────────────────────────────────────
#  AUTH CORE
# ─────────────────────────────────────────
def get_users():
    """Ambil users dari st.secrets."""
    users = {}
    try:
        for username, info in st.secrets.get("users", {}).items():
            users[username] = {
                "password": info["password"],
                "role": info["role"],
            }
    except Exception:
        pass
    return users


def verify_login(username, password):
    """Verify credentials. Return role kalau betul, None kalau salah."""
    users = get_users()
    user = users.get(username.strip().lower())
    if user and user["password"] == password:
        return user["role"]
    return None


def check_session_timeout():
    """Check sama ada session dah expired. Return True kalau masih valid."""
    last_active = st.session_state.get("last_active")
    if not last_active:
        return False
    elapsed = datetime.now() - last_active
    if elapsed > timedelta(minutes=SESSION_TIMEOUT_MINUTES):
        return False
    return True


def refresh_session():
    """Update last active timestamp."""
    st.session_state["last_active"] = datetime.now()


def logout():
    """Clear session dan log activity."""
    username = st.session_state.get("username", "")
    role = st.session_state.get("role", "")
    if username:
        log_activity(username, role, "LOGOUT", "User logout")
    for key in ["logged_in", "username", "role", "last_active"]:
        st.session_state.pop(key, None)


def is_logged_in():
    """Check sama ada user logged in dan session masih valid."""
    if not st.session_state.get("logged_in"):
        return False
    if not check_session_timeout():
        username = st.session_state.get("username", "")
        role = st.session_state.get("role", "")
        if username:
            log_activity(username, role, "AUTO_LOGOUT", "Session expired after 30 minit")
        for key in ["logged_in", "username", "role", "last_active"]:
            st.session_state.pop(key, None)
        return False
    refresh_session()
    return True


def get_current_user():
    """Return (username, role) untuk user yang sedang login."""
    return st.session_state.get("username", ""), st.session_state.get("role", "")


def is_admin():
    return st.session_state.get("role") == "admin"


def is_staff():
    return st.session_state.get("role") == "staff"


# ─────────────────────────────────────────
#  LOGIN PAGE UI
# ─────────────────────────────────────────
def show_login_page():
    """Render login page."""
    st.markdown("""
    <style>
        .main { background: #0f0f0f; }
        .stApp { background: #111; }
        .login-logo {
            text-align: center; margin-bottom: 1.5rem;
        }
        .login-logo h1 {
            color: #C9A96E !important; font-size: 1.8rem; margin: 0;
        }
        .login-logo p {
            color: #555; font-size: 0.8rem; margin: 0.3rem 0 0;
        }
        .stTextInput > div > div > input {
            background: #242424 !important; color: #f0e8d8 !important;
            border: 1px solid #333 !important; border-radius: 8px !important;
        }
        .stButton > button {
            background: linear-gradient(135deg, #C9A96E, #8B6B2E);
            color: white; border: none; border-radius: 8px;
            font-weight: 600; padding: 0.6rem 1.5rem; width: 100%;
        }
        .stButton > button:hover { opacity: 0.9; }
    </style>
    """, unsafe_allow_html=True)

    col_l, col_mid, col_r = st.columns([1, 2, 1])
    with col_mid:
        st.markdown("""
        <div class='login-logo'>
            <h1>💍 EQStudio</h1>
            <p>Kad Kahwin Digital — Admin Panel</p>
        </div>
        """, unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="username", key="login_username")
        password = st.text_input("Password", type="password", placeholder="••••••••", key="login_password")

        if st.button("🔐 Log Masuk", use_container_width=True):
            if not username or not password:
                st.error("Sila masukkan username dan password.")
            else:
                role = verify_login(username, password)
                if role:
                    st.session_state["logged_in"]   = True
                    st.session_state["username"]     = username.strip().lower()
                    st.session_state["role"]         = role
                    st.session_state["last_active"]  = datetime.now()
                    log_activity(
                        username.strip().lower(), role,
                        "LOGIN", f"Login berjaya — role: {role}"
                    )
                    st.rerun()
                else:
                    st.error("❌ Username atau password salah.")

    return False


# ─────────────────────────────────────────
#  ACTIVITY LOG UI
# ─────────────────────────────────────────
def show_activity_log(username_filter=None, limit=50):
    """Render activity log. Admin nampak semua, staff nampak log sendiri."""
    logs = get_activity_log(limit=limit, username_filter=username_filter)

    ACTION_ICON = {
        "LOGIN":         "🟢",
        "LOGOUT":        "🔴",
        "AUTO_LOGOUT":   "🟡",
        "GENERATE_KAD":  "✨",
        "EDIT_KAD":      "✏️",
        "DELETE_KAD":    "🗑️",
        "COPY_LINK":     "📋",
    }

    if not logs:
        st.info("Tiada activity log lagi.")
        return

    for log in logs:
        icon = ACTION_ICON.get(log.get("action", ""), "•")
        user_badge = (
            f"<span style='background:#2a1f0f;border:1px solid #C9A96E44;"
            f"border-radius:12px;padding:1px 8px;font-size:0.7rem;color:#C9A96E'>"
            f"{log.get('username','')}</span>"
        )
        if log.get("role") == "admin":
            role_badge = (
                "<span style='background:#1a1a2e;border:1px solid #4444aa44;"
                "border-radius:12px;padding:1px 8px;font-size:0.65rem;color:#8888cc;margin-left:4px'>admin</span>"
            )
        else:
            role_badge = (
                "<span style='background:#1a2a1a;border:1px solid #44aa4444;"
                "border-radius:12px;padding:1px 8px;font-size:0.65rem;color:#88cc88;margin-left:4px'>staff</span>"
            )

        detail_html = (
            f"<span style='color:#666;font-size:0.75rem'> — {log.get('detail','')}</span>"
            if log.get('detail') else ""
        )

        st.markdown(
            f"<div style='display:flex;align-items:center;padding:0.45rem 0;"
            f"border-bottom:1px solid #1e1e1e;gap:8px'>"
            f"<span style='font-size:1rem'>{icon}</span>"
            f"<span style='flex:1;color:#e0d8d0;font-size:0.82rem'>"
            f"<b>{log.get('action','')}</b>{detail_html}</span>"
            f"{user_badge}{role_badge}"
            f"<span style='font-size:0.65rem;color:#444;min-width:120px;text-align:right'>"
            f"{log.get('timestamp','')}</span>"
            f"</div>",
            unsafe_allow_html=True
        )
