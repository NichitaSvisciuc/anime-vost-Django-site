from django.db import models

from django.contrib.auth.models import User

from django.core.validators import FileExtensionValidator

from django.shortcuts import redirect
from django.shortcuts import reverse

import datetime
import PIL


class UserAnimePlaylist(models.Model):

	user = models.OneToOneField(User, on_delete = models.CASCADE)
	playlists = models.ManyToManyField('AnimePlaylist', null = True, blank = True)

	def __str__(self):
		return f"{self.user.username}'s playlist"


class Profile(models.Model):

	user = models.OneToOneField(User, on_delete = models.CASCADE)

	profile_photo = models.ImageField(upload_to = 'media/profile_photoes', default = 'media/default.png', null = True, blank = True)

	age = models.IntegerField(null = True, blank = True)
	anime_love_level = models.CharField(max_length = 200, null = True, blank = True)
	self_description = models.TextField(null = True, blank = True)
	gender = models.CharField(max_length = 200, null = True, blank = True)

	def __str__(self):
		return f"{self.user.username}'s Profile"


class AnimeCategory(models.Model):

	name = models.CharField(max_length = 200)

	def __str__(self):
		return f"Category : {self.name}"

	class Meta:
		verbose_name = 'Anime categorye'


class Comment(models.Model):

	body = models.TextField()
	user = models.ForeignKey(User, on_delete = models.CASCADE)

	date = models.DateTimeField(default = datetime.datetime.now)

	def __str__(self):
		return f"Comment written by {self.user.username}"


class PasswordResetCode(models.Model):

	user = models.OneToOneField(User, on_delete = models.CASCADE)
	code_body = models.CharField(default = '', max_length = 6)

	def __str__(self):
		return f'Code - "{self.code_body}", For user - {self.user.username}'


class Movie(models.Model):

	name = models.CharField(max_length = 200)
	content = models.FileField(upload_to = 'media', null = True, blank = True, 
			validators = [FileExtensionValidator(
				allowed_extensions = ['MOV','avi','mp4','webm','mkv']
			)])
	preview_photo = models.ImageField(upload_to = 'media', null = True, blank = True)

	episode = models.IntegerField(default = 1)

	likes = models.IntegerField(default = 0)
	views = models.ManyToManyField(User)

	comments = models.ManyToManyField(Comment, null = True, blank = True)
	filler = models.BooleanField(default = False)

	slug = models.SlugField()

	def __str__(self):
		return self.name

	def get_views(self):
		k = 0

		for i in self.views.all():
			k += 1
		return k


class AnimePlaylist(models.Model):

	class AgeRatingCategory(models.TextChoices):
		undefined = 'Undefined Type'

		for_kids = "0+"
		for_adults = "18+"

	name = models.CharField(max_length = 200)
	content_videos = models.ManyToManyField(Movie)
	preview_picture = models.ImageField(upload_to = 'media/images')

	comments = models.ManyToManyField(Comment, null = True, blank = True)

	playlist_type = models.CharField(max_length = 200, null = True, blank = True)
	studio = models.CharField(max_length = 200, null = True, blank = True)
	date_aired = models.CharField(max_length = 200, null = True, blank = True)
	status = models.CharField(max_length = 200, null = True, blank = True)
	scores = models.CharField(max_length = 200, null = True, blank = True)
	rating = models.CharField(max_length = 200, null = True, blank = True)
	duration_episode = models.CharField(max_length = 200, null = True, blank = True)
	quality = models.CharField(max_length = 200, null = True, blank = True)

	description = models.TextField(null = True, blank = True)

	likes = models.IntegerField(default = 0)
	categoryes = models.ManyToManyField(AnimeCategory)
	age_rating = models.CharField(
				max_length = 200,
				choices = AgeRatingCategory.choices,
				default = AgeRatingCategory.undefined
			)

	slug = models.SlugField()

	def __str__(self):
		return f"{self.name}"

	def get_absolute_url(self):
		return reverse("anime_playlist", kwargs = {
			'slug' : self.slug
		})	

	def add_to_favourites(self):
		return reverse("add_to_favourites", kwargs = {
			'slug' : self.slug
		})	

	def get_views(self):
		k = 0

		for item in self.content_videos.all():
			k += item.get_views()
		return k

	def get_number_of_comments(self):
		k = 0

		for item in self.comments.all():
			k += 1
		return k

	def get_number_of_episodes(self):
		k = 0

		for item in self.content_videos.all():
			k += 1
		return k