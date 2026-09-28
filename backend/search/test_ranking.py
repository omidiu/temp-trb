import pytest

from catalog.models import Vehicle
from market.models import Offer
from search.intent import empty_intent, resolve
from search.ranking import percentile_scores, rank, total_score


def test_spec_worked_example_score():
    """Family (sedan strong 1, airbags 0.6, ABS 1, newer 0.7, clean 1) + explicit strong low fuel 0.7, deal p=0.85."""
    parts = [(2, 1), (1, 0.6), (1, 1), (1, 0.7), (1, 1), (2, 0.7)]
    assert total_score(0.85, parts) == pytest.approx(0.84)


def test_no_preferences_means_best_deals_first():
    assert total_score(0.9, []) > total_score(0.4, [])


def test_percentiles():
    assert percentile_scores([100, 200, 300], higher_is_better=False) == [1.0, 0.5, 0.0]
    assert percentile_scores([5, None, 5], higher_is_better=True) == [0.5, None, 0.5]


@pytest.fixture
def market(db):
    Vehicle.objects.create(id="dena-plus-turbo", make="dena", make_fa="دنا", model="plus", model_fa="دنا پلاس",
                           family="dena", body_type="sedan", fuel_consumption=7.9, airbags=2, abs=True)
    Vehicle.objects.create(id="quick-manualr", make="quick", make_fa="کوییک", model="manualr", model_fa="کوییک R",
                           family="quick", body_type="hatchback", fuel_consumption=7.0, airbags=2, abs=True)

    def mk(vid, price, verdict="fair", p=0.5, **kw):
        return Offer.objects.create(vehicle_id=vid, title="x", year=1400, mileage=50_000, price=price,
                                    verdict=verdict, p_cheaper=p, fair_price=price, confidence="high", **kw)
    return {
        "cheap_suspicious": mk("quick-manualr", 300_000_000, verdict="suspicious", p=1.0),
        "great_dena": mk("dena-plus-turbo", 780_000_000, verdict="great", p=0.9),
        "fair_quick": mk("quick-manualr", 600_000_000),
        "over_budget": mk("dena-plus-turbo", 850_000_000, verdict="great", p=0.95),
        "too_expensive": mk("dena-plus-turbo", 950_000_000),
        "placeholder": mk("quick-manualr", 1_000, exclusion="placeholder"),
    }


def intent_with(**constraints):
    i = empty_intent()
    i["constraints"].update(constraints)
    return i


def test_filters_groups_and_top_pick(market):
    r = rank(resolve(intent_with(max_price=800_000_000)))
    main_ids = [x["offer"].pk for x in r["main"]]
    assert market["placeholder"].pk not in main_ids
    assert market["too_expensive"].pk not in main_ids
    assert [x["offer"].pk for x in r["over_budget"]] == [market["over_budget"].pk]
    assert r["top_pick"] == market["great_dena"].pk
    assert r["main"][-1]["offer"].pk == market["cheap_suspicious"].pk  # deal score 0


def test_family_need_prefers_sedan(market):
    i = intent_with(max_price=800_000_000)
    i["needs"] = [{"key": "family", "off": []}]
    r = rank(resolve(i))
    top = r["main"][0]
    assert top["offer"].vehicle.body_type == "sedan"
    assert any(b["key"] == "body_sedan" and b["weight"] == 2 for b in top["breakdown"])


def test_zero_results_relaxations(market):
    from search.relax import suggestions
    s = suggestions({**empty_intent()["constraints"], "max_price": 500_000_000, "gearbox": "automatic"})
    labels = {x["label"]: x for x in s}
    assert "با گیربکس دستی" in labels and labels["با گیربکس دستی"]["patch"] == {"gearbox": None}
    assert labels["با گیربکس دستی"]["count"] >= 1
