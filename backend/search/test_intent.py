import json

import pytest
from rest_framework.test import APIClient

from llm import client as llm
from search.intent import resolve
from search.parse import keyword_parse, llm_parse

PRIDES = ["pride-111", "pride-131", "pride-132", "pride-141"]

# (text, expected constraints subset, expected (pref key, strength) set, expected needs)
GOLDEN = [
    ("ماشین خانوادگی تا ۸۰۰ میلیون، خیلی کم‌مصرف، فقط اتوماتیک",
     {"max_price": 800_000_000, "gearbox": "automatic"}, {("low_fuel", "strong")}, ["family"]),
    ("فقط اتوماتیک زیر ۳۰۰ میلیون", {"max_price": 300_000_000, "gearbox": "automatic"}, set(), []),
    ("برای اسنپ، مدل ۹۸ به بالا، کارکرد زیر ۱۰۰ هزار", {"min_year": 1398, "max_mileage": 100_000}, set(), ["ride_hailing"]),
    ("پراید نمیخوام، بودجه یک و نیم میلیارد، بدون رنگ",
     {"max_price": 1_500_000_000, "exclude_models": PRIDES, "body_condition": "clean"}, set(), []),
    ("۲۰۶ یا کوییک تا ۶۰۰م", {"max_price": 600_000_000, "models": ["peugeot-206ir", "peugeot-206sd", "quick"]}, set(), []),
    ("یه چیزی مثل ۲۰۶ ارزون", {"models": []}, {("like", "normal"), ("cheaper", "normal")}, []),
    ("ماشین شهری کم‌کارکرد", {}, {("low_mileage", "normal")}, ["city"]),
    ("می‌خوام ماشین بخرم که ضرر نکنم", {}, set(), ["holds_value"]),
    ("ماشین اقتصادی دوگانه سوز تا ۵۰۰ میلیون", {"max_price": 500_000_000}, {("dual_fuel", "normal")}, ["economical"]),
    ("فقط دوگانه‌سوز", {"fuel_type": "dual"}, set(), []),
    ("دنا پلاس مدل بالا تا ۱.۲ میلیارد", {"models": ["dena"], "max_price": 1_200_000_000}, {("newer", "normal")}, []),
    ("ماشین", {}, set(), []),
]


@pytest.mark.parametrize("text,constraints,prefs,needs", GOLDEN)
def test_keyword_parser_golden(text, constraints, prefs, needs):
    i = keyword_parse(text)
    for k, v in constraints.items():
        assert i["constraints"][k] == v, k
    assert {(p["key"], p["strength"]) for p in i["preferences"]} == prefs
    assert [n["key"] for n in i["needs"]] == needs
    assert i["constraints"]["city"] == "tehran"


def test_resolve_explicit_beats_need_and_duplicates_merge():
    i = keyword_parse("ماشین خانوادگی هاچبک، کم‌مصرف")
    i["needs"].append({"key": "economical", "off": ["popular"]})
    r = resolve(i)
    keys = {p["key"]: p for p in r["resolved_preferences"]}
    assert "body_sedan" not in keys and {"key": "body_sedan", "need": "family"}.items() <= r["dropped"][0].items()
    assert keys["low_fuel"]["strength"] == "strong"  # explicit normal + economical's strong → strong
    assert "popular" not in keys                      # switched off on the Need chip
    assert keys["body_hatchback"]["origin"] == "explicit"


def test_llm_parse_numbers_come_from_our_code_and_spans_must_exist():
    def fake(model, system, prompt, schema):
        return json.dumps({
            "max_price_span": "تا ۸۰۰ میلیون", "min_price_span": None, "min_year_span": "مدل ۱۴۰۵ به بالا",
            "max_year_span": None, "max_mileage_span": None, "models": ["dena"], "exclude_models": [],
            "gearbox": None, "fuel_type": None, "body_condition": None,
            "preferences": [{"key": "low_fuel", "strength": "strong", "like_model": None, "span": "خیلی کم‌مصرف"}],
            "needs": [{"key": "family", "span": "خانوادگی"}],
        })
    llm.use_fake(fake)
    try:
        i = llm_parse("دنا خانوادگی تا ۸۰۰ میلیون، خیلی کم‌مصرف")
    finally:
        llm.use_fake(None)
    assert i["constraints"]["max_price"] == 800_000_000
    assert i["constraints"]["min_year"] is None  # invented span not in the text → ignored
    assert i["constraints"]["models"] == ["dena"] and i["source"] == "llm"


@pytest.mark.django_db
def test_parse_and_needs_endpoints(settings):
    settings.ANTHROPIC_API_KEY = ""
    c = APIClient()
    r = c.post("/api/intent/parse", {"text": "خانوادگی تا ۸۰۰ میلیون"}, format="json").json()
    assert r["constraints"]["max_price"] == 800_000_000 and r["source"] == "keywords"
    assert any(p["origin"] == "need:family" for p in r["resolved_preferences"])
    needs = c.get("/api/needs").json()
    assert set(needs["needs"]) == {"family", "economical", "city", "ride_hailing", "holds_value"}
