import os
import requests
import streamlit as st

API_BASE = os.environ.get("API_BASE", "http://127.0.0.1:8000")

st.set_page_config(page_title="Chat Platform UI", layout="wide")
st.title("Chat Platform")

# --- Session state ---
if "token" not in st.session_state:
    st.session_state.token = None
if "projects" not in st.session_state:
    st.session_state.projects = []
if "project_id" not in st.session_state:
    st.session_state.project_id = None
if "chat" not in st.session_state:
    st.session_state.chat = {}  # {project_id: [(role, content), ...]}

def api(method, path, **kwargs):
    headers = kwargs.pop("headers", {})
    if st.session_state.token:
        headers["Authorization"] = f"Bearer {st.session_state.token}"
    url = f"{API_BASE}{path}"
    r = requests.request(method, url, headers=headers, **kwargs, timeout=60)
    if r.status_code >= 400:
        try:
            detail = r.json()
        except Exception:
            detail = r.text
        raise RuntimeError(f"HTTP {r.status_code} at {path}: {detail}")
    if "application/json" in r.headers.get("Content-Type", ""):
        return r.json()
    return r.text

# --- Sidebar: Auth ---
st.sidebar.header("Auth")
auth_mode = st.sidebar.radio("Choose", ["Login", "Register"], horizontal=True)
email = st.sidebar.text_input("Email")
password = st.sidebar.text_input("Password", type="password")
colA, colB = st.sidebar.columns(2)

if colA.button(auth_mode):
    try:
        body = {"email": email, "password": password}
        if auth_mode == "Register":
            api("POST", "/auth/register", json=body)
        data = api("POST", "/auth/login", json=body)
        st.session_state.token = data["access_token"]
        st.sidebar.success("Authenticated")
        st.rerun()
    except Exception as e:
        st.sidebar.error(str(e))

if colB.button("Logout"):
    st.session_state.token = None
    st.session_state.project_id = None
    st.session_state.projects = []
    st.session_state.chat = {}
    st.rerun()

if not st.session_state.token:
    st.info("Login or register to continue.")
    st.stop()

# --- Projects panel ---
st.subheader("Projects")

pc1, pc2 = st.columns([2, 1])

with pc1:
    # refresh list
    try:
        st.session_state.projects = api("GET", "/projects")
    except Exception as e:
        st.error(str(e))
    names = [f"{p['name']} ({p['provider']})" for p in st.session_state.projects]
    ids = [p["id"] for p in st.session_state.projects]
    if ids:
        idx = 0
        if st.session_state.project_id in ids:
            idx = ids.index(st.session_state.project_id)
        chosen = st.selectbox("Select a project", options=list(range(len(ids))), format_func=lambda i: names[i], index=idx)
        st.session_state.project_id = ids[chosen]
    else:
        st.write("No projects yet.")

with pc2:
    st.markdown("**Create project**")
    new_name = st.text_input("Name", value="My Agent")
    provider = st.selectbox("Provider", ["openai", "openrouter", "groq", "mock"])
    model = st.text_input("Model (optional)", placeholder="gpt-4o-mini or llama-3.3-70b-versatile ...")

    if st.button("Create"):
        try:
            body = {"name": new_name, "provider": provider}
            if model.strip():
                body["model"] = model.strip()
            p = api("POST", "/projects", json=body)
            st.success(f"Created: {p['name']}")
            st.session_state.project_id = p["id"]
            st.rerun()
        except Exception as e:
            st.error(str(e))

if not st.session_state.project_id:
    st.stop()

# --- Prompts + Files + Chat ---
left, right = st.columns([1, 2])

with left:
    st.markdown("### Prompts")
    try:
        prompts = api("GET", f"/projects/{st.session_state.project_id}/prompts")
    except Exception as e:
        st.error(str(e))
        prompts = []
    if prompts:
        for pr in prompts:
            st.caption(f"{pr['role']}: {pr['content'][:120]}")
    add_role = st.selectbox("Role", ["system", "assistant", "user"])
    add_text = st.text_area("Content", height=100, placeholder="System prompt goes here")
    if st.button("Add prompt"):
        try:
            api("POST", f"/projects/{st.session_state.project_id}/prompts", json={"role": add_role, "content": add_text})
            st.success("Prompt added")
            st.rerun()
        except Exception as e:
            st.error(str(e))

    st.markdown("### Files")
    up = st.file_uploader("Upload to project", type=None)
    if up and st.button("Upload"):
        try:
            files = {"file": (up.name, up.getvalue(), up.type or "application/octet-stream")}
            data = {"purpose": "assistants"}
            api("POST", f"/projects/{st.session_state.project_id}/files", files=files, data=data)
            st.success("Uploaded")
        except Exception as e:
            st.error(str(e))
    try:
        file_list = api("GET", f"/projects/{st.session_state.project_id}/files")
        if file_list:
            st.caption("Project files:")
            for f in file_list:
                st.caption(f"- {f['filename']} ({f['bytes']} bytes)")
    except Exception as e:
        st.error(str(e))

with right:
    st.markdown("### Chat")
    msgs = st.session_state.chat.setdefault(st.session_state.project_id, [])
    for role, content in msgs:
        st.chat_message(role).write(content)

    with st.form("chat_form"):
        user_msg = st.text_area("Your message", height=100, placeholder="Ask anything")
        send = st.form_submit_button("Send")
    if send and user_msg.strip():
        try:
            msgs.append(("user", user_msg.strip()))
            reply = api("POST", f"/projects/{st.session_state.project_id}/chat", json={"message": user_msg.strip()})
            msgs.append(("assistant", reply["reply"]))
            st.rerun()
        except Exception as e:
            st.error(str(e))
