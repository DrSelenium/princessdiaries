FROM python:3.9-slim

WORKDIR /app

COPY princessdiaries/requirements.txt .

RUN pip install -r requirements.txt

COPY princessdiaries/ .

CMD ["python", "main.py"]
