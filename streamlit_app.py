import streamlit as st
import hashlib
import json
from pathlib import Path
from functools import wraps

# ------------------------------------------------------------
# 0) HELPERS: bezpieczne przeładowanie + hashowanie hasła
# ------------------------------------------------------------
def safe_rerun():
    """
    Najpierw próbujemy st.experimental_rerun().
    Jeśli go nie ma, rzucamy wewnętrzny RerunException.
    """
    try:
        st.experimental_rerun()
    except AttributeError:
        from streamlit.runtime.scriptrunner import get_script_run_ctx
        from streamlit.runtime.scriptrunner.script_runner import RerunException

        ctx = get_script_run_ctx()
        if ctx is None:
            st.error("Brak kontekstu Streamlita – nie można przeladować.")
        else:
            raise RerunException(ctx)


def hash_pw(pw: str) -> str:
    return hashlib.sha256(pw.encode("utf-8")).hexdigest()


# ------------------------------------------------------------
# 1) PLIK JSON Z UŻYTKOWNIKAMI I ICH ROLAMI
# ------------------------------------------------------------
DB_PATH = Path("users.json")


def load_users() -> dict:
    if DB_PATH.exists():
        return json.loads(DB_PATH.read_text())
    # jeśli brak pliku – zakładamy bootstrap admin/admin
    default = {
        "admin": {
            "password": hash_pw("admin"),
            "role": "admin"
        }
    }
    DB_PATH.write_text(json.dumps(default, indent=2))
    return default


def save_users(u: dict):
    DB_PATH.write_text(json.dumps(u, indent=2))


def authenticate(username: str, pw: str) -> bool:
    users = load_users()
    return username in users and users[username]["password"] == hash_pw(pw)


def get_role(username: str) -> str:
    return load_users().get(username, {}).get("role", "")


def register(username: str, pw: str, role: str = "user") -> bool:
    users = load_users()
    if username in users:
        return False
    users[username] = {"password": hash_pw(pw), "role": role}
    save_users(users)
    return True


def set_role(username: str, new_role: str):
    users = load_users()
    if username in users:
        users[username]["role"] = new_role
        save_users(users)


# ------------------------------------------------------------
# 2) SESJA
# ------------------------------------------------------------
if "auth" not in st.session_state:
    st.session_state.auth = False
    st.session_state.user = ""
    st.session_state.role = ""


# ------------------------------------------------------------
# 3) DEKORATOR @requires_role
# ------------------------------------------------------------
def requires_role(*allowed_roles):
    def dec(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            if not st.session_state.auth:
                st.warning("Musisz się zalogować.")
                return
            if st.session_state.role not in allowed_roles:
                st.error(f"Brak uprawnień. Wymagana rola: {allowed_roles}")
                return
            return f(*args, **kwargs)
        return wrapper
    return dec


# ------------------------------------------------------------
# 4) FORMULARZE
# ------------------------------------------------------------
def login_form():
    st.title("🔐 Logowanie")
    u = st.text_input("Login")
    p = st.text_input("Hasło", type="password")
    if st.button("Zaloguj"):
        if authenticate(u, p):
            st.session_state.auth = True
            st.session_state.user = u
            st.session_state.role = get_role(u)
            safe_rerun()
        else:
            st.error("Niepoprawny login lub hasło")


def signup_form():
    st.title("🆕 Rejestracja")
    u = st.text_input("Nowy login", key="su1")
    p = st.text_input("Nowe hasło", type="password", key="su2")
    # Tylko admin może nadawać rolę przy rejestracji
    role = "user"
    if st.session_state.auth and st.session_state.role == "admin":
        role = st.selectbox("Rola nowego użytkownika", ["user", "admin"])
    if st.button("Zarejestruj"):
        if register(u, p, role):
            st.success(f"Utworzono konto [{u}] z rolą [{role}].")
        else:
            st.error("Login już istnieje.")


# ------------------------------------------------------------
# 5) STRONY DLA RÓŻNYCH RÓL
# ------------------------------------------------------------
@requires_role("user", "admin")
def user_page():
    st.header("📋 Panel zwykłego użytkownika")
    st.write("Treść dostępna dla zalogowanych userów.")


@requires_role("admin")
def admin_panel():
    st.header("🛠️ Panel administratora")
    users = load_users()
    df = {
        "Login": list(users.keys()),
        "Rola": [users[u]["role"] for u in users]
    }
    st.table(df)

    st.subheader("Zmień rolę użytkownika")
    sel = st.selectbox("Wybierz użytkownika", list(users.keys()))
    newr = st.selectbox("Nowa rola", ["user", "admin"], index=0)
    if st.button("Zapisz rolę"):
        if sel == st.session_state.user:
            st.error("Nie możesz zmienić własnej roli.")
        else:
            set_role(sel, newr)
            st.success(f"Rola `{sel}` → `{newr}`")
            safe_rerun()


@requires_role("admin")
def secret_admin_page():
    st.header("🔒 Sekretna strona tylko dla adminów")
    st.write("Tylko ADMIN widzi tę zawartość.")


# ------------------------------------------------------------
# 6) GŁÓWNY PRZEBIEG APLIKACJI
# ------------------------------------------------------------
st.sidebar.title("Nawigacja")

if not st.session_state.auth:
    choice = st.sidebar.radio("Wybierz akcję", ["Logowanie", "Rejestracja"])
    if choice == "Logowanie":
        login_form()
    else:
        signup_form()
    st.stop()

# — po zalogowaniu —
st.sidebar.markdown(f"**Zalogowany:** `{st.session_state.user}`\n**Rola:** `{st.session_state.role}`")
if st.sidebar.button("Wyloguj"):
    st.session_state.auth = False
    st.session_state.user = ""
    st.session_state.role = ""
    safe_rerun()

page = st.sidebar.selectbox("Strona", ["User Page", "Admin Panel", "Admin Secret"])
if page == "User Page":
    user_page()
elif page == "Admin Panel":
    admin_panel()
else:
    secret_admin_page()
