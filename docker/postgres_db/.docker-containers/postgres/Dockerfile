FROM postgres:15-alpine

LABEL maintainer="Viachaslau Kazakou <via.kazakou@gmail.com>"

# add docker user and group first to make sure their IDs get assigned consistently, regardless of whatever dependencies get added
RUN addgroup -S docker && adduser -S -G docker docker

# Copy configure script
COPY configure.sh /docker-entrypoint-initdb.d/configure.sh

RUN chmod 755 /docker-entrypoint-initdb.d/configure.sh
