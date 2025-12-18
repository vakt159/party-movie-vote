from django.db import models

class Movie(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    imdb_url = models.URLField()

    def __str__(self):
        return self.name