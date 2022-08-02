from djoser.serializers import (CurrentPasswordSerializer, PasswordSerializer,
                                UserCreateSerializer, UserSerializer)
from recipes.models import Ingredient, Recipe, RecipeIngredients, Tag
from rest_framework import serializers
from users.models import User


class CustomUserCreateSerializer(UserCreateSerializer):
    """Custom serializer for new users registration."""

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'password',
        )


class CustomUserSerializer(UserSerializer):
    """Custom serializer for displaying information about users."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name',
            'last_name', 'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.following.filter(user=request.user).exists()


class CustomSetPasswordRetypeSerializer(
    PasswordSerializer, CurrentPasswordSerializer
):
    """Custom serializer to change current user's password."""

    pass


class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags."""

    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    """Serializer for ingredients."""

    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientsSerializer(serializers.ModelSerializer):
    """Serializer for ingredients of a particular recipe."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    tags = TagSerializer(many=True)
    author = CustomUserSerializer()
    ingredients = RecipeIngredientsSerializer(
        many=True, source='recipeingredients')

    class Meta:
        model = Recipe
#        fields = [
#            'id', 'tags', 'author', 'ingredients', 'image', 'name', 'text',
#            'cooking_time', 'is_favorited', 'is_in_shopping_cart'
#        ]
# добавить поля 'image', 'is_favorited', 'is_in_shopping_cart'
        fields = [
            'id', 'tags', 'author', 'ingredients', 'name', 'text',
            'cooking_time'
        ]
