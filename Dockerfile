FROM ubuntu:16.04

RUN mkdir /code
WORKDIR /code

COPY data_code /code/

RUN apt-get update
RUN apt-get install -y curl python nano
RUN apt-get install -y python-pip

RUN apt-get install -y python-dev libldap2-dev libsasl2-dev libssl-dev libpq-dev

RUN pip install --upgrade pip
RUN pip install gunicorn
RUN pip install -r requirements.txt

EXPOSE 8000

CMD ["/bin/bash"]
