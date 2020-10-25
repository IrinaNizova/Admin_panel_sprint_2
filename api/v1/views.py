from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView
from django.http.response import Http404
from django.core.exceptions import ValidationError

from movies.models import Filmwork
from config.settings.base import ITEMS_ON_PAGE


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self):
        actors = ArrayAgg('members__full_name', distinct=True, filter=Q(membership__role='actor'))
        writers = ArrayAgg('members__full_name', distinct=True, filter=Q(membership__role='writer'))
        director = ArrayAgg('members__full_name', distinct=True, filter=Q(membership__role='director'))
        genres = ArrayAgg('genre_types__name', distinct=True)
        return (self.model.objects.annotate(actors=actors, writers=writers, directors=director, genres=genres)
                .all().values())

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, safe=False)


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    slug_field = 'id'

    def get_object(self):
        uuid = self.kwargs.get('uuid', '')
        try:
            results = self.get_queryset().filter(id=uuid).values()
        except ValidationError:
            raise Http404(f"Could not find a film with uuid {uuid}")
        if not results:
            raise Http404(f"Could not find a film with uuid {uuid}")
        return results

    def get_context_data(self, **kwargs):
        return self.get_object().first()


class MoviesListApi(MoviesApiMixin, BaseListView):

    paginate_by = ITEMS_ON_PAGE

    def get_context_data(self, **kwargs):
        paginator, page, queryset, is_paginated = self.paginate_queryset(list(self.get_queryset()), self.paginate_by)

        return {
            'results': queryset,
            'count': self.get_queryset().count(),
            'total_pages': paginator.num_pages,
            'prev': page.previous_page_number() if page.has_previous() else None,
            'next': page.next_page_number() if page.has_next() else None
        }

