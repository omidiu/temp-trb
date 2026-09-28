import json

import pytest

from catalog.models import Vehicle, VehicleAlias
from llm import client as llm
from market.llm_normalize import enrich
from market.models import Listing


@pytest.fixture
def fake_llm():
    calls = []

    def fake(model, system, prompt, schema):
        calls.append(prompt)
        props = schema["properties"]
        if "vehicle_id" in props:
            return json.dumps({"vehicle_id": "pride-131-se", "reason": "131 SE in the title"})
        return json.dumps({"body_condition": "minor", "offer_type": "used_car"})

    llm.use_fake(fake)
    yield calls
    llm.use_fake(None)


@pytest.fixture
def data(db):
    for trim in ["se", "sx"]:
        Vehicle.objects.create(id=f"pride-131-{trim}", make="pride", make_fa="پراید", model="131",
                               model_fa="پراید 131", trim=trim, trim_fa=trim.upper(), family="pride-131")
    common = dict(source="divar", raw_name="Pride 131 SE-new", title="پراید ۱۳۱ SE", year=1398, mileage=1, price=300_000_000)
    Listing.objects.create(source_id="a", description="یک لکه رنگ", **common)
    Listing.objects.create(source_id="b", description="", **common)
    Listing.objects.create(source="divar", source_id="c", raw_name="Pride 131 SE-new", title="قسطی", exclusion="instalment",
                           description="فروش نقدی", year=1398, mileage=1, price=300_000_000)


def test_trim_matched_once_per_raw_name_and_written_back(data, fake_llm):
    stats = enrich()
    assert stats["trims_asked"] == 1 and stats["trims_matched"] == 1
    assert Listing.objects.filter(vehicle_id="pride-131-se").count() == 3
    alias = VehicleAlias.objects.get(source="divar")
    assert (alias.method, alias.vehicle_id) == ("llm", "pride-131-se")
    # Closed list: the schema only allows candidate IDs of the matched make, or "none".
    assert "pride-131-sx" in fake_llm[0]


def test_condition_read_and_keyword_flag_confirmed(data, fake_llm):
    enrich()
    assert Listing.objects.get(source_id="a").body_condition == "minor"
    assert Listing.objects.get(source_id="c").exclusion == ""  # LLM says it's a normal used-car ad
    assert Listing.objects.get(source_id="b").body_condition == ""  # no description: nothing to read


def test_no_credentials_skips(data, settings):
    settings.ANTHROPIC_API_KEY = ""
    assert enrich()["skipped"] is True
