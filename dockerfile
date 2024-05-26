FROM python:3.9-slim

WORKDIR /ulMeinBot

COPY requirements.txt /ulMeinBot

RUN pip install --no-cache-dir -r requirements.txt

COPY . /ulMeinBot

CMD [ "python", "start.py"]