# imghdr.py – shim for Python 3.13 removal
# This restores the old imghdr.what() behavior enough for python-telegram-bot 13.x
import mimetypes
import os

def what(file, h=None):
    """
    Lightweight replacement for Python's removed imghdr module.
    Returns 'jpeg', 'png', 'gif', etc., or None if not identifiable.
    """
    if not isinstance(file, str):
        return None
    mime, _ = mimetypes.guess_type(file)
    if mime and mime.startswith("image/"):
        return mime.split("/")[1]
    ext = os.path.splitext(file)[1].lower()
    if ext in [".jpg", ".jpeg"]:
        return "jpeg"
    if ext == ".png":
        return "png"
    if ext == ".gif":
        return "gif"
    if ext == ".bmp":
        return "bmp"
    if ext == ".webp":
        return "webp"
    return None
