FROM python:3.9.5

RUN mkdir /urfub

WORKDIR /urfub

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .