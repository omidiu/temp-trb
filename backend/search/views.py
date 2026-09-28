from rest_framework.response import Response
from rest_framework.views import APIView

from market.models import Offer
from market.serializers import OfferSerializer


class SearchView(APIView):
    def post(self, request):
        constraints = (request.data.get("intent") or {}).get("constraints") or {}
        offers = Offer.objects.select_related("vehicle").prefetch_related("listings")
        if (max_price := constraints.get("max_price")) is not None:
            offers = offers.filter(price__lte=max_price)
        offers = offers.order_by("price")
        return Response({"results": OfferSerializer(offers, many=True).data})
