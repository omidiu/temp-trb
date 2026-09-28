import math

import pytest

from catalog.models import Vehicle
from market.models import ModelStats, Offer
from market.stats import compute_market, depreciation, solar_year, verdict


@pytest.fixture
def v206(db):
    return Vehicle.objects.create(id="peugeot-206ir-type2", make="peugeot", make_fa="پژو", model="206ir",
                                  model_fa="پژو 206", trim="type2", trim_fa="تیپ 2", family="peugeot-206ir")


def offer(price, year=1399, km=85_000, cond="clean", **kw):
    return Offer.objects.create(vehicle_id="peugeot-206ir-type2", title="206", year=year, mileage=km,
                                price=price, body_condition=cond, **kw)


def test_spec_worked_example(v206):
    """206 Tip 2, 1399, 85k km, clean, 495M; 11 tier-1 comparables with median 520M, 9 pricier → great deal."""
    target = offer(495_000_000)
    for p in [480, 490, 500, 505, 510, 520, 525, 530, 540, 545, 550]:
        offer(p * 1_000_000, km=85_000 + p)  # all within ±20k km
    compute_market()
    target.refresh_from_db()
    assert target.fair_price == 520_000_000
    assert target.p_cheaper == pytest.approx(9 / 11)
    assert (target.verdict, target.confidence) == ("great", "high")
    assert len(target.comparable_ids) == 11


def test_suspicious_beats_great():
    comps = [type("C", (), {"price": p})() for p in [500, 510, 520, 530, 540]]
    assert verdict(350, comps)[2] == "suspicious"   # > 25% under median 520
    assert verdict(515, comps)[2] == "fair"
    assert verdict(495, comps)[2] == "great"
    assert verdict(545, comps)[2] == "overpriced"


def test_too_few_comparables_gives_no_verdict_and_tiers_widen(v206):
    target = offer(500_000_000)
    for i in range(4):
        offer(510_000_000 + i, year=1400)  # only tier 2/3 (year ±1)
    compute_market()
    target.refresh_from_db()
    assert target.verdict == "unknown"          # 4 < 5 comparables
    offer(520_000_000, year=1398)
    compute_market()
    target.refresh_from_db()
    assert (target.verdict, target.confidence) == ("great", "medium")


def test_excluded_offers_get_no_verdict_and_are_not_comparables(v206):
    target = offer(500_000_000)
    for i in range(5):
        offer(300_000_000 + i, exclusion="instalment")
    compute_market()
    target.refresh_from_db()
    assert target.verdict == "unknown"


def test_depreciation_slope():
    this = 1405
    rows = []
    for age, median in [(1, 1000), (2, 920), (3, 846)]:  # ≈ 8% per year
        rows += [type("O", (), {"year": this - age, "price": median})() for _ in range(5)]
    assert depreciation(rows, this) == pytest.approx(0.08, abs=0.002)


def test_popularity(v206):
    Vehicle.objects.create(id="tiba-sedan-sx", make="tiba", make_fa="تیبا", model="sedan", model_fa="تیبا", family="tiba")
    offer(500_000_000)
    offer(501_000_000)
    Offer.objects.create(vehicle_id="tiba-sedan-sx", title="t", year=1399, mileage=1, price=400_000_000)
    compute_market()
    assert ModelStats.objects.get(model_key="peugeot-206ir").popularity == 1.0
    assert ModelStats.objects.get(model_key="tiba").popularity == 0.0


def test_solar_year():
    from datetime import date
    assert solar_year(date(2026, 9, 28)) == 1405
    assert solar_year(date(2026, 3, 1)) == 1404
