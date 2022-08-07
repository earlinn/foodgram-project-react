from django.shortcuts import get_object_or_404
from django_filters import rest_framework as rf_filters
from recipes.models import Favorite, Ingredient, Recipe, Tag
from rest_framework import mixins, permissions, status, views, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from users.models import Subscription, User

from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (CustomSetPasswordRetypeSerializer,
                          CustomUserCreateSerializer, CustomUserSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeLightSerializer, RecipeSerializer,
                          SubscriptionSerializer, TagSerializer)


class UserViewSet(
    mixins.CreateModelMixin, mixins.ListModelMixin,
    mixins.RetrieveModelMixin, viewsets.GenericViewSet
):
    """Viewset for users registration and displaying."""

    queryset = User.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [permissions.AllowAny]

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        return CustomUserSerializer

    @action(detail=False, permission_classes=[permissions.IsAuthenticated])
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={
                'request': request,
                'format': self.format_kwarg,
                'view': self
            }
        )
        return self.get_paginated_response(serializer.data)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated]
    )
    def subscribe(self, request, pk):
        author = get_object_or_404(User, id=pk)
        subscription = Subscription.objects.filter(
            user=request.user, author=author)
        if request.method == 'DELETE' and not subscription:
            return Response(
                {"errors": "Unable to delete non-existent subscription."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE':
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if subscription:
            return Response(
                {"errors": 'You are already following this user.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if author == request.user:
            return Response(
                {"errors": "Unable to subscribe to yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )
        Subscription.objects.create(user=request.user, author=author)
        serializer = SubscriptionSerializer(
            author,
            context={
                'request': request,
                'format': self.format_kwarg,
                'view': self
            }
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class SelfUserView(views.APIView):
    """View class for the current user displaying."""

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = CustomUserSerializer(
            request.user,
            context={
                'request': request,
                'format': self.format_kwarg,
                'view': self
            }
        )
        return Response(serializer.data, status=status.HTTP_200_OK)


class SetPasswordRetypeView(views.APIView):
    """View class for changing current user's password."""

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = CustomSetPasswordRetypeSerializer(
            data=request.data,
            context={
                'request': request,
                'format': self.format_kwarg,
                'view': self
            }
        )
        if serializer.is_valid():
            self.request.user.set_password(serializer.data["new_password"])
            self.request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for tags display."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Viewset for ingredients display."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None
    filter_backends = [rf_filters.DjangoFilterBackend]
    filterset_class = IngredientFilter


class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset for recipes."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [rf_filters.DjangoFilterBackend]
    filterset_class = RecipeFilter

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return RecipeCreateSerializer
        return RecipeSerializer

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=[permissions.IsAuthenticated]
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        favorite = Favorite.objects.filter(recipe=recipe, user=request.user)
        if request.method == 'DELETE' and not favorite:
            return Response(
                {"errors": "This recipe was not on your list."},
                status=status.HTTP_400_BAD_REQUEST
            )
        if request.method == 'DELETE':
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        if favorite:
            return Response(
                {"errors": 'This recipe was already on your list.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Favorite.objects.create(user=request.user, recipe=recipe)
        serializer = RecipeLightSerializer(
            recipe,
            context={
                'request': request,
                'format': self.format_kwarg,
                'view': self
            }
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)
