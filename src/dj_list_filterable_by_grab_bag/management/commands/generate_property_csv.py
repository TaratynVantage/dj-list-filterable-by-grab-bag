import csv
import io
import random

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = (
        'Generate a fake CSV for import_property_csv: one row per property '
        'and one column per property set, filled with Faker values.'
    )

    def add_arguments(self, parser):
        parser.add_argument('--properties', type=int, required=True,
                            help='Number of property rows.')
        parser.add_argument('--columns', type=int, required=True,
                            help='Number of property set columns.')
        parser.add_argument('--output', default='-',
                            help='File to write to; "-" (default) is stdout.')
        parser.add_argument('--empty-ratio', type=float, default=0.2,
                            help='Chance (0-1) that a cell is left empty.')
        parser.add_argument('--seed', type=int,
                            help='Seed for reproducible output.')

    def handle(self, *args, properties, columns, output, empty_ratio, seed,
               **options):
        # Faker is a dev dependency, so only require it when this runs.
        try:
            from faker import Faker
            from faker.exceptions import UniquenessException
        except ImportError:
            raise CommandError('Faker is not installed; run `uv sync`.')

        if properties < 1:
            raise CommandError('--properties must be at least 1')
        if columns < 1:
            raise CommandError('--columns must be at least 1')
        if not 0 <= empty_ratio <= 1:
            raise CommandError('--empty-ratio must be between 0 and 1')

        fake = Faker()
        fake.seed_instance(seed)
        rng = random.Random(seed)

        try:
            set_names = [fake.unique.catch_phrase() for _ in range(columns)]
            property_names = [
                fake.unique.word().title() for _ in range(properties)
            ]
        except UniquenessException:
            raise CommandError(
                'Faker ran out of unique names; use fewer properties or columns.'
            )

        buffer = io.StringIO()
        writer = csv.writer(buffer, lineterminator='\n')
        writer.writerow(['property'] + set_names)
        for property_name in property_names:
            # A small pool per property so values repeat across columns.
            value_pool = fake.words(nb=rng.randint(3, 5), unique=True)
            writer.writerow([property_name] + [
                '' if rng.random() < empty_ratio else rng.choice(value_pool)
                for _ in range(columns)
            ])

        if output == '-':
            self.stdout.write(buffer.getvalue(), ending='')
            return

        try:
            with open(output, 'w', encoding='utf-8', newline='') as f:
                f.write(buffer.getvalue())
        except OSError as e:
            raise CommandError(f'Could not write {output}: {e}')
        self.stderr.write(self.style.SUCCESS(
            f'Wrote {properties} properties x {columns} columns to {output}'
        ))
