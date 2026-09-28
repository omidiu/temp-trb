import pytest
from django.core.management import call_command
from rest_framework.test import APIClient


@pytest.fixture
def sample(db):
    call_command("load_sample_offers", stdout=None)


def test_budget_constraint_filters_offers(sample):
    res = APIClient().post("/api/search", {"intent": {"constraints": {"max_price": 500_000_000}}}, format="json")
    prices = [o["price"] for o in res.json()["results"]]
    assert prices and all(p <= 500_000_000 for p in prices)
    assert len(prices) == 3


def test_no_constraints_returns_everything(sample):
    res = APIClient().post("/api/search", {"intent": {}}, format="json")
    assert len(res.json()["results"]) == 6
