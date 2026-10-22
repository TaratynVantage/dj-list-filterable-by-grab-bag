from django.db.models import Prefetch
from django.db.models.query import QuerySet
from django.shortcuts import render

from dj_list_filterable_by_grab_bag.models import Item, PropertyValue


def home(request):
    return render(request, 'dj_list_filterable_by_grab_bag/home.html')


def item_list(request):
    items: QuerySet[Item] = (
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
    query = request.GET.get('q', '').strip()
    if query:
        # distinct() because an item matches once per matching value.
        items = items.filter(
            property_set__property_values__value__icontains=query
        ).distinct()
    print(items.explain())
    return render(
        request,
        'dj_list_filterable_by_grab_bag/_item_list.html',
        {'items': items, 'query': query},
    )
