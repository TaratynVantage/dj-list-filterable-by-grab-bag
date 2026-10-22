import csv
from collections import Counter

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from dj_list_filterable_by_grab_bag.models import (
    Item,
    Property,
    PropertySet,
    PropertyValue,
)


class Command(BaseCommand):
    help = (
        'Import a CSV where each row is a Property (named by the first column), '
        'each other column heading is a PropertySet, and each non-empty cell is '
        'a PropertyValue that belongs to that column\'s PropertySet. Each '
        'column also gets an Item with the same name as its PropertySet.'
    )

    def add_arguments(self, parser):
        parser.add_argument('csv_path')

    def handle(self, *args, csv_path, **options):
        try:
            with open(csv_path, encoding='utf-8-sig', newline='') as f:
                rows = list(csv.reader(f))
        except OSError as e:
            raise CommandError(f'Could not read {csv_path}: {e}')

        if not rows:
            raise CommandError(f'{csv_path} is empty')

        created = Counter()
        reused = Counter()

        def track(kind, was_created):
            (created if was_created else reused)[kind] += 1

        with transaction.atomic():
            # Keep one entry per column so cells line up; blank headings are None.
            property_sets = []
            for set_name in rows[0][1:]:
                set_name = set_name.strip()
                if not set_name:
                    property_sets.append(None)
                    continue
                property_set, was_created = PropertySet.objects.get_or_create(
                    name=set_name
                )
                track('property sets', was_created)
                property_sets.append(property_set)

                # Price isn't in the CSV; new items start at 0 and existing
                # items keep their price.
                _, was_created = Item.objects.get_or_create(
                    name=set_name,
                    property_set=property_set,
                    defaults={'price': 0},
                )
                track('items', was_created)

            for row in rows[1:]:
                if not row or not row[0].strip():
                    continue
                prop, was_created = Property.objects.get_or_create(
                    name=row[0].strip()
                )
                track('properties', was_created)

                for property_set, cell in zip(property_sets, row[1:]):
                    value = cell.strip()
                    if property_set is None or not value:
                        continue
                    property_value, was_created = (
                        PropertyValue.objects.get_or_create(
                            property=prop, value=value
                        )
                    )
                    track('property values', was_created)
                    property_set.property_values.add(property_value)

        for kind in ('properties', 'property sets', 'property values', 'items'):
            self.stdout.write(self.style.SUCCESS(
                f'{kind}: {created[kind]} created, {reused[kind]} reused'
            ))
