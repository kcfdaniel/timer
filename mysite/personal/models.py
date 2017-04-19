from django.db import models
from django.contrib.auth.models import User
from taggit.managers import TaggableManager
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import datetime, timedelta


class Reward(models.Model):
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	issue_date = models.DateTimeField(auto_now_add=True)
	expiry_date = models.DateTimeField(auto_now_add=True)
	def save(self, force_insert=False, force_update=False, using=None):
		super(Reward, self).save()
		self.expiry_date += timedelta(days=120)
		super(Reward, self).save()
	def __str__(self, **kwargs):
		return str(self.issue_date)

class Spending_to_next_reward(models.Model):
	user = models.OneToOneField(User, on_delete=models.CASCADE)
	amount = models.DecimalField(default = 62, max_digits=10, decimal_places=1)
	def __str__(self):
		return str(self.user)

@receiver(post_save, sender=User)
def create_user_spending_to_next_reward(sender, instance, created, **kwargs):
    if created:
        Spending_to_next_reward.objects.create(user=instance, amount=62)

@receiver(post_save, sender=User)
def save_user_spending_to_next_reward(sender, instance, **kwargs):
    instance.spending_to_next_reward.save()


class Game(models.Model):
	title = models.CharField(max_length=140)
	genre = models.CharField(max_length=140)
	date = models.DateTimeField()
	##tag = models.ManyToManyField(Tag, blank=True)
	tag = TaggableManager(blank=True)
	price = models.DecimalField(max_digits=10, decimal_places=1)
	def __str__(self):
		return self.title

class Review(models.Model):
	text = models.TextField()
	date = models.DateTimeField()
	game = models.ForeignKey(Game, on_delete=models.CASCADE)
	writer = models.ForeignKey(User, on_delete=models.CASCADE)
	def __str__(self):
		return self.text

class List(models.Model):
	name = models.CharField(max_length=100)
	games = models.ManyToManyField(Game)
	def __str__(self):
		return self.name

class Transaction(models.Model):
	buyer = models.ForeignKey(User, on_delete=models.CASCADE)
	game = models.ForeignKey(Game, on_delete=models.CASCADE)
	date = models.DateTimeField()
	def __str__(self):
		return str(self.date)
