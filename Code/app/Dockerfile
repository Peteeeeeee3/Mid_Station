FROM python:3
WORKDIR /app
ADD . /app

RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get install -y ffmpeg

RUN python -m pip install --upgrade pip
RUN python -m pip install requests
RUN python -m pip install -r requirements.txt

EXPOSE 5000
EXPOSE 1935

CMD ["python", "app.py"]
