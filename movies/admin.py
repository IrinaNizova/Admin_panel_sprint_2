from django.contrib import admin

from .models import Filmwork, Genre, Persons, Membership, Actors, Directors, Writers


class PersonRoleInline(admin.TabularInline):
    model = Membership
    extra = 0


@admin.register(Filmwork)
class FilmworkAdmin(admin.ModelAdmin):
    # отображение полей в списке
    list_display = ('title', 'type', 'creation_date', 'rating')
    # порядок следования полей в форме создания/редактирования
    fields = (
        'title', 'type', 'description', 'creation_date', 'certificate',
        'file_path', 'rating', 'genre_types'
    )
    list_filter = ('type',)
    inlines = [
        PersonRoleInline
    ]


@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    fields = ('name', 'description')
    ordering = ('name', 'created')
    search_fields = ('name',)


@admin.register(Persons)
class PersonsAdmin(admin.ModelAdmin):
    ordering = ('full_name', 'created')
    search_fields = ('full_name',)


@admin.register(Actors)
class Actor(admin.ModelAdmin):
    ordering = ('full_name', 'created')
    search_fields = ('full_name',)


@admin.register(Directors)
class Director(admin.ModelAdmin):
    ordering = ('full_name', 'created')
    search_fields = ('full_name',)


@admin.register(Writers)
class Writer(admin.ModelAdmin):
    ordering = ('full_name', 'created')
    search_fields = ('full_name',)