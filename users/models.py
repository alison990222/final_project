from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):

	class Meta(AbstractUser.Meta):
		pass


class Pic(models.Model):
	username = models.CharField(max_length=50)
	# upload_to 表圖片保存路徑
	picture = models.ImageField(upload_to='pictures')
	# 處理結果
	res = models.ImageField(blank=True)
	timestamp = models.TextField()

	class Meta:
		db_table = "picture"

	def __str__(self):
		return str(self.id)
