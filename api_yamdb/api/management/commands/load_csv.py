import csv
from pathlib import Path

from django.core.management.base import BaseCommand

from reviews.models import Category, Comment, Genre, Review, Title, User

BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


FILES_DIR = BASE_DIR / 'static/data/'


files_func = {
    'category.csv': lambda data: (
        Category,
        [Category(**category) for category in data],
    ),
    'genre.csv': lambda data: (Genre, [Genre(**genre) for genre in data]),
    'titles.csv': lambda data: (
        Title,
        [
            Title(
                id=title['id'],
                name=title['name'],
                year=title['year'],
                category_id=title['category'],
            )
            for title in data
        ],
    ),
    'users.csv': lambda data: (User, [User(**user) for user in data]),
    'review.csv': lambda data: (
        Review,
        [
            Review(
                id=review['id'],
                title_id=review['title_id'],
                text=review['text'],
                author_id=review['author'],
                score=review['score'],
                pub_date=review['pub_date'],
            )
            for review in data
        ],
    ),
    'comments.csv': lambda data: (
        Comment,
        [
            Comment(
                id=comment['id'],
                review_id=comment['review_id'],
                text=comment['text'],
                author_id=comment['author'],
                pub_date=comment['pub_date'],
            )
            for comment in data
        ],
    ),
    'genre_title.csv': None,
}


def load_data():
    """Загружает данные из подготовленных csv в db."""

    for file, get_data in files_func.items():
        with open(FILES_DIR / file, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            if file == 'genre_title.csv':
                for row in reader:
                    title = Title.objects.get(pk=row['title_id'])
                    title.genre.add(row['genre_id'])

            else:
                # Пропускаем заголовок и создаем объекты Category
                model, instances = get_data(reader)
                # Сохраняем объекты в базу данных
                model.objects.bulk_create(instances, ignore_conflicts=True)


class Command(BaseCommand):

    help = 'Load data from csv to .db'

    def handle(self, *args, **options):
        load_data()
