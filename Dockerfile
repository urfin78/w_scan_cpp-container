FROM debian:11 as build
ARG VERSION
RUN apt-get update
RUN apt-get -y install build-essential wget bzip2 git linux-libc-dev libfreetype6-dev libfontconfig1-dev libcurl4-openssl-dev libjpeg-dev libpugixml-dev libcap-dev ca-certificates
WORKDIR /src
RUN wget https://www.gen2vdr.de/wirbel/w_scan_cpp/w_scan_cpp-${VERSION}.tar.bz2
RUN tar xfv w_scan_cpp-${VERSION}.tar.bz2
WORKDIR /src/w_scan_cpp-${VERSION}
RUN make download
RUN make -j4
FROM debian:11-slim
ARG VERSION
ARG LOCALE
WORKDIR /
COPY --from=build  /src/w_scan_cpp-${VERSION}/w_scan_cpp .
COPY --from=build  /src/w_scan_cpp-${VERSION}.tar.bz2 SOURCE_w_scan_cpp-${VERSION}.tar.bz2
COPY LICENSE .
COPY LICENSE.GPLv2 .
COPY README.md .
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y --no-install-recommends libjpeg62 libcap2 libfreetype6 libfontconfig1 libpugixml1v5 libcurl4 ca-certificates locales && rm -rf /var/lib/apt/lists/*
RUN echo "${LOCALE} UTF-8" > /etc/locale.gen && dpkg-reconfigure --frontend=noninteractive locales && update-locale LANG="${LOCALE}"
ENV LANG ${LOCALE}
ENTRYPOINT ["/w_scan_cpp"]
