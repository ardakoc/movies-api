from typing import Any, Optional
from django.core.management.base import BaseCommand, CommandParser

from movies.omdb_integration import search_and_save


class Command(BaseCommand):
    help = 'Search OMDb and populates the database with results'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('search', nargs='+')

    def handle(self, *args: Any, **options: Any) -> str or None:
        search = ' '.join(options['search'])
        search_and_save(search)
