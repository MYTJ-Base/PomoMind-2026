from src.pomomind.config import HEADPHONES_RECOMMENDED, SOUNDS

SUPPORTED = (".mp3", ".wav", ".ogg")


def test_sound_files_have_supported_extensions():
    for key, filename in SOUNDS.items():
        if filename is not None:
            assert filename.lower().endswith(SUPPORTED), f"{key}: {filename}"


def test_headphone_hint_only_for_known_sounds():
    assert all(key in SOUNDS for key in HEADPHONES_RECOMMENDED)
