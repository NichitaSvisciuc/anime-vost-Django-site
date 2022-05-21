from django.contrib import admin

from .models import *

class AnimeFilterAdmin(admin.ModelAdmin):

	search_fields = [
		'name',
	]

admin.site.register(Movie, AnimeFilterAdmin)
admin.site.register(Comment)
admin.site.register(AnimePlaylist, AnimeFilterAdmin)
admin.site.register(AnimeCategory)
admin.site.register(UserAnimePlaylist)
admin.site.register(PasswordResetCode)
admin.site.register(Profile)