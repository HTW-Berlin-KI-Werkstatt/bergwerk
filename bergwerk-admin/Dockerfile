FROM python:3.11

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

WORKDIR /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]
