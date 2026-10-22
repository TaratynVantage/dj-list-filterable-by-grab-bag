from django.contrib import admin

from dj_list_filterable_by_grab_bag.models import (
    Item,
    Property,
    PropertySet,
    PropertyValue,
)


class PropertyValueInline(admin.TabularInline):
    model = PropertyValue
    extra = 1


class ItemInline(admin.TabularInline):
    model = Item
    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):

    list_display = ('name',)
    ordering = ('name',)
    search_fields = ('name',)
    inlines = (PropertyValueInline,)


@admin.register(PropertyValue)
class PropertyValueAdmin(admin.ModelAdmin):
    list_display = ('value', 'property')
    ordering = ('property__name', 'value')
    list_filter = ('property',)
    list_select_related = ('property',)
    search_fields = ('value', 'property__name')
    autocomplete_fields = ('property',)


@admin.register(PropertySet)
class PropertySetAdmin(admin.ModelAdmin):
    list_display = ('name',)
    ordering = ('name',)
    search_fields = ('name',)
    autocomplete_fields = ('property_values',)
    inlines = (ItemInline,)


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'property_set')
    ordering = ('name',)
    list_filter = ('property_set',)
    list_select_related = ('property_set',)
    search_fields = ('name', 'property_set__name')
    autocomplete_fields = ('property_set',)
