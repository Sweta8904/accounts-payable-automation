
from django.db import transaction
from rest_framework import serializers

from .models import (
    PurchaseOrder,
    PurchaseOrderItem,
    GoodsReceiptNote,
    GoodsReceiptItem,
)


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseOrderItem
        fields = ["id", "description", "quantity", "unit_price", "tax_rate"]
        read_only_fields = ["id"]


class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True)
    vendor_name = serializers.CharField(source="vendor.name", read_only=True)
    total_amount = serializers.DecimalField(
        max_digits=15, decimal_places=2, read_only=True
    )

    class Meta:
        model = PurchaseOrder
        fields = [
            "id", "po_number", "vendor", "vendor_name",
            "order_date", "expected_delivery_date", "status",
            "currency", "notes", "items", "total_amount",
            "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    def validate_items(self, items):
        if not items:
            raise serializers.ValidationError(
                "A purchase order must contain at least one item."
            )

        for item in items:
            if item["quantity"] <= 0 or item["unit_price"] < 0:
                raise serializers.ValidationError(
                    "Quantity must be positive and unit price cannot be negative."
                )
        return items

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        purchase_order = PurchaseOrder.objects.create(**validated_data)

        for item in items_data:
            PurchaseOrderItem.objects.create(
                purchase_order=purchase_order, **item
            )

        return purchase_order

    @transaction.atomic
    def update(self, instance, validated_data):
        items_data = validated_data.pop("items", None)

        for key, value in validated_data.items():
            setattr(instance, key, value)

        instance.save()

        if items_data is not None:
            if instance.goods_receipts.exists():
                raise serializers.ValidationError(
                    "Cannot replace PO items after goods have been received."
                )

            instance.items.all().delete()

            for item in items_data:
                PurchaseOrderItem.objects.create(
                    purchase_order=instance, **item
                )

        return instance


class GoodsReceiptItemSerializer(serializers.ModelSerializer):
    description = serializers.CharField(
        source="purchase_order_item.description", read_only=True
    )

    class Meta:
        model = GoodsReceiptItem
        fields = [
            "id", "purchase_order_item", "description",
            "received_quantity", "accepted_quantity", "notes",
        ]
        read_only_fields = ["id"]

    def validate(self, attrs):
        received = attrs.get(
            "received_quantity",
            getattr(self.instance, "received_quantity", None)
        )
        accepted = attrs.get(
            "accepted_quantity",
            getattr(self.instance, "accepted_quantity", None)
        )

        if received is not None and accepted is not None:
            if received <= 0 or accepted < 0 or accepted > received:
                raise serializers.ValidationError(
                    "Received quantity must be positive; accepted quantity "
                    "must be between zero and received quantity."
                )
        return attrs


class GoodsReceiptNoteSerializer(serializers.ModelSerializer):
    items = GoodsReceiptItemSerializer(many=True)
    po_number = serializers.CharField(
        source="purchase_order.po_number", read_only=True
    )

    class Meta:
        model = GoodsReceiptNote
        fields = [
            "id", "grn_number", "purchase_order", "po_number",
            "received_date", "status", "notes", "items", "created_at",
        ]
        read_only_fields = ["id", "created_at"]

    @transaction.atomic
    def create(self, validated_data):
        items_data = validated_data.pop("items")
        purchase_order = validated_data["purchase_order"]

        if purchase_order.status in ["DRAFT", "CANCELLED", "CLOSED"]:
            raise serializers.ValidationError(
                "GRNs can only be recorded against an active approved PO."
            )

        for item in items_data:
            if item["purchase_order_item"].purchase_order_id != purchase_order.id:
                raise serializers.ValidationError(
                    "Every GRN item must belong to the selected purchase order."
                )

        grn = GoodsReceiptNote.objects.create(**validated_data)

        for item in items_data:
            GoodsReceiptItem.objects.create(grn=grn, **item)

        update_purchase_order_status(purchase_order)
        return grn


def update_purchase_order_status(purchase_order):
    items = purchase_order.items.all()

    if not items.exists():
        return

    all_received = True
    any_received = False

    for item in items:
        accepted = sum(
            (
                receipt.accepted_quantity
                for receipt in item.receipts.filter(
                    grn__status__in=["RECEIVED", "PARTIAL"]
                )
            ),
            start=0
        )

        if accepted > 0:
            any_received = True

        if accepted < item.quantity:
            all_received = False

    if all_received:
        purchase_order.status = PurchaseOrder.Status.RECEIVED
    elif any_received:
        purchase_order.status = PurchaseOrder.Status.PARTIALLY_RECEIVED
    else:
        purchase_order.status = PurchaseOrder.Status.APPROVED

    purchase_order.save(update_fields=["status", "updated_at"])
