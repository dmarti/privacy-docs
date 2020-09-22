# build.earth
FROM debian:stable

# install build dependencies, then clean up system packages
RUN apt-get -y update && \
    apt-get -y install build-essential curl pandoc texlive-latex-base && \
    apt-get -y --purge autoremove && \
    apt-get -y clean 

RUN apt-get -y install texlive-fonts-recommended

# Install "mo" to process Mustache templates
# Project info: https://github.com/tests-always-included/mo
RUN curl -sSL https://git.io/get-mo -o /usr/local/bin/mo && chmod a+x /usr/local/bin/mo

WORKDIR /docs

docs:
  COPY --dir . /docs
  SAVE IMAGE

build:
	FROM +docs
	RUN --secret name=+secrets/name --secret addressblock=+secrets/addressblock \
	    --secret ccpa_agent_name=+secrets/ccpa_agent_name \
	    DATE=`date +'%B %d, %Y'` make permission-letter.html
	SAVE ARTIFACT permission-letter.html AS LOCAL permission-letter.html

