"""Persian text helpers shared by normalization and Intent parsing."""

import re

_DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")


def latin_digits(s: str) -> str:
    return (s or "").translate(_DIGITS)


def norm(s: str) -> str:
    """Canonical form for keyword matching: Latin digits, Persian ye/kaf, ZWNJ → space, single spaces."""
    s = latin_digits(s or "").replace("‌", " ").replace("‏", "").replace("ي", "ی").replace("ك", "ک")
    return re.sub(r"\s+", " ", s).strip()


def parse_int(s) -> int | None:
    if s is None:
        return None
    if isinstance(s, (int, float)):
        return int(s)
    digits = re.sub(r"[^\d]", "", latin_digits(str(s)))
    return int(digits) if digits else None


def parse_year(s) -> int | None:
    """'۱۳۸۸ - ۲۰۰۹' → 1388; '1399' → 1399; 'مدل ۸۸' → 1388. Solar years only."""
    t = latin_digits(str(s or ""))
    m = re.search(r"\b(13\d\d|14[0-1]\d)\b", t)
    if m:
        return int(m.group(1))
    m = re.search(r"مدل\s*(\d\d)\b", t)
    if m:
        yy = int(m.group(1))
        return 1300 + yy if yy >= 50 else 1400 + yy
    return None


_UNITS = {"میلیارد": 1_000_000_000, "میلیون": 1_000_000, "م": 1_000_000, "هزار": 1_000}


def parse_amount(text: str) -> int | None:
    """Toman amount from free Persian text: '۸۰۰ میلیون', '۸۰۰م', 'یک و نیم میلیارد', '1.2 میلیارد', '880,000,000'."""
    t = norm(text)
    words = {"یک": 1, "دو": 2, "سه": 3, "چهار": 4, "پنج": 5, "شش": 6, "هفت": 7, "هشت": 8, "نه": 9, "ده": 10}
    m = re.search(r"(یک|دو|سه|چهار|پنج)\s*و\s*نیم\s*(میلیارد|میلیون)", t)
    if m:
        return int((words[m[1]] + 0.5) * _UNITS[m[2]])
    m = re.search(r"(\d+(?:[.,/٫]\d+)?)\s*(میلیارد|میلیون|هزار|م)(?![آ-ی])", t)
    if m:
        num = float(m[1].replace(",", ".").replace("/", ".").replace("٫", "."))
        return int(num * _UNITS[m[2]])
    m = re.search(r"(" + "|".join(words) + r")\s*(میلیارد|میلیون)", t)
    if m:
        return words[m[1]] * _UNITS[m[2]]
    m = re.search(r"\d{1,3}(?:,\d{3}){2,}|\d{7,}", t)
    if m:
        return int(m.group().replace(",", ""))
    return None
