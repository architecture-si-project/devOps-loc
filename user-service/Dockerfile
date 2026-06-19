FROM python:3.13-slim

RUN useradd --create-home appuser
WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --only-binary :all: -r requirements.txt

COPY user_app/ user_app/
COPY main.py .

USER appuser
EXPOSE 5000

CMD ["python", "main.py"]
