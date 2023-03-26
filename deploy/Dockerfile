FROM python:3.9

ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

WORKDIR /test_kanalservis
ENV PYTHONPATH=/test_kanalservis:${PYTHONPATH}

ADD ./requirements.txt /test_kanalservis/requirements.txt
RUN pip install -r requirements.txt

WORKDIR /test_kanalservis


