"""Public lead-capture page for The Art of Loving Yourself."""

from __future__ import annotations

import base64
import logging
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

import streamlit as st
from supabase import Client, create_client


EBOOK_TITLE = "The Art of Loving Yourself"
ASSETS_PATH = Path(__file__).parent / "assets"
EBOOK_PATH = ASSETS_PATH / "the-art-of-loving-yourself.pdf"
LOGO_PATH = ASSETS_PATH / "logo.png"
EBOOK_COVER_PATH = ASSETS_PATH / "ebook-cover.png"
AUTHOR_PHOTO_PATH = ASSETS_PATH / "author-photo.png"
AUTHOR_NAME = "Sireesha Puduru"
SOURCE = "LinkedIn Lead Magnet"
EMAIL_PATTERN = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")
LOGGER = logging.getLogger(__name__)


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
        .brand-area { display:flex; flex-direction:column; align-items:center; gap:.8rem; margin:1.2rem 0 2rem; }
        .brand-logo { display:block; width:auto; height:auto; max-width:min(240px, 70vw); max-height:120px; object-fit:contain; }
        .author-name { color:var(--rose-dark); font-family:Georgia,serif; font-size:1.35rem; font-style:italic;
            letter-spacing:.02em; margin:0; text-align:center; }
        .book-author-grid { display:grid; grid-template-columns:minmax(0, 1fr) minmax(0, 1fr); gap:2rem;
            align-items:center; margin:0 auto 2rem; max-width:680px; }
        .book-author-grid.single-image { grid-template-columns:minmax(0, 360px); justify-content:center; }
        .visual-image { display:block; width:100%; height:auto; margin:auto; }
        .ebook-cover { max-width:320px; object-fit:contain; }
        .author-photo { max-width:340px; border-radius:22px; object-fit:cover;
            box-shadow:0 12px 30px rgba(72,45,49,.12); }
        div[data-testid="stForm"], .success-card { background: rgba(255,255,255,.72); border: 1px solid #eadbd6;
            border-radius: 22px; padding: 1.4rem; box-shadow: 0 8px 30px rgba(72,45,49,.06); }
        div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div { border-radius: 12px; }
        .stButton > button, .stDownloadButton > button { background: var(--rose); color: white; border: 0;
            border-radius: 999px; min-height: 3rem; font-weight: 700; width: 100%; }
        .stButton > button:hover, .stDownloadButton > button:hover { background: var(--rose-dark); color:white; }
        .small-note { color:#675a5d; font-size:.9rem; text-align:center; }
        @media (max-width: 640px) {
            .block-container { padding:1.5rem 1rem 3rem; }
            h1 { font-size:2rem; }
            .book-author-grid { grid-template-columns:1fr; gap:1.5rem; }
            .ebook-cover, .author-photo { max-width:min(340px, 88vw); }
        }
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


def image_data_uri(path: Path) -> str | None:
    """Return an embedded PNG URI, or None when the optional image is unavailable."""
    if not path.is_file():
        return None
    try:
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    except OSError:
        return None
    return f"data:image/png;base64,{encoded}"


@st.cache_resource(show_spinner=False)
def get_supabase() -> Client:
    url = str(st.secrets["SUPABASE_URL"]).strip()
    key = str(st.secrets["SUPABASE_SERVICE_ROLE_KEY"]).strip()
    if not url or not key:
        raise ValueError("Supabase secrets are empty")
    if not url.startswith("https://"):
        raise ValueError("Supabase URL must begin with https://")
    parsed_url = urlparse(url)
    if parsed_url.path not in ("", "/") or parsed_url.query or parsed_url.fragment:
        raise ValueError("Supabase URL must be the base project URL without an API path")
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


def submission_error_code(error: Exception) -> str:
    """Return a safe support code without revealing infrastructure details."""
    database_code = str(getattr(error, "code", "") or "").upper()
    message = " ".join(
        str(value)
        for value in (
            getattr(error, "message", ""),
            getattr(error, "details", ""),
            getattr(error, "hint", ""),
            str(error),
        )
        if value
    ).lower()
    if database_code == "PGRST125":
        return "CONFIG-02"
    if isinstance(error, (KeyError, ValueError)) or "secret" in message or "api key" in message:
        return "CONFIG-01"
    if database_code == "42501" or any(
        term in message
        for term in ("401", "403", "jwt", "unauthorized", "forbidden", "row-level security", "permission denied")
    ):
        return "AUTH-01"
    if database_code in {"42P01", "PGRST205"} or any(
        term in message for term in ("could not find the table", "relation does not exist")
    ):
        return "TABLE-01"
    if database_code in {"42703", "PGRST204"} or "column" in message or "schema cache" in message:
        return "SCHEMA-01"
    if database_code in {"23502", "23503", "23505", "23514", "22P02"} or any(
        term in message for term in ("constraint", "null value", "duplicate key", "invalid input syntax")
    ):
        return "SCHEMA-01"
    if any(term in message for term in ("timeout", "connect", "network", "name resolution")):
        return "NETWORK-01"
    if re.fullmatch(r"[A-Z0-9]{5,8}", database_code):
        return f"DATABASE-{database_code}"
    return "DATABASE-01"


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
logo_uri = image_data_uri(LOGO_PATH)
brand_content = (
    f'<img class="brand-logo" src="{logo_uri}" alt="The Art of Loving Yourself logo">'
    if logo_uri
    else ""
)
st.markdown(
    f'<div class="brand-area">{brand_content}<p class="author-name">{AUTHOR_NAME}</p></div>',
    unsafe_allow_html=True,
)

cover_uri = image_data_uri(EBOOK_COVER_PATH)
author_photo_uri = image_data_uri(AUTHOR_PHOTO_PATH)
visuals: list[str] = []
if cover_uri:
    visuals.append(
        f'<img class="visual-image ebook-cover" src="{cover_uri}" '
        'alt="Complete cover of The Art of Loving Yourself ebook">'
    )
if author_photo_uri:
    visuals.append(
        f'<img class="visual-image author-photo" src="{author_photo_uri}" '
        f'alt="Portrait photograph of {AUTHOR_NAME}">'
    )
if visuals:
    grid_class = "book-author-grid single-image" if len(visuals) == 1 else "book-author-grid"
    st.markdown(f'<div class="{grid_class}">{"".join(visuals)}</div>', unsafe_allow_html=True)

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
            except Exception as error:
                error_code = submission_error_code(error)
                # Details go only to the private Streamlit server log, never to the web page.
                LOGGER.exception("Lead submission failed [%s]", error_code)
                st.error(
                    "We could not save your details right now. Your ebook has not been unlocked. "
                    f"Please wait a moment and try again. Support code: {error_code}"
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
