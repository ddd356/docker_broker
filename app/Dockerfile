FROM python:latest
WORKDIR /code
ADD requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY main.py main.py
COPY migrate.py migrate.py
COPY settings.py settings.py
COPY my_test.py my_test.py
# CMD ["python", "migrate.py"]
CMD ["flask", "--app", "main.py", "run"]
# CMD ["echo", "hello"]