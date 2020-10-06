FROM debian:stable

RUN apt-get -y update && \
    apt-get -y install build-essential curl pandoc wkhtmltopdf && \
    apt-get -y --purge autoremove && \
    apt-get -y clean 

# Install "mo" to process Mustache templates
# Project info: https://github.com/tests-always-included/mo
RUN curl -sSL https://git.io/get-mo -o /usr/local/bin/mo && chmod a+x /usr/local/bin/mo

WORKDIR /docs

