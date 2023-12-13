from django.db import models

# Create your models here.

class ViewsCounter(models.Model):
    page = models.CharField(max_length=100, primary_key=True)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.page

class CategoryView(models.Model):
    title = models.CharField(max_length=100, primary_key=True)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.title

class EpisodeView(models.Model):
    episode = models.CharField(max_length=100, primary_key=True)
    views = models.IntegerField(default=0)

    def __str__(self):
        return self.episode
