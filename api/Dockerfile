FROM python:3.8-buster as basepython

WORKDIR /opt/app-root/
ENV PATH=/opt/app-root/bin:$PATH

RUN apt-get update && \
    apt-get install -y default-mysql-client git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    /usr/local/bin/python -m venv /opt/app-root/ && \
    /opt/app-root/bin/pip install -U pip && \
    useradd -m -N -u 1001 -s /bin/bash -g 0 user && \
    chown -R 1001:0 /opt/app-root && \
    chmod -R og+rx /opt/app-root
COPY requirements.txt src/.
RUN pip install --no-cache-dir -r src/requirements.txt

FROM basepython
COPY . src/.
RUN pip install src/. && \
    chown -R 1001:0 /opt/app-root

EXPOSE 8000
USER 1001

CMD ["/opt/app-root/bin/uvicorn", "solarperformanceinsight_api.main:app"]
