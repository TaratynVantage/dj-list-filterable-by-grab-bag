from django.db import models


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


class PropertySet(models.Model):
    name = models.CharField(max_length=255)
    property_values = models.ManyToManyField(
        PropertyValue, related_name='property_sets', blank=True
    )

    def __str__(self):
        return self.name


class Item(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    property_set = models.ForeignKey(
        PropertySet, on_delete=models.PROTECT, related_name='items'
    )

    def __str__(self):
        return self.name
