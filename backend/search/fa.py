"""Persian number formatting for server-written text (reasons, explanations)."""

_FA = str.maketrans("0123456789.", "۰۱۲۳۴۵۶۷۸۹٫")


def num(n) -> str:
    if isinstance(n, float) and not n.is_integer():
        return f"{n:.1f}".translate(_FA)
    return f"{int(n):,}".replace(",", "٬").translate(_FA)


def digits(n) -> str:
    """Plain digits, no grouping: years, counts."""
    return str(n).translate(_FA)


def toman(n: int) -> str:
    """495_000_000 → '۴۹۵ میلیون'; 1_250_000_000 → '۱٫۲۵ میلیارد'."""
    if abs(n) >= 1_000_000_000:
        return f"{round(n / 1_000_000_000, 2):g}".translate(_FA) + " میلیارد"
    return num(round(n / 1_000_000)) + " میلیون"


def pct(x: float) -> str:
    return num(round(x * 100)) + "٪"
