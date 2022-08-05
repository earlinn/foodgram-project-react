from csv import DictReader
from pathlib import Path

from django.core.management.base import BaseCommand
from foodgram.settings import BASE_DIR
from recipes.models import Ingredient

ALREDY_LOADED_ERROR_MESSAGE = """
If you need to reload the ingredients data from the CSV file,
first delete the db.sqlite3 file to destroy the database.
Then, run `python manage.py migrate` for a new empty
database with tables"""

DATA_FILE_PATH = Path(
    # Path for local development:
    # Path(BASE_DIR).parent.parent, 'data', 'recipes_ingredient.csv')
    Path(BASE_DIR), 'recipes_ingredient.csv')


class Command(BaseCommand):
    """Loads ingredients data from csv file to database."""

    help = 'Loads ingredients data from csv file to database'

    def handle(self, *args, **options):

        if Ingredient.objects.exists():
            self.stderr.write('Ingredients data already loaded...exiting.')
            self.stderr.write(ALREDY_LOADED_ERROR_MESSAGE)
            return

        self.stdout.write('Loading ingredients data')

        for row in DictReader(open(DATA_FILE_PATH, encoding='utf-8')):
            ingr = Ingredient(
                name=row['name'], measurement_unit=row['measurement_unit'])
            ingr.save()
