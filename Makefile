makemig:
	cd backend/foodgram; python3 manage.py makemigrations

migrate:
	cd backend/foodgram; python3 manage.py migrate

createlocalsu:
	cd backend/foodgram; python3 manage.py createsuperuser --email admin@test.com --username admin -v 3

ingr:
	cd backend/foodgram; python3 manage.py load_ingredients

dumpdb:
	cd backend/foodgram; python3 manage.py dumpdata --output fixtures.jsom

loaddb:
	cd backend/foodgram; python3 manage.py loaddata fixtures.jsom

collectstatic:
	cd backend/foodgram; python3 manage.py collectstatic --no-input

start-local:
	migrate loaddb collectstatic createlocalsu

flake:
	flake8 --exclude venv,migrations,settings.py

up-compose:
	cd infra; sudo docker-compose up -d

build-compose:
	cd infra; sudo docker-compose up -d --build

stop-compose:
	cd infra; sudo docker-compose stop

start-compose:
	cd infra; sudo docker compose start

makemig-compose:
	cd infra; sudo docker-compose exec -it web python manage.py makemigrations

migrate-compose:
	cd infra; sudo docker-compose exec -it web python manage.py migrate

createlocalsu-compose:
	cd infra; sudo docker-compose exec -it web python manage.py createsuperuser --email admin@test.com --username admin -v 3

dumpdb-compose:
	cd infra; sudo docker-compose exec -it web python manage.py dumpdata --output fixtures.json

loaddb-compose:
	cd infra; sudo docker-compose exec -it web python manage.py loaddata fixtures.json

ingr-compose:
	cd infra; sudo docker-compose exec -it web python manage.py load_ingredients
