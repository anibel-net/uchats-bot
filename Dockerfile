FROM python:3.9-slim

WORKDIR /app
ADD . .

RUN pip install -r requirements.txt

CMD python main.py