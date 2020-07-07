# https://pythonspeed.com/articles/pipenv-docker/
FROM python:3.8

ENV APP /app
RUN mkdir $APP
WORKDIR $APP

RUN pip install pipenv

COPY Pipfile* ./
RUN pipenv lock --requirements > requirements.txt
RUN pip install -r requirements.txt

ADD https://github.com/ufoscout/docker-compose-wait/releases/download/2.2.1/wait /wait
RUN chmod +x /wait

# CMD flask run exampleapp:app
# Dependency stuff
# RUN bundle install 

# Copy ./run.sh into here
# COPY . /code 



