from django.core.management.base import BaseCommand
from django.apps import apps
import csv


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('--csv', required=True, help="file path")
        parser.add_argument('--model', required=True, help="model name")

    def handle(self, *args, **options):
        file_path = options['csv']
        app_name = "psims"
        model = apps.get_model(app_name, options['model'])
        with open(file_path, 'r') as csv_file:
            reader = csv.reader(csv_file, delimiter=',', quotechar='|')
            header = next(reader)
            for row in reader:
                object_dict = {key: value for key, value in zip(header, row)}
                model.objects.get_or_create(**object_dict)
