from collections import OrderedDict

from django.db import transaction
from django.shortcuts import get_object_or_404
from djoser.serializers import (CurrentPasswordSerializer, PasswordSerializer,
                                UserCreateSerializer, UserSerializer)
from drf_extra_fields.fields import Base64ImageField
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

    def validate_username(self, value):
        # это уведомление фронтенд выводит
        if value == 'me':
            raise serializers.ValidationError(
                'Unable to create user with username me.'
            )
        return value


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


class SubscriptionSerializer(CustomUserSerializer):
    """Serializer to subscribe to other recipe authors."""

    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email', 'id', 'username', 'first_name', 'last_name',
            'is_subscribed',  'recipes', 'recipes_count',
        )
        depth = 1

    def get_recipes(self, obj):
        recipes_limit = self.context.get('request').GET.get('recipes_limit')
        if recipes_limit:
            recipes = obj.recipes.all()[:int(recipes_limit)]
        else:
            recipes = obj.recipes.all()
        return RecipeInSubscriptionSerializer(
            recipes, many=True, read_only=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


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
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeCreateIngredientsSerializer(serializers.ModelSerializer):
    """Serializer to display ingredients during recipe creation."""

    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all())

    class Meta:
        model = RecipeIngredients
        fields = ('id', 'amount',)

    def to_representation(self, instance):
        old_repr = super().to_representation(instance)
        new_repr = OrderedDict()
        new_repr['id'] = old_repr['id']
        new_repr['name'] = instance.ingredient.name
        new_repr['measurement_unit'] = instance.ingredient.measurement_unit
        new_repr['amount'] = old_repr['amount']
        return new_repr


class RecipeSerializer(serializers.ModelSerializer):
    """Serializer for displaying recipes."""

    tags = TagSerializer(many=True)
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientsSerializer(
        many=True, source='recipeingredients')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id', 'tags', 'author', 'ingredients', 'is_favorited',
            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.is_favorited(request.user)

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.is_in_shopping_cart(request.user)


class RecipeCreateSerializer(RecipeSerializer):
    """Serializer for creating and updating recipes."""

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    ingredients = RecipeCreateIngredientsSerializer(
        source='recipeingredients', many=True)

#    class Meta:
#        model = Recipe
#        fields = (
#            'id', 'tags', 'author', 'ingredients', 'is_favorited',
#            'is_in_shopping_cart', 'name', 'image', 'text', 'cooking_time',
#        )
#        extra_kwargs = {field:{'required': True} for field in fields}
#        extra_kwargs = {
#            'tags': {'required': True},
#            'ingredients': {'required': True},
#            'name': {'required': True},
#            'image': {'required': True},
#            'text': {'required': True},
#            'cooking_time': {'required': True},
#        }

    def validate(self, attrs):
        if self._kwargs['context']['request']._request.method == 'POST':
            user = self.context.get('request').user
            # эту ошибку фронтенд выводит
            if Recipe.objects.filter(name=attrs['name'], author=user).exists():
                raise serializers.ValidationError(
                    'You already have a recipe with that name.'
                )
        mandatory_fields = [
            'tags', 'ingredients', 'name', 'image', 'text', 'cooking_time']
        for field_name in mandatory_fields:
            if field_name not in self._kwargs['data']:
                raise serializers.ValidationError(
                    f'The field {field_name} is required.'
                )
        return attrs

    def validate_tags(self, value):
        tags_names = [tag.name for tag in value]
        if len(tags_names) != len(set(tags_names)):
            raise serializers.ValidationError(
                'Unable to add the same tag multiple times.'
            )
        return value

    def validate_ingredients(self, value):
        ingredients_ids = [ingredient['ingredient'].id for ingredient in value]
        # фронтенд не выводит этот error
        if len(ingredients_ids) != len(set(ingredients_ids)):
            raise serializers.ValidationError(
                'Unable to add the same ingredient multiple times.'
            )
        return value

    @transaction.atomic
    def set_recipe_ingredients(self, recipe, ingredients):
        recipe_ingredients = [
            RecipeIngredients(
                recipe=recipe,
                ingredient=current_ingredient['ingredient'],
                amount=current_ingredient['amount'],
            )
            for current_ingredient in ingredients
        ]
        RecipeIngredients.objects.bulk_create(recipe_ingredients)

    @transaction.atomic
    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredients')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        self.set_recipe_ingredients(recipe, ingredients)
        return recipe

    # при patch-запросе через postman позволяет обновить рецепт
    # не со всеми полями, при put-запросе требует все поля
    @transaction.atomic
    def update(self, instance, validated_data):
        # if self._kwargs['context']['request']._request.method == 'PATCH':
        #     self._kwargs['partial'] = False
        #     print(self._kwargs)
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('recipeingredients')
        instance.ingredients.clear()
        instance.tags.clear()
        super().update(instance, validated_data)
        instance.tags.set(tags)
        self.set_recipe_ingredients(instance, ingredients)
        return instance

#    def partial_update(self, request, *args, **kwargs):
#        kwargs['partial'] = False
#        return self.update(request, *args, **kwargs)

    def to_representation(self, instance):
        repr = super().to_representation(instance)
        tag_id_list, tag_list = repr['tags'], []
        for tag_id in tag_id_list:
            tag = get_object_or_404(Tag, id=tag_id)
            serialized_tag = OrderedDict(TagSerializer(tag).data)
            tag_list.append(serialized_tag)
        repr['tags'] = tag_list
        return repr


class RecipeInSubscriptionSerializer(serializers.ModelSerializer):
    """Serializer for displaying recipes on the subscriptions page."""

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

# сейчас через админку можно добавить в favorites один и тот же рецепт
# много раз (запрещено по спеке, наверно стоит запретить на уровне модели БД),
# а также свой собственный рецепт (вроде не запрещено, но стоит уточнить)
# применить validators.UniqueTogetherValidator в сериализаторах для favorites
# и shopping
