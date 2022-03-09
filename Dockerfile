FROM openjdk:slim
COPY --from=python:3.10-slim / /

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONNONBUFFERED 1

WORKDIR /code

RUN pip install pipenv
COPY Pipfile Pipfile.lock /code/
RUN pipenv install

COPY . /code/

ENTRYPOINT ["bash", "entrypoint.sh"]
