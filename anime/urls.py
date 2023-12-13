from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('owo/', admin.site.urls),
    path('', views.home, name='home'),
    path('new-season/', views.newSeason, name='newseason'),
    path('popular/', views.popular, name='popular'),
    path('movies/', views.movies, name='movies'),
    path('anime-list/', views.animeList, name='animelist'),
    path('search/', views.search, name='search'),
    path('category/<slug:slug>/', views.category, name='category'),
    path('episode/<slug:slug>/', views.episode, name='episode'),
    path('genre/<slug:slug>/', views.genre, name='genre'),
    path('sub-category/<slug:slug>/', views.subCategory, name='subcategory'),
    path('dmca/', views.dmca, name='dmca'),
    path('about-us/', views.aboutUs, name='about'),
    path('contact-us/', views.contactUs, name='contact'),
    path('blog-boruto-next-generation/', views.boruto, name='boruto'),
    path('blog-naruto/', views.naruto, name='naruto'),
    path('blog-naruto-shippuden/', views.shippuden, name='shippuden'),
    path('blog-hunter-x-hunter/', views.hunter, name='hunter'),
    path('blog-demon-slayer/', views.demon, name='demon'),
    path('blog-tokyo-revengers/', views.tokyo, name='tokyo'),
    path('sitemap/', views.sitemap, name='sitemap'),
    path('ads.txt/', views.ads, name='ads'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
