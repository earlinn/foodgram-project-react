from django_filters import rest_framework as rf_filters
from recipes.models import Favorite, Ingredient, Recipe, ShoppingCart, Tag
from rest_framework import mixins, permissions, status, views, viewsets
from rest_framework.response import Response
from users.models import User

from .permissions import IsAuthorOrReadOnly
from .serializers import (CustomSetPasswordRetypeSerializer,
                          CustomUserCreateSerializer, CustomUserSerializer,
                          IngredientSerializer, RecipeCreateSerializer,
                          RecipeSerializer, TagSerializer)


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


class RecipeFilter(rf_filters.FilterSet):
    """Class for filtering recipes."""

    TAG_CHOICES = tuple([(tag.slug, tag.slug) for tag in Tag.objects.all()])

    tags = rf_filters.MultipleChoiceFilter(
        field_name='tags__slug', choices=TAG_CHOICES)

    class Meta:
        model = Recipe
        fields = ['tags', 'author']


class RecipeViewSet(viewsets.ModelViewSet):
    """Viewset for recipes display."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly, IsAuthorOrReadOnly]
    filter_backends = [rf_filters.DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_queryset(self):
        is_favorited = self.request.query_params.get('is_favorited')
        is_in_shopping_cart = self.request.query_params.get(
            'is_in_shopping_cart')
        user_favorites = Favorite.objects.filter(user=self.request.user)
        user_shopping = ShoppingCart.objects.filter(user=self.request.user)
        # работают даже запросы вида /api/recipes/?is_favorited (без =)
        # запрос вида /api/recipes/?is_favorited=True&is_in_shopping_cart=True
        # фильтрует только по первому параметру, ведь происходит return и
        # выход из данного метода
        if is_favorited is not None:
            print(is_favorited)  # для отладки
            return Recipe.objects.filter(favorites__in=user_favorites)
        if is_in_shopping_cart is not None:
            return Recipe.objects.filter(shopping__in=user_shopping)
        return Recipe.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def get_serializer_class(self):
        if self.action == 'create':
            return RecipeCreateSerializer
        return RecipeSerializer
