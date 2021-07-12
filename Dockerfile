FROM joyzoursky/python-chromedriver:3.7-selenium

WORKDIR /var/project
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
ADD tests/ tests/
ADD config.py config.py
ADD .flake8 .flake8
ADD setup.cfg setup.cfg
ADD pytest.ini pytest.ini
ADD Makefile Makefile
RUN mkdir logs
ENTRYPOINT bash
