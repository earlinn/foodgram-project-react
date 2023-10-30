# Сайт Foodgram "Продуктовый помощник"

![foogram_react workflow](https://github.com/earlinn/foodgram-project-react/actions/workflows/foodgram_workflow.yml/badge.svg)

## _Онлайн-сервис для публикации рецептов_

### Описание проекта Foodgram

На сайте "Продуктовый помощник" пользователи смогут публиковать рецепты, 
подписываться на публикации других пользователей, добавлять понравившиеся 
рецепты в «Избранное», а перед походом в магазин скачивать в виде pdf-файла 
сводный список продуктов, необходимых для приготовления одного или нескольких 
выбранных блюд.
На сайте доступна система регистрации и авторизации пользователей. 
Неавторизованным пользователям доступен просмотр рецептов на главной странице 
с фильтрацией по тегам, страниц отдельных рецептов и страниц других 
пользователей.
Фронтенд и бекенд взаимодействуют через API.
Проект запускается в трёх Docker-контейнерах (nginx, PostgreSQL и Django) 
через docker-compose. Четвертый контейнер (frontend) используется лишь для 
подготовки файлов.

### Локальный запуск приложения в контейнерах

_Важно: при работе в Linux или через терминал WSL2 все команды нужно выполнять от суперпользователя — начинайте каждую команду с sudo._

_Важно: если вы используете [официальные версии Docker и docker compose](https://docs.docker.com/get-started/08_using_compose/), то в командах docker compose слова "docker" и "compose" следует писать через пробел, а не через тире._

Склонировать репозиторий на свой компьютер и перейти в корневую папку:
```
git clone git@github.com:earlinn/foodgram-project-react.git
cd foodgram-project-react
```

Создать в корневой папке и внутри папки infra файл .env с переменными окружения, необходимыми 
для работы приложения.

Пример содержимого файла:
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DB_HOST=db
DB_PORT=5432
SECRET_KEY=key
```

Перейти в папку /infra/ и запустить сборку контейнеров с помощью 
docker-compose: 
```
cd infra
docker-compose up -d
```
После этого будут созданы и запущены в фоновом режиме контейнеры 
(db, web, nginx).

Внутри контейнера web выполнить миграции, создать суперпользователя (для входа 
в админку), собрать статику и загрузить ингредиенты из recipes_ingredients.csv 
в базу данных:
```
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
docker-compose exec web python manage.py collectstatic --no-input
docker-compose exec web python manage.py load_ingredients
```
После этого проект должен стать доступен по адресу http://localhost/.

Для подготовки сайта к работе нужно зайти в админ-зону по адресу 
http://localhost/admin/ и создать теги для рецептов, указав для каждого тега 
его название, цветовой HEX-код (например, #49B64E) и slug (на английском). 
По этим тегам далее можно будет фильтровать рецепты на страницах сайта.
Цветовые HEX-коды можно посмотреть тут - https://colorscheme.ru/html-colors.html

### Остановка контейнеров

Для остановки работы приложения можно набрать в терминале команду Ctrl+C 
либо открыть второй терминал и воспользоваться командой
```
docker-compose stop 
```
Снова запустить контейнеры без их пересборки можно командой
```
docker-compose start 
```

### Спецификация API в формате Redoc:

Чтобы посмотреть спецификацию API в формате Redoc, нужно локально запустить 
проект и перейти на страницу http://localhost/api/docs/

### Запуск на сервере с другим IP

Заменить IP-адрес в infra/nginx.conf, на Github в разделе 
settings/secrets/actions (переменная HOST), а также в последней строке данного 
README и файле settings.py (где указан IP).

Зайти на сервер и остановить службу nginx командой
```
sudo systemctl stop nginx 
```
Обновить на сервере файлы docker-compose.yml и nginx.conf, если в 
них были изменения. Для этого в терминале локального компьютера (не сервера) 
выполнить команды копирования (потребуется ввести пароль для доступа к 
серверу):
```
# копирует файл docker-compose.yml в домашнюю директорию на сервере
scp -r /{имя диска}/{путь к папке}/foodgram-project-react/infra/docker-compose.yml {имя пользователя}@{публичный IPv4}:~/
# копирует файл default.conf в папку /nginx/ домашней директории на сервере
scp -r /{имя диска}/{путь к папке}/foodgram-project-react/infra/nginx.conf {имя пользователя}@{публичный IPv4}:/home/{имя пользователя}/nginx/ 
```
Сделать коммит, зайти на вкладку Actions репозитория на GitHub и проверить, 
что workflow запустился и выполнил все jobs.

### Используемые технологии

Python 3.9, Django 4.0, Django REST Framework, reportlab, Djoser, React, 
PostgreSQL, Docker, nginx, gunicorn, flake8, GitHub Actions (CI/CD).

### Авторы проекта

[Волкова Галина](https://github.com/earlinn) и [Яндекс.Практикум](https://practicum.yandex.ru/)

### Посмотреть готовый проект

Проект доступен по адресу: https://foodgram-earlinn.sytes.net/
