FROM alpine:3.20.2

RUN mkdir -p /logs /fritzbox-monitor /tests
ADD src/*.py /fritzbox-monitor
ADD tests/*.py /tests
ADD requirements.txt /fritzbox-monitor
ADD pytest.ini /
RUN apk add --no-cache python3 py3-pip tree iputils-ping vim tzdata

RUN python -m venv /opt/venv
# Enable venv
ENV PATH="/opt/venv/bin:$PATH"


RUN pip install -r /fritzbox-monitor/requirements.txt

RUN python3 -m pytest

ENTRYPOINT ["python3", "./fritzbox-monitor/fritzbox-monitor.py"]