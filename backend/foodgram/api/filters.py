from django_filters import rest_framework as rf_filters
from recipes.models import Recipe


class RecipeFilter(rf_filters.FilterSet):
    """Class for filtering recipes."""

    tags = rf_filters.AllValuesMultipleFilter(field_name='tags__slug')
    is_favorited = rf_filters.NumberFilter(method='recipe_boolean_methods')
    is_in_shopping_cart = rf_filters.NumberFilter(
        method='recipe_boolean_methods')

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def recipe_boolean_methods(self, queryset, name, value):
        if bool(value) and not self.request.user.is_anonymous:
            user = self.request.user
            recipe_ids = [
                r.pk for r in queryset if getattr(r, name)(user) == value]
            if recipe_ids:
                return queryset.filter(pk__in=recipe_ids)
            return queryset.none()
        return queryset
