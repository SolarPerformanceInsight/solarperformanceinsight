FROM python:3.8-buster as basepython

WORKDIR /opt/app-root/
ENV PATH=/opt/app-root/bin:$PATH

RUN apt-get update && \
    apt-get install -y default-mysql-client && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    /usr/local/bin/python -m venv /opt/app-root/ && \
    /opt/app-root/bin/pip install -U pip && \
    useradd -m -N -u 1001 -s /bin/bash -g 0 user && \
    chown -R 1001:0 /opt/app-root && \
    chmod -R og+rx /opt/app-root
COPY api/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && \
    rm requirements.txt

FROM node:14-buster as jsbuild
COPY ./dashboard js
RUN cd js && \
    npm install --production && \
    npm run build

FROM basepython as wheelbuild
COPY . /src
RUN cd /src/api && \
    apt-get install git && \
    apt-get clean && \
    pip install --no-cache-dir wheel && \
    python setup.py bdist_wheel

FROM basepython
COPY --from=wheelbuild /src/api/dist/*.whl /opt/app-root/.
RUN pip install --no-cache-dir /opt/app-root/*.whl
COPY --from=jsbuild /js/dist /opt/app-root/static

EXPOSE 8000
USER 1001

CMD ["sh", "-c", "STATIC_DIRECTORY=/opt/app-root/static /opt/app-root/bin/uvicorn solarperformanceinsight_api.main:dev_app"]
