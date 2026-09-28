from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from market.models import ModelStats, Offer
from market.serializers import OfferSerializer

from .intent import CONDITION_LABELS, FAMILIES, NEEDS, PREFERENCES, empty_intent, resolve
from .parse import parse
from .ranking import rank
from .reasons import one_line
from .relax import suggestions


def explicit_intent(data) -> dict:
    """Accept a (possibly partial) explicit Intent from the client."""
    intent = empty_intent()
    raw = data or {}
    intent["text"] = raw.get("text", "")
    intent["constraints"].update({k: v for k, v in (raw.get("constraints") or {}).items() if k in intent["constraints"]})
    intent["preferences"] = [p for p in raw.get("preferences") or [] if p.get("key") in PREFERENCES]
    intent["needs"] = [n for n in raw.get("needs") or [] if n.get("key") in NEEDS]
    intent["spans"] = raw.get("spans") or {}
    intent["source"] = raw.get("source", "edited")
    return intent


class IntentParseView(APIView):
    def post(self, request):
        return Response(resolve(parse(request.data.get("text", ""))))


class NeedsView(APIView):
    def get(self, request):
        return Response({
            "needs": {k: {"label": v["label"], "recipe": [{"key": p, "strength": s} for p, s in v["recipe"]]}
                      for k, v in NEEDS.items()},
            "preferences": PREFERENCES,
            "families": FAMILIES,
            "conditions": CONDITION_LABELS,
        })


def serialize_ranked(rows, stats, limit=60):
    out = []
    for r in rows[:limit]:
        data = OfferSerializer(r["offer"]).data
        data.update(score=r["score"], deal=r["deal"], breakdown=r["breakdown"], reason=one_line(r, stats))
        out.append(data)
    return out


class SearchView(APIView):
    def post(self, request):
        intent = resolve(explicit_intent(request.data.get("intent")))
        ranked = rank(intent)
        stats = {m.model_key: m for m in ModelStats.objects.all()}
        return Response({
            "intent": intent,
            "top_pick": ranked["top_pick"],
            "count": len(ranked["main"]),
            "results": serialize_ranked(ranked["main"], stats),
            "over_budget": serialize_ranked(ranked["over_budget"], stats, limit=20),
            "relaxations": suggestions(intent["constraints"]) if not ranked["main"] else [],
        })


class OfferDetailView(APIView):
    def get(self, request, pk):
        offer = get_object_or_404(Offer.objects.select_related("vehicle").prefetch_related("listings"), pk=pk)
        comps = Offer.objects.filter(pk__in=offer.comparable_ids).select_related("vehicle")
        stats = ModelStats.objects.filter(model_key=offer.vehicle.family).first()
        data = OfferSerializer(offer).data
        data["comparables"] = [
            {"id": c.id, "price": c.price, "year": c.year, "mileage": c.mileage,
             "body_condition": c.body_condition, "name_fa": c.vehicle.name_fa}
            for c in sorted(comps, key=lambda c: c.price)
        ]
        data["model_stats"] = {"popularity": stats.popularity, "depreciation": stats.depreciation,
                               "offer_count": stats.offer_count} if stats else None
        data["listings"] = [{"source": l.source, "url": l.url, "price": l.price, "title": l.title,
                             "description": l.description[:600]} for l in offer.listings.all()]
        return Response(data)
