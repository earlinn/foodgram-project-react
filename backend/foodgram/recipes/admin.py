from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, RecipeIngredients,
                     ShoppingCart, Tag)


class RecipeIngredientsInline(admin.TabularInline):
    """Inline class for the RecipeIngredients model display."""

    model = RecipeIngredients
    extra = 1


class RecipeAdmin(admin.ModelAdmin):
    """Class to customize recipes display in admin panel."""

    list_display = [
        'pk', 'name', 'author', 'text', 'cooking_time',
        'total_favorites', 'pub_date']
    search_fields = ['name', 'author', 'cooking_time', 'text']
    readonly_fields = ['total_favorites']
    list_filter = ['name', 'pub_date', 'author', 'tags']
    empty_value_display = '-empty-'
    inlines = [RecipeIngredientsInline]

    @admin.display(description='Total favorites')
    def total_favorites(self, obj):
        return obj.favorites.count()


class TagAdmin(admin.ModelAdmin):
    """Class to customize tags display in admin panel."""

    list_display = ['pk', 'name', 'color', 'slug']
    search_fields = ['name', 'color', 'slug']


class IngredientAdmin(admin.ModelAdmin):
    """Class to customize ingredients display in admin panel."""

    list_display = ['pk', 'name', 'measurement_unit']
    search_fields = ['name', 'measurement_unit']
    list_filter = ['name', 'measurement_unit']
    inlines = [RecipeIngredientsInline]


class RecipeIngredientsAdmin(admin.ModelAdmin):
    """Class to customize ingredients of recipes display in admin panel."""

    list_display = ['pk', 'recipe', 'ingredient', 'amount']
    search_fields = ['recipe', 'ingredient']
    list_filter = ['recipe', 'ingredient']


class FavoriteAdmin(admin.ModelAdmin):
    """Class to customize users' favorite recipes display in admin panel."""

    list_display = ['pk', 'user', 'recipe']
    search_fields = ['user', 'recipe']
    list_filter = ['user', 'recipe']


class ShoppingCartAdmin(admin.ModelAdmin):
    """Class to customize users' shopping carts display in admin panel."""

    list_display = ['pk', 'user', 'recipe']
    search_fields = ['user', 'recipe']
    list_filter = ['user', 'recipe']


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(RecipeIngredients, RecipeIngredientsAdmin)
admin.site.register(Favorite, FavoriteAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
