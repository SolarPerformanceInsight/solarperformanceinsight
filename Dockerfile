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
COPY api/requirements.txt src/.
RUN pip install --no-cache-dir -r src/requirements.txt

FROM node:14-buster as jsbuild
COPY ./dashboard js
RUN cd js && \
    npm install && \
    npm run build

FROM basepython
COPY . src
RUN cd src && \
    pip install --no-cache-dir wheel && \
    python api/setup.py bdist_wheel && \
    pip install --no-cache-dir api/dist/*.whl && \
    chown -R 1001:0 /opt/app-root && \
    cd && rm -r /opt/app-root/src
COPY --from=jsbuild /js/dist /opt/app-root/static

EXPOSE 8000
USER 1001

CMD ["sh", "-c", "STATIC_DIRECTORY=/opt/app-root/static /opt/app-root/bin/uvicorn solarperformanceinsight_api.main:dev_app"]
