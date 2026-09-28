from rest_framework import serializers

from catalog.models import Vehicle

from .models import Listing, Offer


class VehicleSerializer(serializers.ModelSerializer):
    name_fa = serializers.CharField(read_only=True)

    class Meta:
        model = Vehicle
        fields = [
            "id", "make_fa", "model_fa", "trim_fa", "name_fa", "body_type", "engine_cc",
            "gearbox", "fuel_type", "fuel_consumption", "airbags", "abs", "esc",
        ]


class ListingLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Listing
        fields = ["source", "url", "price"]


class OfferSerializer(serializers.ModelSerializer):
    vehicle = VehicleSerializer(read_only=True)
    sources = serializers.SerializerMethodField()

    class Meta:
        model = Offer
        fields = [
            "id", "title", "vehicle", "year", "mileage", "price", "gearbox", "fuel_type",
            "body_condition", "exclusion", "city", "posted_at", "image_url",
            "fair_price", "p_cheaper", "verdict", "confidence", "sources",
        ]

    def get_sources(self, offer):
        return ListingLinkSerializer(offer.listings.all(), many=True).data
