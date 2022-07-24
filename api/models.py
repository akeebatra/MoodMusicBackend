from django.db import models

class Tracks(models.Model):

    href = models.CharField(max_length=50, blank=False, null=False)
    id = models.CharField(max_length=50, blank=False, null=False,primary_key=True)
    name = models.CharField(max_length=50, blank=True, null=False)
    #type = models.CharField(max_length=50, blank=False, null=False)
    uri = models.CharField(max_length=100, blank=True, null=False)
    duration_ms = models.IntegerField(default=0, null=False, blank=False)

