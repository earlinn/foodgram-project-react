FROM python:3.9-slim
WORKDIR /app
COPY . .
RUN pip3 install -r requirements.txt --no-cache-dir

# How to set ru_RU.UTF-8 locale inside this container

# RUN apt-get update
# RUN apt-get install -y locales locales-all
# ENV LC_ALL ru_RU.UTF-8
# ENV LANG ru_RU.UTF-8
# ENV LANGUAGE ru_RU.UTF-8

CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000"]
