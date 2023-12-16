- docker compose build
- docker compose run django python manage.py makemigrations panocam_app
- docker compose run django python manage.py migrate
- docker compose run django python manage.py createsuperuser
- docker compose up

ENV
- P0STGRES_DBNAME
- POSTGRES_USER
- POSTGRES_PASSWORD
- POSTGRES_HOST
- POSTGRES_PORT
- SECRET_KEY
- DJANGO_HOST
- DJANGO_PORT