import os
from pathlib import Path
from dotenv import load_dotenv
from supabase import create_client

BASE_DIR = Path(__file__).resolve().parent
DOTENV_PATH = BASE_DIR / 'integrated_systems' / '.env'

if DOTENV_PATH.exists():
    load_dotenv(dotenv_path=DOTENV_PATH)
else:
    load_dotenv()

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError(
        'Missing SUPABASE_URL or SUPABASE_KEY environment variables. '
        'Set them in your environment or in integrated_systems/.env'
    )

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# Mail configuration for OTP
MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = "jessatagle681@gmail.com"
MAIL_PASSWORD = "rnii uxsv pdfm mwgs"


def get_supabase_client():
    """Return a Supabase client instance."""
    return supabase
