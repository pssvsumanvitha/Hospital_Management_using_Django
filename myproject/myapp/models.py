from django.db import models

class Users(models.Model):
    email = models.EmailField(max_length=30, unique=True)
    password = models.CharField(max_length=50)

    def __str__(self):
        return self.email
