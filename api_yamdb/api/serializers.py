from rest_framework import serializers
from datetime import datetime as dt
from django.db.models import Avg

from reviews.models import Category, Genre, Title


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = '__all__'


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = '__all__'


class TitleGetSerializer(serializers.ModelSerializer):
    genre = GenreSerializer(many=True, read_only=True)
    category = CategorySerializer()
    rating = serializers.SerializerMethodField()

    class Meta:
        model = Title
        read_only_fields = '__all__'

    def get_rating(self, obj):
        ratings = obj.ratings.all()
        if ratings.exists():
            average_rating = ratings.aggregate(Avg('rating'))
            return average_rating
        return None


class TitleSerializer(serializers.ModelSerializer):
    genre = serializers.SlugRelatedField(
        slug_field='slug',
        many=True,
        queryset=Genre.objects.all()
    )
    category = serializers.SlugRelatedField(
        slug_field='slug',
        queryset=Category.objects.all()
    )

    class Meta:
        model = Title
        fields = '__all__'

    def validate_year(self, value):
        year_today = dt.date.today().year
        if value > year_today:
            raise serializers.ValidationError('Проверьте год издания!')
        return value
