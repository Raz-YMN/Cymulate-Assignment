FROM python:3.13-slim

WORKDIR /app
COPY . .

RUN pip install -r requirements.txt

EXPOSE 80

ENTRYPOINT ["fastapi", "run", "main.py", "--port", "8000"]