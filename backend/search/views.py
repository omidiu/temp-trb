from rest_framework.response import Response
from rest_framework.views import APIView

from market.models import Offer
from market.serializers import OfferSerializer

from .intent import CONDITION_LABELS, FAMILIES, NEEDS, PREFERENCES, empty_intent, resolve
from .parse import parse


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


class SearchView(APIView):
    def post(self, request):
        intent = resolve(explicit_intent(request.data.get("intent")))
        c = intent["constraints"]
        offers = Offer.objects.select_related("vehicle").prefetch_related("listings")
        if c.get("max_price") is not None:
            offers = offers.filter(price__lte=c["max_price"])
        offers = offers.order_by("price")
        return Response({"intent": intent, "results": OfferSerializer(offers[:100], many=True).data})
