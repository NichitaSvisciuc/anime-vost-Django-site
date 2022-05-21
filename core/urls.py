from django.urls import path

from django.conf import settings
from django.conf.urls.static import static

from .views import *

urlpatterns = [
	path('', home, name = 'home'),

	path('profile', profile, name = 'profile'),
	path('add_comment/<object_type>', add_comment, name = 'add_comment'),
	path('categories_page', categories_page, name = 'categories_page'),
	path('update_profile_info', update_profile_info, name = 'update_profile_info'),
	path('password_reset/<user>', password_reset, name = 'password_reset'),
	path('set_new_password/<user>', set_new_password, name = 'set_new_password'),
	path('create_reset_password_code', create_reset_password_code, name = 'create_reset_password_code'),

	path('watch/<slug>/<episde_number>', watch, name = 'watch'),
	path('anime_playlist/<slug>', anime_playlist, name = 'anime_playlist'),
	path('add_to_favourites/<slug>', add_to_favourites, name = 'add_to_favourites'),
] 

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,
                          document_root=settings.MEDIA_ROOT)