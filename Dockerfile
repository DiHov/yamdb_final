FROM python:3.8.5

WORKDIR /code
COPY . /code
RUN pip install -r requirements.txt
<<<<<<< HEAD
CMD gunicorn api_yamdb.wsgi:application --bind 0.0.0.0:8000
=======
CMD gunicorn api_yamdb.wsgi:application --bind 0.0.0.0:8000
>>>>>>> 970a1480d544a9ac27c5a2ab74a2be42af9531eb
