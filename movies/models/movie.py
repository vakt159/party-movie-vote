from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from datetime import date


class Movie(models.Model):
    name = models.CharField(max_length=255)
    release_year = models.PositiveIntegerField(
        validators=[MinValueValidator(1895),
                    MaxValueValidator(date.today().year)],
        default=date.today().year, blank=True)
    director = models.CharField(max_length=255, default="", blank=True)
    description = models.TextField()
    imdb_url = models.URLField()

    def __str__(self):
        return self.name
