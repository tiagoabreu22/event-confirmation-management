FROM python:3.10.0-slim

COPY requirements.txt /


RUN pip3 install -r /requirements.txt



COPY . /app

WORKDIR /app



EXPOSE 5010



CMD ["gunicorn","--config", "gunicorn_config.py", "app:app"]