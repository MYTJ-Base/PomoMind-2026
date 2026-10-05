"""All tunable constants live here. No Streamlit imports, no logic."""

APP_NAME = "PomoMind AI"
APP_ICON = "🔒"

# --- Languages -------------------------------------------------------------
DEFAULT_LANGUAGE = "en"
LANGUAGES = {"en": "English", "fr": "French"}

# --- Roles -----------------------------------------------------------------
ROLE_STUDENT = "Student"
ROLE_PROFESSOR = "Professor"
ROLES = (ROLE_STUDENT, ROLE_PROFESSOR)

# --- Gamification ----------------------------------------------------------
STARTING_XP = 150
XP_POMODORO = 50
XP_FLASHCARDS = 20
POMODORO_SECONDS = 10  # focus phase, demo length; set to 25 * 60 for a real Pomodoro
BREAK_SECONDS = 5      # short break after each focus phase; e.g. 5 * 60 for real use
APP_UTC_OFFSET_HOURS = 1  # Cameroon (WAT = UTC+1, no DST): decides when a new "day" starts for streaks
PROGRESS_DB_PATH = "data/pomomind.db"  # SQLite file holding XP / streak / badges per user

# (badge key, XP needed), in ascending order. PLACEHOLDER thresholds: to be agreed with the team.
# Each key needs a label "badge.<key>" in every language in locales.py.
BADGES = (
    ("brain_of_mokolo", 300),
    ("ict_expert", 1000),
)

# --- Professor workflow ----------------------------------------------------
BROADCAST_COOLDOWN_SECONDS = 10

# --- Gemini ----------------------------------------------------------------
# Models are tried in order; the next one is used only on 503/UNAVAILABLE.
VERIFY_MODELS = ("gemini-3.8-flash", "gemini-2.5-pro")
FLASHCARD_MODEL = "gemini-2.5-flash"
FLASHCARD_COUNT = 3
VALID_MARKER = "[VALIDE]"  # the verification prompt asks the model to answer with this

# --- Study sounds ----------------------------------------------------------
# The music files live in the folder AUDIO_DIR (project root). SOUNDS maps
#   sound key -> file name inside AUDIO_DIR   (None = silence).
# The music author provides the files: drop them in assets/audio/ and make the names match here.
# Supported formats: .mp3, .wav, .ogg. Labels come from locales.py ("sound.<key>").
AUDIO_DIR = "assets/audio"
SOUNDS = {
    "silence": None,
    "lofi": "lofi.mp3",
    "binaural": "binaural.mp3",
}
HEADPHONES_RECOMMENDED = ("binaural",)  # sounds that show the "use headphones" hint
