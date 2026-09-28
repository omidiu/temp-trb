import json
from pathlib import Path

import pytest

from market import extract, rules
from market.text import parse_amount, parse_int, parse_year

FIX = Path(__file__).parent / "fixtures"


@pytest.mark.parametrize("text,expected", [
    ("۸۰۰ میلیون", 800_000_000),
    ("تا ۸۰۰م", 800_000_000),
    ("یک و نیم میلیارد", 1_500_000_000),
    ("1.2 میلیارد", 1_200_000_000),
    ("‏۸۸۰,۰۰۰,۰۰۰ تومان", 880_000_000),
    ("دو میلیارد", 2_000_000_000),
    ("بدون عدد", None),
])
def test_parse_amount(text, expected):
    assert parse_amount(text) == expected


def test_parse_year_and_int():
    assert parse_year("۱۳۸۸ - ۲۰۰۹") == 1388
    assert parse_year("۲۰۶ مدل ۸۸") == 1388
    assert parse_year("مدل ۰۲") == 1402
    assert parse_int("۲۴۲,۰۰۰ کیلومتر") == 242000


@pytest.mark.parametrize("body,chassis,expected", [
    ("سالم و بی‌خط و خش", [], "clean"),
    ("خط و خش جزیی", ["تعیین‌نشده"], "clean"),
    ("صافکاری بی‌رنگ", [], "clean"),
    ("رنگ‌شدگی در ۲ ناحیه", [], "minor"),
    ("یک لکه رنگ", [], "minor"),
    ("رنگ‌شدگی در چند ناحیه", [], "major"),
    ("دور رنگ", [], "major"),
    ("سالم و بی‌خط و خش", ["ضربه‌خورده"], "major"),
    ("", [], ""),
])
def test_body_condition(body, chassis, expected):
    assert rules.body_condition(body, *chassis) == expected


def test_exclusion():
    assert rules.exclusion("۲۰۶ اقساطی", "", 300_000_000) == "instalment"
    assert rules.exclusion("حواله دنا", "", 900_000_000) == "presale"
    assert rules.exclusion("پراید", "", 1_000) == "placeholder"
    assert rules.exclusion("پراید ۱۳۱", "تمیز", 250_000_000) == ""


def test_divar_extract():
    post = json.loads((FIX / "divar_post.json").read_text())
    f = extract.divar({"post": post, "row": {"image_url": "x"}})
    assert f["raw_name"] == "Peugeot 206 2"
    assert (f["year"], f["mileage"], f["price"]) == (1388, 242_000, 880_000_000)
    assert (f["gearbox"], f["fuel_type"], f["body_condition"]) == ("manual", "gasoline", "clean")
    assert f["exclusion"] == ""
