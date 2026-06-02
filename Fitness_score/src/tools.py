from pathlib import Path
import os

BASE = Path(__file__).resolve().parent

def translate_path(path_str):
        p = Path(os.path.normpath(os.path.join(str(BASE), path_str)))
        return p