from django.db.models import Prefetch
from django.shortcuts import render

from dj_list_filterable_by_grab_bag.models import Item, PropertyValue


def home(request):
    return render(request, 'dj_list_filterable_by_grab_bag/home.html')


def item_list(request):
    items = (
        Item.objects
        .select_related('property_set')
        .prefetch_related(Prefetch(
            'property_set__property_values',
            queryset=PropertyValue.objects
            .select_related('property')
            .order_by('property__name', 'value'),
        ))
        .order_by('name')
    )
    return render(
        request,
        'dj_list_filterable_by_grab_bag/_item_list.html',
        {'items': items},
    )
