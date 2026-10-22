import os
import tempfile
from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from dj_list_filterable_by_grab_bag.models import (
    Property,
    PropertySet,
    PropertyValue,
)


class ImportPropertyCsvTests(TestCase):
    def setUp(self):
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp_dir.cleanup)

    def write_csv(self, content, encoding='utf-8'):
        path = os.path.join(self.tmp_dir.name, 'import.csv')
        with open(path, 'w', encoding=encoding, newline='') as f:
            f.write(content)
        return path

    def run_import(self, path):
        stdout = StringIO()
        call_command('import_property_csv', path, stdout=stdout)
        return stdout.getvalue()

    def set_values(self, set_name):
        property_set = PropertySet.objects.get(name=set_name)
        return sorted(str(v) for v in property_set.property_values.all())

    def test_imports_rows_as_properties_and_columns_as_sets(self):
        path = self.write_csv(
            'property,Set A,Set B\n'
            'Color,Red,Blue\n'
            'Size,Small,Large\n'
        )

        self.run_import(path)

        self.assertEqual(
            sorted(Property.objects.values_list('name', flat=True)),
            ['Color', 'Size'],
        )
        self.assertEqual(
            sorted(PropertySet.objects.values_list('name', flat=True)),
            ['Set A', 'Set B'],
        )
        self.assertEqual(self.set_values('Set A'), ['Color: Red', 'Size: Small'])
        self.assertEqual(self.set_values('Set B'), ['Color: Blue', 'Size: Large'])

    def test_empty_cells_create_no_value_and_are_excluded_from_set(self):
        path = self.write_csv(
            'property,Set A,Set B\n'
            'Color,Red,Blue\n'
            'Size,,Large\n'
            'Weight,  ,\n'
        )

        self.run_import(path)

        self.assertEqual(self.set_values('Set A'), ['Color: Red'])
        self.assertEqual(self.set_values('Set B'), ['Color: Blue', 'Size: Large'])
        self.assertEqual(PropertyValue.objects.count(), 3)
        self.assertFalse(
            PropertyValue.objects.filter(property__name='Weight').exists()
        )

    def test_same_value_in_two_sets_shares_one_property_value(self):
        path = self.write_csv(
            'property,Set A,Set B\n'
            'Color,Red,Red\n'
        )

        self.run_import(path)

        property_value = PropertyValue.objects.get()
        self.assertEqual(str(property_value), 'Color: Red')
        self.assertEqual(property_value.property_sets.count(), 2)

    def test_reimport_does_not_duplicate(self):
        path = self.write_csv(
            'property,Set A,Set B\n'
            'Color,Red,Blue\n'
            'Size,,Large\n'
        )

        self.run_import(path)
        output = self.run_import(path)

        self.assertEqual(Property.objects.count(), 2)
        self.assertEqual(PropertySet.objects.count(), 2)
        self.assertEqual(PropertyValue.objects.count(), 3)
        self.assertEqual(self.set_values('Set B'), ['Color: Blue', 'Size: Large'])
        self.assertIn('properties: 0 created, 2 reused', output)
        self.assertIn('property sets: 0 created, 2 reused', output)
        self.assertIn('property values: 0 created, 3 reused', output)

    def test_reuses_existing_records(self):
        color = Property.objects.create(name='Color')
        red = PropertyValue.objects.create(property=color, value='Red')
        set_a = PropertySet.objects.create(name='Set A')
        path = self.write_csv(
            'property,Set A\n'
            'Color,Red\n'
        )

        self.run_import(path)

        self.assertEqual(Property.objects.get(), color)
        self.assertEqual(PropertySet.objects.get(), set_a)
        self.assertEqual(list(set_a.property_values.all()), [red])

    def test_skips_rows_without_a_property_name(self):
        path = self.write_csv(
            'property,Set A\n'
            'Color,Red\n'
            ',Orphan\n'
            '\n'
        )

        self.run_import(path)

        self.assertEqual(
            list(Property.objects.values_list('name', flat=True)), ['Color']
        )
        self.assertEqual(self.set_values('Set A'), ['Color: Red'])

    def test_skips_columns_without_a_heading(self):
        path = self.write_csv(
            'property,Set A,,Set C\n'
            'Color,Red,Ignored,Green\n'
        )

        self.run_import(path)

        self.assertEqual(
            sorted(PropertySet.objects.values_list('name', flat=True)),
            ['Set A', 'Set C'],
        )
        self.assertFalse(PropertyValue.objects.filter(value='Ignored').exists())
        self.assertEqual(self.set_values('Set C'), ['Color: Green'])

    def test_strips_whitespace(self):
        path = self.write_csv(
            'property, Set A \n'
            ' Color , Red \n'
        )

        self.run_import(path)

        self.assertEqual(self.set_values('Set A'), ['Color: Red'])

    def test_handles_utf8_bom(self):
        path = self.write_csv(
            'property,Set A\n'
            'Color,Red\n',
            encoding='utf-8-sig',
        )

        self.run_import(path)

        self.assertEqual(self.set_values('Set A'), ['Color: Red'])

    def test_missing_file_raises_command_error(self):
        path = os.path.join(self.tmp_dir.name, 'missing.csv')

        with self.assertRaisesMessage(CommandError, 'Could not read'):
            self.run_import(path)

    def test_empty_file_raises_command_error(self):
        path = self.write_csv('')

        with self.assertRaisesMessage(CommandError, 'is empty'):
            self.run_import(path)
