import os
import sys

if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def asset_path(*paths):
    return os.path.join(BASE_DIR, "assets", *paths)


def get_save_path(filename="highscores.json"):
    """
    Returns a persistent writable file path for saving data (e.g. highscores).
    In frozen mode (PyInstaller/AppImage), uses the user data directory.
    In development mode, uses the project directory.
    """
    if getattr(sys, "frozen", False):
        user_dir = os.path.join(os.path.expanduser("~"), ".local", "share", "excellent_space_shooter")
        try:
            os.makedirs(user_dir, exist_ok=True)
            return os.path.join(user_dir, filename)
        except OSError:
            return os.path.join(os.path.expanduser("~"), f".{filename}")
    return os.path.join(BASE_DIR, filename)
