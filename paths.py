import os
import sys

if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


def asset_path(*paths):
    return os.path.join(BASE_DIR, "assets", *paths)