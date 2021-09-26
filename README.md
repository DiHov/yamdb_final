# Проект YaMDb
[![example workflow](https://github.com//DiHov/yamdb_final/actions/workflows/main.yml/badge.svg)](https://github.com/DiHov/yamdb_final)

### Описание
Проект YaMDb собирает отзывы пользователей на произведения. Произведения делятся на категории: «Книги», «Фильмы», «Музыка».

### Технологии
- [Python 3.7](https://www.python.org/)
- [Django 3.0.5](https://www.djangoproject.com/) - свободный фреймворк для веб-приложений на языке Python
- [Django REST framework](https://www.django-rest-framework.org/) (DRF) - мощный и гибкий инструмент для построения Web API.
- [Gunicorn](https://gunicorn.org/) - это HTTP-сервер Python WSGI для UNIX.
- [nginx](https://www.nginx.com/) — это HTTP-сервер и обратный прокси-сервер, почтовый прокси-сервер, а также TCP/UDP прокси-сервер общего назначения/

### Запуск проекта в dev-режиме
- Для запуска приложения выполните команды: 
```
docker-compose up
docker-compose exec web python manage.py makemigrations yamdb
docker-compose exec web python manage.py migrate --noinput
``` 
- Для создания суперпользователя выполните команду:
```
docker-compose exec web python manage.py createsuperuser
```

### Авторы
Дмитрий Хижянков