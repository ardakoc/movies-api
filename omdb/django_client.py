from django.conf import settings

from .client import OmbdClient


def get_client_from_settings():
    """
    Create an instance of OmdbClient using the API_KEY from the Django settings.
    """
    return OmbdClient(settings.API_KEY)
