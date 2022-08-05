from django_filters import rest_framework as rf_filters
from recipes.models import Recipe, Tag


class RecipeFilter(rf_filters.FilterSet):
    """Class for filtering recipes."""

    TAG_CHOICES = tuple([(tag.slug, tag.slug) for tag in Tag.objects.all()])

    tags = rf_filters.MultipleChoiceFilter(
        field_name='tags__slug', choices=TAG_CHOICES)
    is_favorited = rf_filters.NumberFilter(method='get_is_favorited')
    is_in_shopping_cart = rf_filters.NumberFilter(
        method='get_is_in_shopping_cart')

    class Meta:
        model = Recipe
        fields = ['tags', 'author', 'is_favorited', 'is_in_shopping_cart']

    def get_is_favorited(self, queryset, name, value):
        user = self.request.user
        recipe_ids = [
            x.pk for x in Recipe.objects.all() if x.is_favorited(user) == value
        ]
        if recipe_ids:
            return Recipe.objects.filter(pk__in=recipe_ids)
        return Recipe.objects.none()

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        recipes = Recipe.objects.all()
        recipe_ids = [
            x.pk for x in recipes if x.is_in_shopping_cart(user) == value
        ]
        if recipe_ids:
            return Recipe.objects.filter(pk__in=recipe_ids)
        return Recipe.objects.none()
