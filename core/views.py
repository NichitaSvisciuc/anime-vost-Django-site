from django.shortcuts import render, get_object_or_404
from django.contrib import messages

from django.core.mail import send_mail
from django.conf import settings

from django.contrib.auth.hashers import make_password

from django.contrib.auth.models import User

from django.core.paginator import Paginator, EmptyPage

from django.contrib.auth import authenticate, login
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required

from django.db.models.signals import post_save
from django.dispatch import receiver

from django.db.models import Q

import os

from .models import *
from .forms import *

import random
import string

############################################################################


def sort_playlists_by_views(query_set):

	new_list = list(query_set)

	for i in range(len(new_list)):
		for j in range(0, len(new_list) - i - 1):
			if new_list[j].get_views() < new_list[j + 1].get_views():
				new_list[j], new_list[j + 1] = new_list[j + 1], new_list[j] 

	return new_list


def home(request):

	search = request.GET.get('search', '')

	if search:
		playlist = AnimePlaylist.objects.filter(Q(name__icontains = search) | Q(age_rating__icontains = search))
	else:
		playlist = AnimePlaylist.objects.all()

	playlists = sort_playlists_by_views(playlist)

	context = {
		'playlists' : playlists
	}

	return render(request, 'index.html', context)


def anime_playlist(request, slug):

	playlist = AnimePlaylist.objects.get(slug = slug)

	context = {
		'playlist' : playlist 
	}

	return render(request, 'anime-details.html', context)


def categories_page(request):

	# Filter search
	search = request.GET.get('search', '')

	if search:
		playlists = AnimePlaylist.objects.filter(Q(name__icontains = search) | Q(age_rating__icontains = search))
	else:
		playlists = AnimePlaylist.objects.all()

	# Second argument in class __init__ shows the number of objects displayed on page
	pagins = Paginator(playlists, 1)

	number_of_pages = pagins.num_pages

	page_taken = request.GET.get('page', 1)

	try:
		page = pagins.page(page_taken)
	except EmptyPage:
		page = pagins.page(1)

	context = {
		'playlists' : page,
		'number_of_pages' : range(number_of_pages),
	}		

	return render(request, 'categories.html', context)


# Redirects and specifies the way how episodes will be displayed
def watch(request, slug, episde_number):

	playlist = AnimePlaylist.objects.get(slug = slug)

	current_episode = playlist.content_videos.get(episode = episde_number)

	if request.user not in current_episode.views.all():
		current_episode.views.add(request.user)

	context = {
		'playlist' : playlist,
		'current_episode' : current_episode,

		# Counter for series episode number
		'number_of_episodes' : range(1, playlist.get_number_of_episodes() + 1),
	}

	return render(request, 'anime-watching.html', context)


@login_required
def add_to_favourites(request, slug):

	playlist = AnimePlaylist.objects.get(slug = slug)
	user_playlist = UserAnimePlaylist.objects.get(user = request.user)

	# Adds or deletes content from your playlist
	if playlist not in user_playlist.playlists.all():

		user_playlist.playlists.add(playlist)
		playlist.likes += 1

		playlist.save()
		user_playlist.save()

	else:
		user_playlist.playlists.remove(playlist)
		playlist.likes -= 1

		playlist.save()
		user_playlist.save()

	return redirect(request.META['HTTP_REFERER'])


@login_required
def profile(request):

	if request.method == 'POST':
		form = ProfileUpdateForm(request.POST, request.FILES, instance = request.user.profile)
  
		if form.is_valid():
			form.save()
			document = form.save()
			return redirect('profile')

	else:
		form = ProfileUpdateForm(instance = request.user.profile)

	return render(request, 'profile.html', {'form' : form})


# Adds comments for both, movies or anime playlists, this is specified by a taken argument
@login_required
def add_comment(request, object_type):

	if request.method == 'POST':
		comment_body = request.POST.get('comment_body')

		curent_object_id = request.POST.get('id')

		if object_type == 'playlist':
			curent_object = AnimePlaylist.objects.get(id = curent_object_id)
		elif object_type == 'movie':
			curent_object = Movie.objects.get(id = curent_object_id)
		else:
			print('Uknown object type')

		new_comment = Comment.objects.create(body = comment_body, user = request.user)

		curent_object.comments.add(new_comment)
		curent_object.save()

	else:
		print('Incorect method')

	return redirect(request.META['HTTP_REFERER'])


@login_required
def update_profile_info(request):

	age = request.POST.get('age')
	description = request.POST.get('description')
	experience = request.POST['experience'] 
	gender = request.POST['gender']

	user_profile = Profile.objects.get(user = request.user)

	user_profile.age = age
	user_profile.anime_love_level = experience
	user_profile.self_description = description
	user_profile.gender = gender

	user_profile.save()

	return redirect('profile')


def register(request):
	
	if request.method == 'POST':

		form = UserRegisterForm(request.POST)

		if form.is_valid():

			user = form.save()
			username = form.cleaned_data.get('username')
			email = form.cleaned_data.get('email')

			user = authenticate(username = form.cleaned_data['username'],
								email = form.cleaned_data['email'],
								password = form.cleaned_data['password1'],
								)
			login(request, user)

			messages.success(request, f"New Account Created for {username}")

			form.save()

			return redirect("home")

		else:
			for msg in form.error_messages:
				messages.error(request, f"{msg} : {form.error_messages[msg]}")
				print(msg)             

	form = UserRegisterForm()

	return render(request, 'signup.html', {'form': form})


###########################################################################################################################
# User password reset - |
#                       v
# This function does not allow the user to access a page directly from pasting it to url
def get_referer(request):

	referer = request.META.get('HTTP_REFERER')

	# Checks if the page is accessed by a reference, in case when a user tryes to access it directly from url bar it returns None because its not a reference
	if not referer:
		return None

	return referer


# 1st step - Redirects to a reset code page and this function creates new unique reset code for specified user and sends to it to his email
def create_reset_password_code(request):

	password_codes = PasswordResetCode.objects.all()
	username = request.GET.get('username')

	users = User.objects.all()
	
	for user in users:
		if username == user.username:
			print('User exists')
			user_for_password_reset = User.objects.get(username = username)

			for code in password_codes:
				if code.user == user_for_password_reset:
					code.delete()

			letters = string.ascii_lowercase
			reset_code_body = ''.join(random.choice(letters) for i in range(6))
			reset_code = PasswordResetCode.objects.create(user = user_for_password_reset, code_body = reset_code_body)

			print(user_for_password_reset.email)

			subject = 'Your password reset code for Anime Vost'
			message = f' Reset code - {reset_code_body} '
			email_from = settings.EMAIL_HOST_USER
			recipient_list = [user_for_password_reset.email,]
			send_mail( subject, message, email_from, recipient_list )

			return redirect('password_reset', user = user_for_password_reset.id)

	messages.error(request, f"Inexistent account")

	return render(request, 'set_account_for_password_reset.html')


# This page can not be accessed from directly url pasting
# 2nd step - User checks his email and enters the reset code, if it exists user will be redirected to 3rd page for password change
def password_reset(request, user):

	if not get_referer(request):

		response = HttpResponse('Page does not exist')
		response.status_code = 404

		return response

	current_user_for_password_reset = User.objects.get(id = user)

	password_reset_code = request.GET.get('password_reset_code')
	user_password_reset_codes = PasswordResetCode.objects.filter(user = current_user_for_password_reset)

	for code in user_password_reset_codes:
		if str(code.code_body) == password_reset_code:
			print('Access granted')

			return redirect('set_new_password', user = current_user_for_password_reset.id)

	return render(request, 'password_reset.html', {'current_user_for_password_reset' : current_user_for_password_reset})


# This page can not be accessed from directly url pasting
# 3rd step - Changes the account password for one that was specified by user
def set_new_password(request, user):

	if not get_referer(request):

		response = HttpResponse('Page does not exist')
		response.status_code = 404

		return response

	current_user_for_password_reset = User.objects.get(id = user)

	password = request.GET.get('password', '')

	if password:

		current_user_for_password_reset.password = make_password(password)

		print(current_user_for_password_reset.password)

		current_user_for_password_reset.save()
		print('password changed successfully')

		login(request, current_user_for_password_reset)

		return redirect('home')

	return render(request, 'set_new_password.html', {'current_user_for_password_reset' : current_user_for_password_reset})

###########################################################################################################################


# Creates a unique for playlist for every user when its registered
@receiver(post_save, sender = User)
def create_anime_playlist_for_user_when_registered(sender, instance, created, **kwargs):

	if created:
		UserAnimePlaylist.objects.create(user = instance)


# Creates an extension for User model, that is unique and only one for every user
@receiver(post_save, sender = User)
def update_user_profile(sender, instance, created, **kwargs):

	if created:
		Profile.objects.create(user = instance)