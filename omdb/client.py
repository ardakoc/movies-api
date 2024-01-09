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