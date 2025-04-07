FROM python:3.11.9-slim

RUN apt update
RUN mkdir "/social"

WORKDIR /social

COPY ./src ./src
COPY ./requirements.txt ./requirements.txt

RUN python -m pip install --upgrade & pip install -r ./requirements.txt

CMD ["sh", "-c", "cd src && python manage.py migrate && python manage.py runserver 0:8000"]
