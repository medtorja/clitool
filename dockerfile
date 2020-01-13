FROM ubuntu:latest

RUN apt-get update && \
    apt-get install -y \
        python3 \
        python3-pip \
        python3-setuptools \
        groff \
        less \
    && pip3 install --upgrade pip \
    && apt-get clean

RUN pip3 --no-cache-dir install --upgrade awscli

COPY ./clitool.py ./clitool.py
COPY ./create_test.json ./create_test.json
COPY ./example.json ./example.json
COPY ./requirements.txt ./requirements.txt
COPY ./test.py ./test.py
COPY ./update_test.json ./update_test.json

RUN pip3 install -r /requirements.txt

COPY aws_fake_credentials/credentials ./.aws/credentials
COPY aws_fake_credentials/config ./.aws/config

# Fake credentials for localstack
ENV AWS_SECRET_ACCESS_KEY=fake
ENV AWS_ACCESS_KEY_ID=fake

RUN echo 'alias "cli-tool=python3 /clitool.py"' >> ~/.bashrc

CMD ["/bin/bash"]