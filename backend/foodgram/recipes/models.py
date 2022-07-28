from django.db import models
from users.models import User


class Tag(models.Model):
    """Class to store recipe tags in the database."""

    name = models.CharField('Name', max_length=200, unique=True, db_index=True)
    color = models.CharField('Color', max_length=7, unique=True)
    slug = models.SlugField('Slug', max_length=200, unique=True)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Class to store ingredients for recipes in the database."""

    name = models.CharField('Name', max_length=200, unique=True, db_index=True)
    measurement_unit = models.CharField('Measurement unit', max_length=200)

    class Meta:
        verbose_name = 'Ingredient'
        verbose_name_plural = 'Ingredients'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Class to store recipes in the database."""

    tags = models.ManyToManyField(
        Tag, related_name='recipes', verbose_name='Tags')
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Author'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredients',
        related_name='recipes',
        verbose_name='Ingredients'
    )
    name = models.CharField('Name', max_length=200)
    image = models.ImageField('Image', upload_to='recipes/')
    text = models.TextField('Text')
    cooking_time = models.PositiveIntegerField('Cooking time')

    class Meta:
        verbose_name = 'Recipe'
        verbose_name_plural = 'Recipes'

    def __str__(self):
        return self.name


class RecipeIngredients(models.Model):
    """Class to store ingredients of a particular recipe in the database."""

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField('Quantity')

    class Meta:
        verbose_name = 'Ingredient of a recipe'
        verbose_name_plural = 'Ingredients of recipes'

    def __str__(self):
        return f'{self.recipe} needs {self.quantity} of {self.ingredient}'


class Favorite(models.Model):
    """Class to store favorite recipes of a user in the database."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='User'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Recipe'
    )

    class Meta:
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'

    def __str__(self):
        return f'{self.user} added {self.recipe} to favorites'


class ShoppingCart(models.Model):
    """Class to store favorite recipes of a user in the database."""

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping',
        verbose_name='User'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping',
        verbose_name='Recipe'
    )

    class Meta:
        verbose_name = 'Shopping Cart'
        verbose_name_plural = 'Shopping Carts'

    def __str__(self):
        return f'{self.user} added {self.recipe} to shopping cart'
