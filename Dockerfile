FROM python:3.12-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app /app/app

ENV DB_PATH=/data/links.db
ENV ADMIN_USERNAME=admin
ENV ADMIN_PASSWORD=change_me
ENV SECRET_KEY=change-this-secret

EXPOSE 8080
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app.main:app"]
