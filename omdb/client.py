import logging
import requests

from django.conf import settings

logger = logging.getLogger(__name__)
OMDB_API_URL = settings.API_URL


class OmdbMovie:
    """
    To represent movie data coming back from OMDb API
    and transform to Python types.
    """

    def __init__(self, data):
        """
        The data that raw JSON returned from OMDb API.
        """
        self.data = data

    def check_for_detail_data_key(self, key):
        """
        Some keys are only in the detail response. Raise an exception
        if the key is not found.
        """
        if key not in self.data:
            raise AttributeError(
                f'{key} is not in data, please make sure this is a detail response.'
            )

    @property
    def imdb_id(self):
        return self.data['imdbID']

    @property
    def title(self):
        return self.data['Title']

    @property
    def year(self):
        return int(self.data['Year'])
    
    @property
    def runtime_minutes(self):
        self.check_for_detail_data_key('Runtime')
        runtime_minutes, units = self.data['Runtime'].split(' ')
        if units != 'min':
            raise ValueError(f"Expected units 'min' for runtime. Got {units}")        
        return int(runtime_minutes)

    @property
    def genres(self):
        self.check_for_detail_data_key('Genre')
        return self.data['Genre'].split(', ')

    @property
    def plot(self):
        self.check_for_detail_data_key('Plot')
        return self.data['Plot']
    

class OmbdClient:
    def __init__(self, api_key):
        self.api_key = api_key

    def make_request(self, params):
        """
        Make a GET request to the API.
        """
        params['apikey'] = self.api_key # Automatically add the api key to the params.

        response = requests.get(OMDB_API_URL, params=params)
        response.raise_for_status()
        return response
    
    def get_by_imdb_id(self, imdb_id):
        """
        Get a movie by its IMDB ID.
        """
        logger.info(f'Fetching detail for IMDB ID {imdb_id}')
        response = self.make_request({'i': imdb_id})
        return OmdbMovie(response.json())

    def search(self, search):
        """
        Search for movies by title.

        This is a generator so all results from all pages will be iterated across.
        """
        page = 1
        seen_results = 0
        total_results = None

        logger.info(f'Performing a search for {search}')

        while True:
            logger.info(f'Fetching page {page}')
            response = self.make_request({'s': search, 'type': 'movie', 'page': str(page)})
            response_body = response.json()
            if total_results is None:
                total_results = int(response_body['totalResults'])

            for movie in response_body['Search']:
                seen_results += 1
                yield OmdbMovie(movie)

            if seen_results >= total_results:
                break

            page += 1
