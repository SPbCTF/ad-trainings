from django.conf.urls import patterns, url
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cats.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^accounts/login/$', 'main.views.login', name='login'),
    url(r'^accounts/logout/$', 'django.contrib.auth.views.logout'),
    url(r'^accounts/register/$', 'main.views.registration', name='registration'),

    url(r'^$', 'main.views.main_view'),
    url(r'^search/$', 'main.views.search'),
    url(r'^users/$', 'main.views.users_list'),
    url(r'^user/(?P<user_name>\w+)$', 'main.views.user_images'),
) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
