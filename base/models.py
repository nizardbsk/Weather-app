from django.db import models
from django.contrib.auth.models import User
# Create your models here.
class City(models.Model):
    name=models.CharField(max_length=200)
    cover=models.ImageField(upload_to='images/',blank=True)
    def __str__(self):
        return str(self.name)
class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    username=models.CharField(max_length=200)
    avatar=models.ImageField(default='avatar.svg',upload_to='images/')
    created=models.DateField(auto_now_add=True)
    cities = models.ManyToManyField(City,blank=True,default=None)
    def __str__(self):
        return str(self.user)
    def profileimg(self):
        try:
            return self.avatar.url 
        except :
            return ''