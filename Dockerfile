FROM debian:11 as build
ARG VERSION
ARG LIBVERSION
RUN apt-get update
RUN apt-get -y install build-essential wget bzip2 git linux-libc-dev libfreetype6-dev libfontconfig1-dev libcurl4-openssl-dev libjpeg-dev libpugixml-dev libcap-dev ca-certificates
WORKDIR /src
RUN git clone https://github.com/wirbel-at-vdr-portal/librepfunc
WORKDIR /src/librepfunc
RUN git checkout tags/${LIBVERSION}
RUN make -j4
RUN make install
WORKDIR /src
RUN wget https://www.gen2vdr.de/wirbel/w_scan_cpp/w_scan_cpp-${VERSION}.tar.bz2
RUN tar xfv w_scan_cpp-${VERSION}.tar.bz2
WORKDIR /src/w_scan_cpp-${VERSION}
RUN make download
RUN make -j4
FROM debian:11-slim
ARG VERSION
ARG LOCALE
ARG LIBVERSION
WORKDIR /
RUN mkdir -p /usr/include /usr/lib/pkconfig
COPY --from=build /usr/lib/librepfunc.so.${LIBVERSION} /usr/lib/librepfunc.so.${LIBVERSION}
COPY --from=build /usr/lib/pkgconfig/librepfunc.pc /usr/lib/pkgconfig/librepfunc.pc 
COPY --from=build /usr/include/repfunc.h /usr/include/repfunc.h
RUN ln -sfr /usr/lib/librepfunc.so.${LIBVERSION} /usr/lib/librepfunc.so
COPY --from=build /src/w_scan_cpp-${VERSION}/w_scan_cpp .
COPY --from=build /src/w_scan_cpp-${VERSION}.tar.bz2 SOURCE_w_scan_cpp-${VERSION}.tar.bz2
COPY LICENSE .
COPY LICENSE.GPLv2 .
COPY README.md .
RUN DEBIAN_FRONTEND=noninteractive apt-get update && apt-get install -y --no-install-recommends libjpeg62 libcap2 libfreetype6 libfontconfig1 libpugixml1v5 libcurl4 ca-certificates locales && rm -rf /var/lib/apt/lists/*
RUN echo "${LOCALE} UTF-8" > /etc/locale.gen && dpkg-reconfigure --frontend=noninteractive locales && update-locale LANG="${LOCALE}"
ENV LANG ${LOCALE}
ENTRYPOINT ["/w_scan_cpp"]
