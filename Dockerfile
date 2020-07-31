FROM python:3

RUN pip install --upgrade pip && \
    pip install --no-cache-dir nibabel pydicom matplotlib pillow && \
    pip install --no-cache-dir med2image

# As per https://docs.docker.com/develop/develop-images/dockerfile_best-practices/

COPY requirements.txt /tmp
RUN pip install --requirement /tmp/requirements.txt
COPY . /tmp/

RUN mkdir /opt/wsb/
COPY grapher.py market_scanner.py stocklist.py /opt/wsb/

RUN mkdir /opt/wsb/data
COPY data /opt/wsb/data
