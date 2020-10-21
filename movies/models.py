import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator
from model_utils.models import TimeStampedModel, UUIDModel


class Genre(TimeStampedModel, UUIDModel):
    name = models.CharField(_('название'), max_length=255)
    description = models.TextField(_('описание'), blank=True)

    class Meta:
        verbose_name = _('жанр')
        verbose_name_plural = _('жанры')
        db_table = 'genre'
        indexes = [
                models.Index(fields=['name']),
            ]

    def __str__(self):
        return self.name


class FilmworkType(models.TextChoices):
    MOVIE = 'movie', _('фильм')
    TV_SHOW = 'tv_show', _('шоу')


class Persons(TimeStampedModel, UUIDModel):
    full_name = models.CharField(_('имя'), max_length=255)
    birth_date = models.DateField(_('дата рождения'), blank=True)

    class Meta:
        verbose_name = _('участник фильма')
        verbose_name_plural = _('участники фильма')
        db_table = 'person'
        indexes = [
            models.Index(fields=['full_name']),
        ]

    def __str__(self):
        return self.full_name


class RolesType(models.TextChoices):
    ACTOR = 'actor', _('актёр')
    WRITER = 'writer', _('сценарист')
    DIRECTOR = 'director', _('режиссёр')


class ActorManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(membership__role=RolesType.ACTOR)


class Actors(Persons):
    objects = ActorManager()

    class Meta:
        proxy = True
        verbose_name = _('актёр')
        verbose_name_plural = _('актёры')


class WriterManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(membership__role=RolesType.WRITER)


class Writers(Persons):
    objects = WriterManager()

    class Meta:
        proxy = True
        verbose_name = _('сценарист')
        verbose_name_plural = _('сценаристы')


class DirectorManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(membership__role=RolesType.DIRECTOR)


class Directors(Persons):
    objects = DirectorManager()

    class Meta:
        proxy = True
        verbose_name = _('режиссёр')
        verbose_name_plural = _('режиссёры')


class Filmwork(TimeStampedModel, UUIDModel):
    title = models.CharField(_('название'), max_length=255)
    description = models.TextField(_('описание'), blank=True)
    creation_date = models.DateField(_('дата создания фильма'), blank=True)
    certificate = models.TextField(_('сертификат'), blank=True)
    file_path = models.FileField(_('файл'), upload_to='film_works/', blank=True)
    rating = models.FloatField(_('рейтинг'), validators=[MinValueValidator(0)], blank=True)
    type = models.CharField(_('тип'), max_length=20, choices=FilmworkType.choices)
    genre_types = models.ManyToManyField(Genre, db_table='genre_film_work')
    members = models.ManyToManyField(Persons, through='Membership')

    class Meta:
        verbose_name = _('кинопроизведение')
        verbose_name_plural = _('кинопроизведения')
        db_table = 'film_work'
        indexes = [
            models.Index(fields=['title']),
        ]

    def __str__(self):
        return self.title


class Membership(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    film_work = models.ForeignKey(Filmwork, on_delete=models.CASCADE)
    person = models.ForeignKey(Persons, on_delete=models.CASCADE)
    role = models.CharField(_('тип'), max_length=20, choices=RolesType.choices)

    class Meta:
        db_table = 'person_film_work'
        constraints = [
            models.UniqueConstraint(fields=['film_work', 'person', 'role'], name='film_person_role')
        ]

