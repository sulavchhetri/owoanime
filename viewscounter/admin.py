from django.contrib import admin
from .models import ViewsCounter, CategoryView, EpisodeView
# Register your models here.

class CounterAdmin(admin.ModelAdmin):
    list_display = ('page', 'views')
    #list_editable = ('views',)
    ordering = ['-views']

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('title', 'views')
    #list_editable = ('views',)
    ordering = ['-views']

class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('episode', 'views')
    #list_editable = ('views',)
    ordering = ['-views']

admin.site.register(ViewsCounter, CounterAdmin)
admin.site.register(CategoryView, CategoryAdmin)
admin.site.register(EpisodeView, EpisodeAdmin)
