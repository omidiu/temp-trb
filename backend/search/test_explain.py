import pytest

from llm import client as llm
from search.explain import explain, fact_sheet, grounded, template
from search.intent import empty_intent, resolve
from search.ranking import rank
from search.test_ranking import market  # noqa: F401  (fixture)


def _intent():
    i = empty_intent()
    i["constraints"]["max_price"] = 800_000_000
    i["needs"] = [{"key": "family", "off": []}]
    return resolve(i)


def test_template_and_fact_sheet(market):
    rows = rank(_intent())["main"][:3]
    sheet = fact_sheet(_intent(), rows)
    assert sheet["top_pick"]["name"] == "دنا پلاس"
    text = template(sheet)
    assert "دنا پلاس" in text and grounded(text, sheet)


def test_grounding_rejects_invented_numbers(market):
    rows = rank(_intent())["main"][:3]
    sheet = fact_sheet(_intent(), rows)
    assert not grounded("دنا پلاس ۳۵٪ ارزان‌تر است.", sheet)
    assert not grounded("سمند هم گزینهٔ خوبی است.", sheet)


@pytest.mark.parametrize("llm_text,method", [
    ("«دنا پلاس» بهترین گزینه است چون زیر قیمت است و بدنه سدان دارد.", "llm"),
    ("«دنا پلاس» ۹۹ میلیون زیر قیمت است.", "template_after_llm_rejected"),
])
def test_llm_text_is_checked(market, llm_text, method):
    llm.use_fake(lambda *a: llm_text)
    try:
        out = explain(_intent(), rank(_intent())["main"][:3])
    finally:
        llm.use_fake(None)
    assert out["method"] == method
    if method == "llm":
        assert out["text"] == llm_text
