"""
ocr_image.py  —  OCR a multi-line label that must match:

    BNL LArASIC VersionP??Bdd/dddddd-ddddd
                     ▲▲ ▲ ▲      ▲   ▲
                     ││ │ │______│   └── 5-digit group
                     ││ │   6-digit group (2+4)
                     ││ └── slash
                     │└── 2-digit group
                     └─ 1–2 alphanumeric characters allowed here

Prerequisites:
    • Install Tesseract OCR engine (and add to PATH on Windows)
    • pip install pytesseract pillow
"""

import sys
import os
import re
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from PIL import Image, ImageOps, ImageFilter

# ── (Windows) point pytesseract at tesseract.exe if not on PATH ────────────
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def preprocess(img):
    """Gray → autocontrast → binary threshold → median blur."""
    img = ImageOps.grayscale(img)
    img = ImageOps.autocontrast(img)
    img = img.point(lambda p: 255 if p > 128 else 0, mode="1")
    img = img.filter(ImageFilter.MedianFilter(size=3))
    return img


ALLOWED = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/-\\")

# -------- 1–2 alphanumerics allowed between P and B ------------------------
LABEL_RE = re.compile(
    r"BNLLArASICVersionP([A-Za-z0-9]{1,2})B"   # capture 1–2 chars
    r"(\d{2})"                                 # 2-digit group
    r"/"                                       # literal slash
    r"(\d{2})(\d{3})"                          # 6-digit group (2+4)
    r"-"                                       # literal dash
    r"(\d{5})",                                # 5-digit group
    re.IGNORECASE,
)


def ocr_and_extract(path: str) -> str | None:
    """Return canonical label or *None* if the pattern is not found."""
    img       = preprocess(Image.open(path))
    whitelist = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/-\\"
    user_pattern = "BNLLArASICVersionP?Bdd/ddddd-ddddd"
    config    = f"-c tessedit_char_whitelist={whitelist} --psm 6 --user-patterns {user_pattern}"

    raw = pytesseract.image_to_string(img, lang="eng", config=config)

    flat     = re.sub(r"\s+", "", raw)                     # squash whitespace
    filtered = "".join(ch for ch in flat if ch in ALLOWED) # drop disallowed
    print (flat)

    m = LABEL_RE.search(filtered)
    if not m:
        return None

    mid, d2, d2b, d4, d5 = m.groups()
    mid = mid.upper()                                      # canonicalise case

    # Canonical form:  BNL LArASIC VersionP??Bdd/dddddd-ddddd
    return f"BNL LArASIC VersionP{mid}B{d2}/{d2b}{d4}-{d5}"


# ── CLI ────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    #if len(sys.argv) != 2:
    #    sys.exit("Usage: python ocr_image.py <image_path>")

    #img_path = sys.argv[1]
    dp = "E:/tmp\ocr/run1\images/20250709152236_OCR_POST/"
    #os.listdir(imagedir)
    image_fns = [d for d in os.listdir(dp) ]
    fns = []
    for ifn in image_fns:
        if "tray_label" in ifn:
            pass
        else:
            if ("NAN" not in ifn) and (".bmp" in ifn) and ("tray_" in ifn):
                fns.append(ifn)

        print (dp + ifn)
        try:
            label = ocr_and_extract(dp + ifn)
            if label:
                print("✔  Recognized label:")
                print(label)
            else:
                print(label)
                print("❌  Pattern not detected.")
        except Exception as exc:
            sys.exit(f"Error: {exc}")





#
#
#
#if __name__ == "__main__":
#    if len(sys.argv) != 2:
#        sys.exit("Usage: python ocr_image.py <image_path>")
#
#    try:
#        label = ocr_and_extract(sys.argv[1])
#        print("✔  Recognized label:\n" + label if label else "❌  Pattern not detected.")
#    except Exception as exc:
#        sys.exit(f"Error: {exc}")
#
exit()
"""
ocr_image.py  —  OCR a multi-line label that must match:

    BNL LArASIC VersionP5Bdd/dddddd-ddddd
                 └───────────┬────────┘
                     2-digit  6-digit     5-digit
                     group    group       group

All spaces / line breaks may vary.  Any other punctuation is discarded.

Prerequisites (once):
    • Install Tesseract      (Windows: enable 'Add to PATH' in installer)
    • pip install pytesseract pillow
"""

import sys
import os
import re
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from PIL import Image, ImageOps, ImageFilter

# -------------------------------------------------------------------------
# (Windows only)  Tell pytesseract where *tesseract.exe* lives if it
# isn’t already on PATH, e.g.:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# -------------------------------------------------------------------------


def preprocess(img: Image.Image) -> Image.Image:
    """
    Quick, generic cleanup:
      1) convert to gray
      2) autocontrast
      3) binary threshold
      4) light median blur for speckle noise
    """
    img = ImageOps.grayscale(img)
    img = ImageOps.autocontrast(img)
    img = img.point(lambda p: 255 if p > 128 else 0, mode="1")
    img = img.filter(ImageFilter.MedianFilter(size=3))
    return img


# Allowed characters after post-processing
ALLOWED = set("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/-\\")

# Regex for the *flattened* (no spaces / newlines) canonical pattern
LABEL_RE = re.compile(
    r"BNLLArASICVersionP([A-Za-z0-9]{1,2})B"        # fixed header
    r"(\d{2})"                     # 2-digit group
    r"/"                           # literal slash
    r"(\d{2})(\d{4})"              # 2-digit + 4-digit = 6-digit group
    r"-"                           # literal dash
    r"(\d{5})",                    # 5-digit group
    re.IGNORECASE,
)


def ocr_and_extract(path: str) -> str | None:
    """Return the canonical label or *None* if the pattern is not found."""
    img = preprocess(Image.open(path))

    # Whitelist the exact glyph universe → fewer OCR mistakes
    config = (
        "-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789/-\\ "
        "--psm 6"            # treat image as a block of text
    )
    raw = pytesseract.image_to_string(img, lang="eng", config=config)

    # 1) squash all whitespace
    flat = re.sub(r"\s+", "", raw)
    print (flat)

    # 2) keep *only* allowed glyphs (letters, digits, /, \, -)
    filtered = "".join(ch for ch in flat if ch in ALLOWED)

    m = LABEL_RE.search(filtered)
    if not m:
        return None

    d2, d2b, d4, d5 = m.groups()
    # Canonical re-format:
    return f"BNL LArASIC VersionP5B{d2}/{d2b}{d4}-{d5}"


# -------------------------------------------------------------------------
#  CLI
# -------------------------------------------------------------------------
if __name__ == "__main__":
    #if len(sys.argv) != 2:
    #    sys.exit("Usage: python ocr_image.py <image_path>")

    #img_path = sys.argv[1]
    dp = "E:/tmp\ocr/run1\images/20250709152236_OCR_POST/"
    #os.listdir(imagedir)
    image_fns = [d for d in os.listdir(dp) ]
    fns = []
    for ifn in image_fns:
        if "tray_label" in ifn:
            pass
        else:
            if ("NAN" not in ifn) and (".bmp" in ifn) and ("tray_" in ifn):
                fns.append(ifn)

        print (dp + ifn)
        try:
            label = ocr_and_extract(dp + ifn)
            if label:
                print("✔  Recognized label:")
                print(label)
            else:
                print(label)
                print("❌  Pattern not detected.")
        except Exception as exc:
            sys.exit(f"Error: {exc}")






exit()
"""
ocr_image.py  —  OCR a label that always matches:

    BNL LArASIC VersionP5Bdd/dddddd-ddddd
                |  |  |  |---|  |---|  |
                |  |  |   2   2  4   5   digits
                |  |  |          groups
                |  |  |
    spaces / line breaks may appear anywhere

Usage:
    python ocr_image.py path/to/image.png
"""
import sys
import re
import pytesseract
# Full path to tesseract.exe — adjust if you chose a different folder
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from PIL import Image, ImageOps, ImageFilter

# ────────────────────────────────────────────────────────────────────────────
# 1)  (only on Windows)  tell pytesseract where tesseract.exe lives:
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
# ────────────────────────────────────────────────────────────────────────────


def preprocess(img: Image.Image) -> Image.Image:
    """Gray → autocontrast → adaptive threshold → light median blur."""
    img = ImageOps.grayscale(img)
    img = ImageOps.autocontrast(img)
    # simple 128-level threshold (works well for printed labels)
    img = img.point(lambda p: 255 if p > 128 else 0, mode="1")
    img = img.filter(ImageFilter.MedianFilter(size=3))
    return img


# Regex for the *exact* string, ignoring any accidental whitespace
PATTERN = re.compile(
    r"BNL\s*LArASIC\s*VersionP5B\s*\d{2}\s*/\s*\d{2}\s*\d{4}\s*-\s*\d{5}",
    re.IGNORECASE,
)

# Same regex, but without the \s* so we can rebuild a perfect canonical form
CLEAN_PATTERN = re.compile(
    r"BNL\s*LArASIC\s*VersionP5B\s*(\d{2})\s*/\s*(\d{2})\s*(\d{4})\s*-\s*(\d{5})",
    re.IGNORECASE,
)


def ocr_and_extract(path: str) -> str | None:
    """Run OCR and return the canonical label string, or None if not found."""
    img = Image.open(path)
    img = preprocess(img)

    # Restrict tess to the characters we expect → fewer false positives
    whitelist = "BLArSICVersionP5B0123456789/"
    config = (
        f"-c tessedit_char_whitelist={whitelist} "
        "--psm 7"  # treat image as a single text line
    )
    raw = pytesseract.image_to_string(img, lang="eng", config=config)

    # Flatten whitespace so the regex sees a contiguous string
    compressed = re.sub(r"\s+", "", raw)

    match = CLEAN_PATTERN.search(compressed)
    if not match:
        return None

    # Re-assemble in the canonical   BNL LArASIC VersionP5Bdd/dddddd-ddddd   form
    d2, d2b, d4, d5 = match.groups()
    return f"BNL LArASIC VersionP5B{d2}/{d2b}{d4}/{d5}"


# ────────────────────────────────────────────────────────────────────────────
#  CLI
# ────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: python ocr_image.py <image_path>")

    img_path = sys.argv[1]
    try:
        result = ocr_and_extract(img_path)
        if result:
            print("Recognized label:\n", result)
        else:
            print("❌  Pattern not detected.")
    except Exception as e:
        sys.exit(f"Error: {e}")


exit()
"""
ocr_image.py  —  Minimal OCR helper
Usage:
    python ocr_image.py path/to/image.jpg
"""

import sys
import pytesseract
# Full path to tesseract.exe — adjust if you chose a different folder
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
from PIL import Image, ImageOps, ImageFilter

# ----- (Windows) point pytesseract at the Tesseract installation -----------
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def preprocess(img: Image.Image) -> Image.Image:
    """
    Simple preprocessing:
      • convert to grayscale
      • increase contrast
      • apply adaptive threshold
      • optional slight median blur to reduce noise
    """
    img = ImageOps.grayscale(img)
    img = ImageOps.autocontrast(img)

    # PIL’s built-in point() with lambda ≈ Otsu/threshold
    img = img.point(lambda p: 255 if p > 128 else 0, mode="1")

    # Uncomment for noisy images
    # img = img.filter(ImageFilter.MedianFilter(size=3))
    return img

def ocr_image(path: str) -> str:
    """Run OCR on a single image file and return detected text."""
    img = Image.open(path)
    img = preprocess(img)
    text = pytesseract.image_to_string(img, lang="eng")  # add other langs if needed
    return text.strip()

# ---------------------------------------------------------------------------

if __name__ == "__main__":
    #if len(sys.argv) != 2:
    #    sys.exit("Usage: python ocr_image.py <image_path>")
    image_path = "E:/tmp/ocr/run3/images/1_ocr.png"
    #sys.argv[1]

    try:
        recognized = ocr_image(image_path)
        print("---- OCR RESULT ----")
        print(recognized or "[No text detected]")
    except Exception as exc:
        sys.exit(f"Error: {exc}")

