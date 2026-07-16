"""Password-protected administrator dashboard."""

from __future__ import annotations

import hmac
from datetime import date, datetime, timezone

import pandas as pd
import streamlit as st
from supabase import Client, create_client


st.set_page_config(page_title="Admin Dashboard", page_icon="🔒", layout="wide")


st.markdown(
    """
    <style>
    .stApp { background:#fbf7f2; color:#302b2c; }
    [data-testid="stHeader"] { background:transparent; }
    h1,h2,h3 { font-family:Georgia,serif; color:#302b2c; }
    [data-testid="stMetric"] { background:white; border:1px solid #eadbd6; border-radius:16px; padding:1rem; }
    .stButton > button, .stDownloadButton > button { border-radius:999px; }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource(show_spinner=False)
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
    if not url or not key:
        raise ValueError("Supabase secrets are empty")
    return create_client(url, key)


@st.cache_data(ttl=60, show_spinner=False)
def load_leads() -> pd.DataFrame:
    columns = (
        "id,lead_number,created_at,name,email,contact_number,inspiration,"
        "marketing_consent,download_status,download_count,source,archived"
    )
    rows: list[dict[str, object]] = []
    page_size = 1000
    start = 0
    while True:
        response = (
            get_supabase()
            .table("leads")
            .select(columns)
            .order("created_at", desc=True)
            .range(start, start + page_size - 1)
            .execute()
        )
        page = response.data or []
        rows.extend(page)
        if len(page) < page_size:
            break
        start += page_size
    frame = pd.DataFrame(rows)
    if frame.empty:
        return pd.DataFrame(
            columns=[
                "id", "lead_number", "created_at", "name", "email", "contact_number",
                "inspiration", "marketing_consent", "download_status", "download_count", "source", "archived",
            ]
        )
    frame["created_at"] = pd.to_datetime(frame["created_at"], utc=True, errors="coerce")
    frame["download_count"] = pd.to_numeric(frame["download_count"], errors="coerce").fillna(0).astype(int)
    frame["archived"] = frame["archived"].fillna(False).astype(bool)
    return frame


def secrets_are_valid() -> bool:
    required = ("ADMIN_USERNAME", "ADMIN_PASSWORD", "SUPABASE_URL", "SUPABASE_SERVICE_ROLE_KEY")
    try:
        return all(str(st.secrets[key]).strip() for key in required)
    except (KeyError, FileNotFoundError):
        return False


def login() -> None:
    st.title("Administrator Sign In")
    st.write("Enter the administrator details stored in Streamlit Secrets.")
    with st.form("admin_login"):
        username = st.text_input("Username", autocomplete="username")
        password = st.text_input("Password", type="password", autocomplete="current-password")
        submitted = st.form_submit_button("Sign In", use_container_width=True)
    if submitted:
        try:
            valid_user = hmac.compare_digest(username, str(st.secrets["ADMIN_USERNAME"]))
            valid_password = hmac.compare_digest(password, str(st.secrets["ADMIN_PASSWORD"]))
        except (KeyError, FileNotFoundError):
            valid_user = valid_password = False
        if valid_user and valid_password:
            st.session_state.admin_authenticated = True
            st.rerun()
        else:
            st.error("The username or password is incorrect.")


if not secrets_are_valid():
    st.error("The application secrets have not been configured. Please ask the site owner for help.")
    st.stop()

if not st.session_state.get("admin_authenticated", False):
    login()
    st.stop()

top_left, refresh_col, logout_col = st.columns([6, 1, 1])
with top_left:
    st.title("Lead Dashboard")
with refresh_col:
    if st.button("Refresh", use_container_width=True):
        load_leads.clear()
        st.rerun()
with logout_col:
    if st.button("Logout", use_container_width=True):
        st.session_state.admin_authenticated = False
        st.rerun()

try:
    all_leads = load_leads()
except Exception:
    st.error("The leads could not be loaded. Please check the app configuration and try again.")
    st.stop()

active = all_leads.loc[~all_leads["archived"]].copy()
now_utc = datetime.now(timezone.utc)
created = active["created_at"]
today_count = int((created.dt.date == now_utc.date()).sum()) if not active.empty else 0
month_count = int(((created.dt.year == now_utc.year) & (created.dt.month == now_utc.month)).sum()) if not active.empty else 0
downloads = int(active["download_count"].sum()) if not active.empty else 0
pending = int(active["download_status"].eq("Pending").sum()) if not active.empty else 0

metric_cols = st.columns(5)
for column, label, value in zip(
    metric_cols,
    ["Total leads", "Received today", "This month", "Ebook downloads", "Pending downloads"],
    [len(active), today_count, month_count, downloads, pending],
):
    column.metric(label, value)

st.subheader("Find and filter leads")
filter_cols = st.columns([1.2, 1.2, 1, 1, 1])
name_search = filter_cols[0].text_input("Search by name")
email_search = filter_cols[1].text_input("Search by email")
status_options = ["All"] + sorted(active["download_status"].dropna().unique().tolist())
status_filter = filter_cols[2].selectbox("Download status", status_options)
sort_order = filter_cols[3].selectbox("Sort", ["Newest first", "Oldest first"])
show_archived = filter_cols[4].checkbox("Show archived", value=False)

filtered = all_leads.copy() if show_archived else active.copy()
if name_search.strip():
    filtered = filtered[filtered["name"].fillna("").str.contains(name_search.strip(), case=False, regex=False)]
if email_search.strip():
    filtered = filtered[filtered["email"].fillna("").str.contains(email_search.strip(), case=False, regex=False)]
if status_filter != "All":
    filtered = filtered[filtered["download_status"].eq(status_filter)]

valid_dates = filtered["created_at"].dropna()
default_start = valid_dates.min().date() if not valid_dates.empty else date.today()
default_end = valid_dates.max().date() if not valid_dates.empty else date.today()
date_range = st.date_input("Date range", value=(default_start, default_end), max_value=date.today())
if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        (filtered["created_at"].dt.date >= start_date) & (filtered["created_at"].dt.date <= end_date)
    ]

filtered = filtered.sort_values("created_at", ascending=sort_order == "Oldest first")
display = filtered.rename(
    columns={
        "lead_number": "Lead number", "created_at": "Date", "name": "Name", "email": "Email",
        "contact_number": "Contact number", "inspiration": "Inspiration",
        "marketing_consent": "Marketing consent", "download_status": "Download status", "source": "Source",
    }
)
display_columns = [
    "Lead number", "Date", "Name", "Email", "Contact number", "Inspiration",
    "Marketing consent", "Download status", "Source",
]
st.caption(f"Showing {len(display)} lead(s). Dates and dashboard metrics use UTC.")
st.dataframe(display[display_columns], use_container_width=True, hide_index=True)

export = display[display_columns].copy()
# Stop spreadsheet programs from treating user-entered text as formulas.
for column in ["Name", "Email", "Contact number", "Inspiration", "Source"]:
    export[column] = export[column].apply(
        lambda value: f"'{value}" if isinstance(value, str) and value.startswith(("=", "+", "-", "@")) else value
    )
csv_data = export.to_csv(index=False).encode("utf-8")
st.download_button(
    "Export filtered leads as CSV",
    data=csv_data,
    file_name=f"ebook-leads-{date.today().isoformat()}.csv",
    mime="text/csv",
)

st.subheader("Archive leads")
st.caption("Archived leads are kept in the database and can still be viewed. Nothing is permanently deleted.")
archive_candidates = active["lead_number"].dropna().tolist()
selected = st.multiselect("Select lead numbers to archive", archive_candidates)
if st.button("Archive selected leads", disabled=not selected):
    try:
        get_supabase().table("leads").update({"archived": True}).in_("lead_number", selected).execute()
        load_leads.clear()
        st.success(f"Archived {len(selected)} lead(s).")
        st.rerun()
    except Exception:
        st.error("The selected leads could not be archived. Please try again.")
