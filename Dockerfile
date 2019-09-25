FROM joyzoursky/python-chromedriver:3.7

WORKDIR /var/project
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD tests/ tests/
ADD config.py config.py
RUN mkdir logs
ENTRYPOINT bash
