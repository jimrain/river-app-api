import django_filters
from core.models import River


class RiverFilter(django_filters.FilterSet):
    name = django_filters.CharFilter(field_name='name',
                                     lookup_expr='icontains')
    feature = django_filters.CharFilter(field_name='feature',
                                        lookup_expr='iexact')
    state = django_filters.CharFilter(field_name='state',
                                      lookup_expr='iexact')

    class Meta:
        model = River
        fields = ['name', 'feature', 'state']
