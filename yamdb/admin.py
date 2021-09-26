from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from yamdb.models import Category, CustomUser, Genre, Review, Title

admin.site.register(Category)
admin.site.register(CustomUser, UserAdmin)
admin.site.register(Genre)
admin.site.register(Review)
admin.site.register(Title)
