from django.db import models


class SearchTerm(models.Model):
    term = models.TextField(unique=True)
    last_search = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['id']


class Genre(models.Model):
    name = models.TextField(unique=True)

    class Meta:
        ordering = ['name']


class Movie(models.Model):
    title = models.TextField()
    year = models.PositiveIntegerField()
    runtime_minutes = models.PositiveIntegerField(null=True)
    imdb_id = models.SlugField(unique=True)
    genres = models.ManyToManyField(Genre, related_name='movies')
    plot = models.TextField(null=True, blank=True)
    # to determine if the movie contains only the values in the list response, or if it
    # has been supplemented with the full detail response:
    is_full_record = models.BooleanField(default=False)
