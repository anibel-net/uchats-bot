FROM python:slim

WORKDIR /app
ADD . .

RUN pip install -r requirements.txt

CMD python main.py