import logging
from typing import Any, Optional

from django.core.management.base import BaseCommand, CommandParser

from movies.models import Movie
from movies.omdb_integration import fill_movie_details

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Search OMDb and populates the database with results.'

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument('imdb_id', nargs=1)

    def handle(self, *args: Any, **options: Any) -> str or None:
        try:
            movie = Movie.objects.get(imdb_id=options['imdb_id'][0])
        except Movie.DoesNotExist:
            logger.error(f'Movie with IMDB ID {options["imdb_id"][0]} was not found.')
            return
        fill_movie_details(movie)
