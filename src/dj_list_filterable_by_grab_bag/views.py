import logging

from django.shortcuts import render

from dj_list_filterable_by_grab_bag.models import Item

logger = logging.getLogger(__name__)


def home(request):
    return render(request, 'dj_list_filterable_by_grab_bag/home.html')


def item_list(request):
    query = request.GET.get('q', '').strip()
    items = Item.objects.get_items_from_property_value(query)
    logger.critical(items.explain(analyze=True))
    return render(
        request,
        'dj_list_filterable_by_grab_bag/_item_list.html',
        {'items': items, 'query': query},
    )
