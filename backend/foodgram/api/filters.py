from django_filters import rest_framework as rf_filters
from recipes.models import Recipe, Tag


class RecipeFilter(rf_filters.FilterSet):
    """Class for filtering recipes."""

    TAG_CHOICES = tuple([(tag.slug, tag.slug) for tag in Tag.objects.all()])

    tags = rf_filters.MultipleChoiceFilter(
        field_name='tags__slug', choices=TAG_CHOICES)
    is_favorited = rf_filters.NumberFilter(method='recipe_boolean_methods')
    is_in_shopping_cart = rf_filters.NumberFilter(
        method='recipe_boolean_methods')

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def recipe_boolean_methods(self, queryset, name, value):
        user = self.request.user
        recipe_ids = [
            r.pk for r in queryset if getattr(r, name)(user) == value]
        if recipe_ids:
            return queryset.filter(pk__in=recipe_ids)
        return queryset.none()
