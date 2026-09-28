import json
from pathlib import Path

import pytest

from catalog.models import Vehicle, VehicleAlias
from ingest.models import RawListing
from market.normalize import normalize_all
from market.offers import rebuild_offers

FIX = Path(__file__).parent / "fixtures"


@pytest.fixture
def raw(db):
    Vehicle.objects.create(id="peugeot-206ir-type2", make="peugeot", make_fa="پژو", model="206ir",
                           model_fa="پژو 206", trim="type2", trim_fa="تیپ 2", family="peugeot-206ir",
                           body_type="hatchback", gearbox="manual")
    post = json.loads((FIX / "divar_post.json").read_text())
    return RawListing.objects.create(source="divar", source_id="ga4CdHeO", payload={"post": post, "row": {}})


def test_unmatched_without_alias_is_kept_but_not_offered(raw):
    assert normalize_all() == {"total": 1, "matched": 0}
    assert rebuild_offers()["offers"] == 0


def test_alias_match_becomes_offer(raw):
    VehicleAlias.objects.create(source="divar", raw_name="peugeot 206 2", vehicle_id="peugeot-206ir-type2", method="manual")
    assert normalize_all() == {"total": 1, "matched": 1}
    assert rebuild_offers()["offers"] == 1
