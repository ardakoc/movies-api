import logging
import re
from datetime import timedelta

from django.utils.timezone import now

from .models import Genre, Movie, SearchTerm
from ..omdb.django_client import get_client_from_settings

logger = logging.getLogger()

def get_or_create_genres(genre_names):
    """
    Accepts a list of genre names and yields a Genre object for each of them.
    """
    for genre_name in genre_names:
        genre, created = Genre.objects.get_or_create(name=genre_name)
        yield genre

def fill_movie_details(movie):
    """
    Accepts a Movie object and then queries the OMDb API to fill in the missing data.
    """
    if movie.is_full_record:
        # If the movie already has a 'full_record', it means it's already filled. No
        # need for anything else.
        logger.warning(f'{movie.title} is already a full record.')
        return
    # Otherwise instantiate an OmdbClient,
    omdb_client = get_client_from_settings()
    # fetch the details,
    movie_details = omdb_client.get_by_imdb_id(movie.imdb_id)
    # then update,
    movie.title = movie_details.title
    movie.year = movie_details.year
    movie.plot = movie_details.plot
    movie.runtime_minutes = movie_details.runtime_minutes
    movie.genres.clear()
    for genre in get_or_create_genres(movie_details.genres):
        movie.genres.add(genre)
    movie.is_full_record = True
    # and save the Movie.
    movie.save()

def search_and_save(search):
    """
    Perform a search for search_term against the API, but only if it hasn't been
    searched in the past 24 hours. Save each result to the local db as a partial
    record.
    """
    # Replace multiple spaces with single spaces, and lowercase the search
    normalized_search_term = re.sub(r'\s+', ' ', search.lower())

    search_term, created = SearchTerm.objects.get_or_create(term=normalized_search_term)
    if not created and (search_term.last_search > now() - timedelta(days=1)):
        # Don't search as it has been searched recently.
        logger.warning(f'''
            Search for {normalized_search_term} was performed in the past 24 hours so
            not searching again.
        ''')
        return
    # Otherwise instantiate an OmdbClient,
    omdb_client = get_client_from_settings()

    # perform a search,
    for omdb_movie in omdb_client.search(search):
        logger.info(f'Saving movie: {omdb_movie.title} / {omdb_movie.imdb_id}')
        # with each result being saved to the local db.
        movie, created = Movie.objects.get_or_create(
            imdb_id=omdb_movie.imdb_id,
            defaults={
                'title': omdb_movie.title,
                'year': omdb_movie.year,
            },
        )
        if created:
            logger.info(f'Movie created: {movie.title}')

    search_term.save()
