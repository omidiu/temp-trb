import pytest

from catalog.models import Vehicle
from market.models import Listing, Offer
from market.offers import rebuild_offers


@pytest.fixture
def vehicle(db):
    return Vehicle.objects.create(id="quick-manualr", make="quick", make_fa="کوییک", model="manualr",
                                  model_fa="کوییک R", family="quick", gearbox="manual")


def mk(source, sid, mileage, price, cond="clean", year=1400, **kw):
    return Listing.objects.create(source=source, source_id=sid, title="کوییک", vehicle_id="quick-manualr",
                                  year=year, mileage=mileage, price=price, body_condition=cond, **kw)


def test_cross_posted_car_merges_at_lowest_price_with_bama_attributes(vehicle):
    mk("divar", "d1", 55_000, 700_000_000)
    mk("bama", "b1", 55_400, 690_000_000, image_url="https://img")
    s = rebuild_offers()
    assert (s["offers"], s["merged"]) == (1, 1)
    offer = Offer.objects.get()
    assert offer.price == 690_000_000 and offer.image_url == "https://img"
    assert offer.listings.count() == 2


@pytest.mark.parametrize("second", [
    dict(mileage=58_000, price=700_000_000),                 # mileage too far
    dict(mileage=55_000, price=760_000_000),                 # price > 3% apart
    dict(mileage=55_000, price=700_000_000, cond="minor"),   # different condition class
    dict(mileage=55_000, price=700_000_000, year=1401),      # different model year
])
def test_different_cars_stay_apart(vehicle, second):
    mk("divar", "d1", 55_000, 700_000_000)
    mk("bama", "b1", **second)
    assert rebuild_offers()["offers"] == 2
