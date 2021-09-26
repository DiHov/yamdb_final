from django_filters import rest_framework as filters

from .models import Category, Genre, Title


class TitleFilter(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='contains')
    year = filters.NumberFilter()
    genre = filters.ModelChoiceFilter(
        queryset=Genre.objects.all(),
        to_field_name='slug'
    )
    category = filters.ModelChoiceFilter(
        queryset=Category.objects.all(),
        to_field_name='slug'
    )

    class Meta:
        model = Title
        fields = ["name", "genre", "year", "category"]
