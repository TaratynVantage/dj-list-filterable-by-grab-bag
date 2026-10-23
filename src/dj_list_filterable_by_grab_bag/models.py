from __future__ import annotations

from django.db import models
from django.db.models import QuerySet, Prefetch


class Property(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class PropertyValue(models.Model):
    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='values'
    )
    value = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.property}: {self.value}'


class PropertyValuePropertySetThroughModel(models.Model):
    property_value = models.ForeignKey(
        PropertyValue, on_delete=models.CASCADE, related_name='property_values'
    )
    property_set = models.ForeignKey(
        'PropertySet', on_delete=models.CASCADE, related_name='propertysets'
    )

    class Meta:
        unique_together = (
            ('property_value', 'property_set',),
        )
        indexes = [
            models.Index(fields=['property_set', 'property_value', ]),
        ]


class PropertySet(models.Model):
    name = models.CharField(max_length=255)
    property_values = models.ManyToManyField(
        PropertyValue, related_name='property_sets', blank=True, through=PropertyValuePropertySetThroughModel
    )

    def __str__(self):
        return self.name


class ItemManager(models.Manager):
    def get_items_from_property_value(self, query: str) -> QuerySet:
        items: QuerySet[Item] = (
            self.get_queryset()
            .prefetch_related(Prefetch(
                'property_set__property_values',
                queryset=PropertyValue.objects
                .select_related('property')
            ))
            .order_by('name')
        )
        if query:
            # distinct() because an item matches once per matching value.
            items = (items
                     .filter(property_set__property_values__value__icontains=query)
                     .distinct()
                     )
        return items


class Item(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    property_set = models.ForeignKey(
        PropertySet, on_delete=models.PROTECT, related_name='items'
    )

    objects = ItemManager()

    def __str__(self):
        return self.name
