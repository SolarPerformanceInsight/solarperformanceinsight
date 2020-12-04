FROM amacneil/dbmate:v1.11.0 as dbmate

WORKDIR /opt/app-root/
ENV PATH=/opt/app-root/bin:$PATH

FROM debian:bullseye
# for compatible mysql cli

RUN apt-get update && \
    apt-get install -y mariadb-client-10.5 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    mkdir -p /opt/app-root/bin

COPY --from=dbmate /usr/local/bin/dbmate /opt/app-root/bin/dbmate
COPY ./migrations /opt/app-root/migrations
COPY migrate /opt/app-root/bin/migrate

CMD /opt/app-root/bin/migrate
