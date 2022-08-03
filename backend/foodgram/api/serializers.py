import base64
import io
from collections import OrderedDict

from django.core.files.images import ImageFile
from django.shortcuts import get_object_or_404
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
    """Serializer to display the ingredients of a particular recipe."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredients
        fields = ['id', 'name', 'measurement_unit', 'amount']


class RecipeCreateIngredientsSerializer(serializers.ModelSerializer):
    """Serializer to display ingredients during recipe creation."""

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredients
        fields = ['id', 'amount']

    def to_representation(self, instance):
        old_repr = super().to_representation(instance)
        new_repr = OrderedDict()
        new_repr['id'] = old_repr['id']
        new_repr['name'] = instance.ingredient.name
        new_repr['measurement_unit'] = instance.ingredient.measurement_unit
        new_repr['amount'] = old_repr['amount']
        return new_repr


class ImageBase64Field(serializers.Field):
    """Image objects encoded in base64 strings."""

    # Comment to_representation method before running the app
    # in docker-compose containers as the frontend encodes the image itself
    def to_representation(self, value):
        value = base64.b64encode(bytes(value.read()))
        return f'data:image/png;base64,{value}'

    def to_internal_value(self, data):
        data = base64.b64decode(data.strip('data:image/png;base64,'))
        return ImageFile(io.BytesIO(data), name='image.png')


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for recipes."""

    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(
        many=True, source='recipeingredients')
    image = ImageBase64Field()

    class Meta:
        model = Recipe
        # добавить поля 'is_favorited', 'is_in_shopping_cart'
        fields = [
            'id', 'tags', 'author', 'ingredients', 'name', 'image', 'text',
            'cooking_time'
        ]


class RecipeCreateSerializer(RecipeSerializer):
    """Serializer for creating recipes."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = RecipeCreateIngredientsSerializer(
        source='recipeingredients', many=True)

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        recipe_ingredients = [
            RecipeIngredients(
                recipe=recipe,
                ingredient=current_ingredient['ingredient'],
                amount=current_ingredient['amount'],
            )
            for current_ingredient in ingredients
        ]

        RecipeIngredients.objects.bulk_create(recipe_ingredients)

        return recipe

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        tag_id_list, tag_list = repr['tags'], []
        for tag_id in tag_id_list:
            tag = get_object_or_404(Tag, id=tag_id)
            serialized_tag = OrderedDict(TagSerializer(tag).data)
            tag_list.append(serialized_tag)
        repr['tags'] = tag_list
        return repr
