from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.
class CustomUser(AbstractUser):
    USERNAME_FIELD = 'email'
    email = models.EmailField(('email address'), unique=True)
    REQUIRED_FIELDS = [] # removes email from REQUIRED_FIELDS

    def __str__(self):
        return self.email


class SuperSecretCode(models.Model):
    code = models.CharField(max_length=19, unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='super_secret_code', blank=True, null=True)
    activated = models.BooleanField(default=False)
    activation_date = models.DateTimeField(blank=True, auto_now_add=True)

    def __str__(self):
        if self.activated:
            return f'{self.code} (activated on {self.activation_date.strftime("%d %B %Y")} by {self.user})'
        else:
            return f'{self.code} (not yet activated)'
