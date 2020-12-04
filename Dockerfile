FROM python:3.8-buster as basepython

WORKDIR /opt/app-root/
ENV PATH=/opt/app-root/bin:$PATH


RUN curl -LsSO https://downloads.mariadb.com/MariaDB/mariadb-keyring-2019.gpg && \
    curl -LsS https://downloads.mariadb.com/MariaDB/mariadb-keyring-2019.gpg.sha256 | sha256sum -c --quiet  && \
    mv mariadb-keyring-2019.gpg /etc/apt/trusted.gpg.d/ && \
    echo \
    'deb http://downloads.mariadb.com/MariaDB/mariadb-10.5/repo/debian buster main\n\
    deb http://downloads.mariadb.com/Tools/debian buster main\n' \
    > /etc/apt/sources.list.d/mariadb.list && \
    apt-get update && \
    apt-get install -y mariadb-client-10.5 libmariadb3 && \
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
    npm install && \
    npm run build

FROM basepython as wheelbuild
COPY . /src
RUN cd /src/api && \
    apt-get install git && \
    apt-get clean && \
    pip install --no-cache-dir wheel && \
    python setup.py bdist_wheel

FROM amacneil/dbmate:v1.11.0 as dbmate

FROM basepython
COPY --from=wheelbuild /src/api/dist/*.whl /opt/app-root/.
COPY --from=wheelbuild /src/db/migrations /opt/app-root/migrations
COPY --from=wheelbuild /src/db/migrate /opt/app-root/bin/migrate
COPY --from=dbmate /usr/local/bin/dbmate /opt/app-root/bin/dbmate
RUN pip install --no-cache-dir /opt/app-root/*.whl
COPY --from=jsbuild /js/dist /opt/app-root/static


EXPOSE 8000
USER 1001

CMD ["sh", "-c", "STATIC_DIRECTORY=/opt/app-root/static /opt/app-root/bin/python -m solarperformanceinsight_api.devapp"]
