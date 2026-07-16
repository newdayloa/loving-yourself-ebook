"""Public lead-capture page for The Art of Loving Yourself."""

from __future__ import annotations

import re
import uuid
from datetime import datetime, timezone
from pathlib import Path

import streamlit as st
from supabase import Client, create_client


EBOOK_TITLE = "The Art of Loving Yourself"
EBOOK_PATH = Path(__file__).parent / "assets" / "the-art-of-loving-yourself.pdf"
SOURCE = "LinkedIn Lead Magnet"
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")


st.set_page_config(
    page_title=f"Complimentary Ebook | {EBOOK_TITLE}",
    page_icon="🌸",
    layout="centered",
    initial_sidebar_state="collapsed",
)


def apply_styles() -> None:
    st.markdown(
        """
        <style>
        :root { --cream:#fbf7f2; --rose:#a96370; --rose-dark:#824754; --charcoal:#302b2c; }
        .stApp { background: var(--cream); color: var(--charcoal); }
        [data-testid="stHeader"] { background: transparent; }
        [data-testid="stSidebarNav"] { background: #f3e9e5; }
        .block-container { max-width: 760px; padding-top: 3rem; padding-bottom: 4rem; }
        h1, h2, h3 { color: var(--charcoal); font-family: Georgia, serif; line-height: 1.2; }
        h1 { text-align: center; }
        .eyebrow { color: var(--rose-dark); font-size: .82rem; font-weight: 700; letter-spacing: .14em;
            text-align: center; text-transform: uppercase; }
        .intro { font-size: 1.08rem; line-height: 1.75; text-align: center; margin: 0 auto 1.6rem; max-width: 650px; }
        .placeholder { border: 1px dashed #b88b93; border-radius: 18px; color: #765d62; padding: 2rem 1rem;
            text-align: center; background: #fffaf7; margin-bottom: 1rem; }
        .brand-row { display:flex; gap:1rem; justify-content:center; flex-wrap:wrap; margin-bottom:1rem; }
        .brand-row .placeholder { min-width:180px; padding:1rem; }
        div[data-testid="stForm"], .success-card { background: rgba(255,255,255,.72); border: 1px solid #eadbd6;
            border-radius: 22px; padding: 1.4rem; box-shadow: 0 8px 30px rgba(72,45,49,.06); }
        div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div { border-radius: 12px; }
        .stButton > button, .stDownloadButton > button { background: var(--rose); color: white; border: 0;
            border-radius: 999px; min-height: 3rem; font-weight: 700; width: 100%; }
        .stButton > button:hover, .stDownloadButton > button:hover { background: var(--rose-dark); color:white; }
        .small-note { color:#675a5d; font-size:.9rem; text-align:center; }
        @media (max-width: 640px) { .block-container { padding: 1.5rem 1rem 3rem; } h1 { font-size:2rem; } }
        </style>
        """,
        unsafe_allow_html=True,
    )


def clean_text(value: str, max_length: int | None = None, single_line: bool = False) -> str:
    """Remove control characters and unnecessary whitespace from user input."""
    value = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", "", value or "")
    if single_line:
        value = re.sub(r"\s+", " ", value)
    else:
        value = "\n".join(line.strip() for line in value.splitlines()).strip()
    value = value.strip()
    return value[:max_length] if max_length else value


@st.cache_resource(show_spinner=False)
def get_supabase() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
    if not url or not key:
        raise ValueError("Supabase secrets are empty")
    return create_client(url, key)


def validate(name: str, email: str) -> list[str]:
    errors: list[str] = []
    if len(name) < 2:
        errors.append("Please enter a name with at least two characters.")
    elif not any(character.isalpha() for character in name):
        errors.append("Please enter a valid name, not numbers only.")
    if not email:
        errors.append("Please enter your email address.")
    elif len(email) > 254 or not EMAIL_PATTERN.fullmatch(email):
        errors.append("Please enter a valid email address (for example, name@example.com).")
    return errors


def save_lead(payload: dict[str, object]) -> dict[str, object]:
    response = get_supabase().table("leads").insert(payload).execute()
    if not response.data:
        raise RuntimeError("Lead was not saved")
    return response.data[0]


def record_download(lead_id: str) -> None:
    """Record the first download click without exposing database errors."""
    try:
        client = get_supabase()
        result = client.table("leads").select("download_count").eq("id", lead_id).single().execute()
        current_count = int((result.data or {}).get("download_count") or 0)
        client.table("leads").update(
            {
                "download_status": "Downloaded",
                "download_count": current_count + 1,
                "downloaded_at": datetime.now(timezone.utc).isoformat(),
            }
        ).eq("id", lead_id).execute()
        st.session_state.download_clicked = True
    except Exception:
        # The lead is already safely stored. Avoid revealing infrastructure details.
        st.session_state.download_tracking_error = True


apply_styles()

st.markdown('<div class="eyebrow">A complimentary ebook for you</div>', unsafe_allow_html=True)
st.title('Get Your Complimentary Copy of “The Art of Loving Yourself”')
st.markdown(
    """
    <div class="intro">
    Thank you for your interest in <em>The Art of Loving Yourself</em>.<br><br>
    This book is my gift to high-achieving women who are ready to stop seeking validation
    outside themselves and begin building a loving relationship within.<br><br>
    Simply enter your details below, and your complimentary copy will be available immediately.
    </div>
    """,
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="brand-row"><div class="placeholder">Logo placeholder</div>'
    '<div class="placeholder">Author name placeholder</div></div>',
    unsafe_allow_html=True,
)
left, right = st.columns(2)
with left:
    st.markdown('<div class="placeholder">Ebook cover placeholder</div>', unsafe_allow_html=True)
with right:
    st.markdown('<div class="placeholder">Author photograph placeholder</div>', unsafe_allow_html=True)

if "lead" not in st.session_state:
    st.session_state.lead = None
if "download_clicked" not in st.session_state:
    st.session_state.download_clicked = False

if st.session_state.lead is None:
    with st.form("lead_form", clear_on_submit=False):
        name_input = st.text_input("Name *", max_chars=150, placeholder="Your name")
        email_input = st.text_input("Email *", max_chars=254, placeholder="you@example.com")
        contact_input = st.text_input("Contact Number (optional)", max_chars=50, placeholder="Your contact number")
        inspiration_input = st.text_area(
            "What inspires you to download this book? (optional)",
            max_chars=1000,
            height=130,
            placeholder="Share what brought you here…",
        )
        consent_input = st.checkbox(
            "I would like to receive occasional insights, updates and resources.", value=False
        )
        submitted = st.form_submit_button("Get My Complimentary Copy", use_container_width=True)

    if submitted:
        name = clean_text(name_input, 150, single_line=True)
        email = clean_text(email_input, 254, single_line=True).lower()
        contact = clean_text(contact_input, 50, single_line=True)
        inspiration = clean_text(inspiration_input, 1000)
        errors = validate(name, email)
        if errors:
            for message in errors:
                st.error(message)
        else:
            payload: dict[str, object] = {
                "id": str(uuid.uuid4()),
                "lead_number": f"LOVE-{datetime.now(timezone.utc):%Y%m%d}-{uuid.uuid4().hex[:8].upper()}",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "name": name,
                "email": email,
                "contact_number": contact or None,
                "inspiration": inspiration or None,
                "marketing_consent": bool(consent_input),
                "source": SOURCE,
                "ebook_title": EBOOK_TITLE,
                "download_status": "Pending",
                "download_count": 0,
                "archived": False,
            }
            try:
                with st.spinner("Preparing your complimentary copy…"):
                    st.session_state.lead = save_lead(payload)
                st.rerun()
            except Exception:
                st.error(
                    "We could not save your details right now. Your ebook has not been unlocked. "
                    "Please wait a moment and try again."
                )
else:
    st.success("Your details were saved successfully.")
    st.markdown('<div class="success-card">', unsafe_allow_html=True)
    st.header("Your Complimentary Copy Is Ready")
    st.write(
        "Thank you for taking this meaningful step towards building a more loving relationship "
        "with yourself."
    )
    st.write('Your complimentary copy of “The Art of Loving Yourself” is ready.')
    if not EBOOK_PATH.is_file():
        st.error("The ebook is temporarily unavailable. Please contact the site owner.")
    elif st.session_state.download_clicked:
        st.success("Your download has started. We hope you enjoy the book.")
    else:
        try:
            ebook_bytes = EBOOK_PATH.read_bytes()
            st.download_button(
                "Download the Ebook",
                data=ebook_bytes,
                file_name="the-art-of-loving-yourself.pdf",
                mime="application/pdf",
                on_click=record_download,
                args=(str(st.session_state.lead["id"]),),
                use_container_width=True,
            )
        except OSError:
            st.error("The ebook is temporarily unavailable. Please contact the site owner.")
    if st.session_state.get("download_tracking_error"):
        st.warning("Your ebook is available, but we could not update its download status.")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown(
    '<p class="small-note">Your details are used only to deliver this resource and according to your consent choice.</p>',
    unsafe_allow_html=True,
)
