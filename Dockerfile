FROM alpine:3.20.2

RUN mkdir -p /logs /install
ADD src/*.py /install
ADD requirements.txt install
RUN apk add --no-cache python3 py3-pip tree iputils-ping vim

RUN python -m venv /opt/venv
# Enable venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install -r /install/requirements.txt

ENTRYPOINT ["python3", "./install/fritz.py"]