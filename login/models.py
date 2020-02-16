from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    username = models.CharField(max_length=30)

    def __str__(self):
        return self.username

class TutorCourse(models.Model):
    name = models.CharField(max_length=200)
    dept = models.CharField(max_length=200)
    number = models.IntegerField()
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class StudentCourse(models.Model):
    name = models.CharField(max_length=200)
    dept = models.CharField(max_length=200)
    number = models.IntegerField()
    user = models.ForeignKey(Profile, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()
