"""LLM steps of normalization: only what the rules and alias table can't settle.

1. Trim matching: pick one trim from a closed list of catalog IDs (or none). One call per
   distinct (Source, raw name); the answer is written back to the alias table as method=llm.
2. Condition and exclusion: read the ad text when structured fields are missing or a keyword
   flag needs confirming.
"""

import json
import logging

from catalog.models import Vehicle, VehicleAlias
from llm import client as llm

from .models import BodyCondition, Exclusion, Listing
from .normalize import alias_key

log = logging.getLogger(__name__)

# First word of a Source's raw name → catalog make
MAKE_HINTS = {
    "peugeot": "peugeot", "پژو": "peugeot", "pride": "pride", "پراید": "pride", "saipa": "pride",
    "tiba": "tiba", "تیبا": "tiba", "dena": "dena", "دنا": "dena", "samand": "samand", "سمند": "samand",
    "quick": "quick", "کوییک": "quick", "shahin": "shahin", "شاهین": "shahin",
}

MATCH_SYSTEM = (
    "You match Iranian used-car ads to a canonical trim catalog. Answer only from the candidate "
    "list. Trim names differ across sites: 'تیپ ۲' = type2, 'SD'/'صندوقدار' = sedan, CNG/دوگانه‌سوز = "
    "bi-fuel. If the ad only names the model and several trims fit, or nothing fits, answer 'none'."
)

CONDITION_SYSTEM = (
    "You read Persian used-car ads. Classify body condition: clean = no paint (scratches or "
    "paintless dent repair are still clean); minor = one or two painted spots or panels; major = "
    "more paint, full/two-tone paint, accident, or chassis damage; unknown = the text doesn't say. "
    "Also say whether the ad is an instalment/leasing offer (the price shown is a down payment), a "
    "pre-sale/allocation permit (حواله/پیش‌فروش) rather than a used car, or neither."
)


def _candidates(raw_name: str) -> list[Vehicle]:
    first = (raw_name or "").split()[0].lower() if raw_name else ""
    make = MAKE_HINTS.get(first)
    qs = Vehicle.objects.all()
    return list(qs.filter(make=make) if make else qs)


def match_trim(source: str, raw_name: str, title: str) -> str | None:
    cands = _candidates(raw_name)
    if not cands:
        return None
    lines = "\n".join(f"- {v.id}: {v.name_fa} ({v.year_from}–{v.year_to}, {v.body_type}, {v.fuel_type})" for v in cands)
    prompt = f"Site: {source}\nSite's model name: {raw_name}\nAd title: {title}\n\nCandidates:\n{lines}"
    schema = {
        "type": "object",
        "properties": {
            "vehicle_id": {"type": "string", "enum": [v.id for v in cands] + ["none"]},
            "reason": {"type": "string"},
        },
        "required": ["vehicle_id", "reason"],
        "additionalProperties": False,
    }
    out = llm.complete_json(prompt, system=MATCH_SYSTEM, schema=schema, max_tokens=300)
    vid = out.get("vehicle_id")
    VehicleAlias.objects.update_or_create(
        source=source, raw_name=alias_key(raw_name),
        defaults={"vehicle_id": vid if vid and vid != "none" else None,
                  "method": VehicleAlias.Method.LLM, "reason": out.get("reason", "")[:500]},
    )
    return vid if vid and vid != "none" else None


def read_condition(title: str, description: str) -> dict:
    schema = {
        "type": "object",
        "properties": {
            "body_condition": {"type": "string", "enum": ["clean", "minor", "major", "unknown"]},
            "offer_type": {"type": "string", "enum": ["used_car", "instalment", "presale"]},
        },
        "required": ["body_condition", "offer_type"],
        "additionalProperties": False,
    }
    prompt = f"Title: {title}\n\nDescription:\n{description[:1500]}"
    return llm.complete_json(prompt, system=CONDITION_SYSTEM, schema=schema, max_tokens=100)


def enrich(limit: int | None = None, stdout=None) -> dict:
    """Run the LLM steps over Listings the rules left incomplete. No-op without credentials."""
    stats = {"trims_asked": 0, "trims_matched": 0, "conditions_read": 0, "skipped": False}
    if not llm.available():
        stats["skipped"] = True
        log.warning("LLM unavailable: skipping LLM normalization")
        return stats
    # 1. Trim matching, once per distinct unmatched raw name without an alias yet.
    known = set(VehicleAlias.objects.values_list("source", "raw_name"))
    todo = {}
    for l in Listing.objects.filter(vehicle__isnull=True).exclude(raw_name=""):
        k = (l.source, alias_key(l.raw_name))
        if k not in known:
            todo.setdefault(k, l)
    for (source, _), l in list(todo.items())[:limit]:
        try:
            vid = match_trim(source, l.raw_name, l.title)
        except llm.LLMUnavailable as e:
            log.warning("trim match failed for %r: %s", l.raw_name, e)
            continue
        stats["trims_asked"] += 1
        if vid:
            stats["trims_matched"] += 1
            Listing.objects.filter(source=source, raw_name=l.raw_name, vehicle__isnull=True).update(vehicle_id=vid)
    # 2. Condition / exclusion from the ad text, for matched Listings only (others are never shown).
    need = Listing.objects.filter(vehicle__isnull=False).filter(body_condition="").exclude(description="")
    flagged = Listing.objects.filter(vehicle__isnull=False, exclusion__in=[Exclusion.INSTALMENT, Exclusion.PRESALE])
    for l in list(need[:limit]) + list(flagged[:limit]):
        try:
            out = read_condition(l.title, l.description)
        except llm.LLMUnavailable as e:
            log.warning("condition read failed for %s: %s", l.pk, e)
            continue
        stats["conditions_read"] += 1
        if not l.body_condition and out["body_condition"] != "unknown":
            l.body_condition = out["body_condition"]
        if l.exclusion in (Exclusion.INSTALMENT, Exclusion.PRESALE):
            l.exclusion = {"used_car": "", "instalment": Exclusion.INSTALMENT, "presale": Exclusion.PRESALE}[out["offer_type"]]
        l.save(update_fields=["body_condition", "exclusion"])
    if stdout:
        stdout.write(json.dumps(stats))
    return stats
