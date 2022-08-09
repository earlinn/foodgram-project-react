makemig:
	python manage.py makemigrations

migrate:
	python manage.py migrate

createlocalsu:
	python manage.py createsuperuser --email admin@test.com --username admin -v 3

ingr:
    python manage.py load_ingredients

dumpdb:
	python manage.py dumpdata > fixtures.jsom

loaddb:
	python manage.py loaddata fixtures.jsom

collectstatic:
	python manage.py collectstatic --no-input

start-local:
    migrate loaddb collectstatic createlocalsu

flake:
	flake8 --exclude venv,migrations,settings.py

up-compose:
	docker-compose up -d

build-compose:
	docker-compose up -d --build

stop-compose:
	docker-compose stop

start-compose:
	docker-compose start

makemig-compose:
	docker-compose exec -it web python manage.py makemigrations

migrate-compose:
	docker-compose exec -it web python manage.py migrate

createlocalsu-compose:
	docker-compose exec -it web python manage.py createsuperuser --email admin@test.com --username admin -v 3

dumpdb-compose:
	docker-compose exec -it web python manage.py dumpdata > fixtures.json

loaddb-compose:
	docker-compose exec -it web python manage.py loaddata fixtures.json

ingr-compose:
    docker-compose exec -it web python manage.py load_ingredients
