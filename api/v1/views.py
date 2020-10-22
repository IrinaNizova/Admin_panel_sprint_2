from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.list import BaseListView
from django.views.generic.detail import BaseDetailView
from django.http.response import Http404
from django.core.exceptions import ValidationError

from movies.models import Filmwork


class MoviesApiMixin:
    model = Filmwork
    http_method_names = ['get']

    def get_queryset(self):
        actors = ArrayAgg('members__full_name', distinct=True, filter=Q(membership__role='actor'))
        writers = ArrayAgg('members__full_name', distinct=True, filter=Q(membership__role='writer'))
        director = ArrayAgg('members__full_name', distinct=True, filter=Q(membership__role='director'))
        genres = ArrayAgg('genre_types__name', distinct=True)
        return self.model.objects.prefetch_related('genre_types', 'members').\
            annotate(actors=actors, writers=writers, directors=director, genres=genres).all().values()

    def render_to_response(self, context, **response_kwargs):
        return JsonResponse(context, safe=False)


class MoviesDetailApi(MoviesApiMixin, BaseDetailView):

    slug_field = 'id'

    def get_object(self):
        uuid = self.kwargs.get('uuid', '')
        try:
            results = self.get_queryset().filter(id=uuid).values()
        except ValidationError:
            raise Http404(f"Do not find film with uuid {uuid}")
        if not results:
            raise Http404(f"Do not find film with uuid {uuid}")
        return results

    def get_context_data(self, **kwargs):
        return list(self.get_object())[0]


class MoviesListApi(MoviesApiMixin, BaseListView):

    paginate_by = 50

    def get_context_data(self, **kwargs):
        paginator, page, queryset, is_paginated = self.paginate_queryset(list(self.get_queryset()), self.paginate_by)
        total_pages = round(self.get_queryset().count() / self.paginate_by)
        page = self.request.GET.get('page')
        if not page:
            next = 2
            prev = None
        elif page == total_pages or page == 'last':
            next = None
            prev = total_pages - 1
        else:
            next = int(page) + 1
            prev = int(page) - 1
        return {
            'results': queryset,
            'count': self.get_queryset().count(),
            'total_pages': total_pages,
            'prev': prev,
            'next': next
        }

