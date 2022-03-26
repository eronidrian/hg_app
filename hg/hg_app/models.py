from django.db import models
from json import dumps, loads


class Package(models.Model):
    id = models.AutoField(primary_key=True)
    long = models.DecimalField(max_digits=9, decimal_places=6)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    description = models.CharField(max_length=100)
    opening_time = models.DateTimeField()
    picked_up = models.BooleanField()


class Point(models.Model):
    id = models.AutoField(primary_key=True)
    long = models.DecimalField(max_digits=9, decimal_places=6)
    lat = models.DecimalField(max_digits=9, decimal_places=6)
    description = models.CharField(max_length=100)
    opening_time = models.DateTimeField()
    codes = models.CharField(max_length=200)

    # using json to store the codes
    def set_codes(self, x):
        self.set_codes = dumps(x)

    def get_codes(self):
        return loads(self.codes)
