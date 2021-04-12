FROM debian:10 as build
ARG VERSION
RUN apt-get update
RUN apt-get -y install build-essential wget bzip2 git linux-libc-dev libfreetype6-dev libfontconfig1-dev libcurl4-openssl-dev libjpeg-dev libpugixml-dev libcap-dev ca-certificates
WORKDIR /src
RUN wget https://www.gen2vdr.de/wirbel/w_scan_cpp/w_scan_cpp-${VERSION}.tar.bz2
RUN tar xfv w_scan_cpp-${VERSION}.tar.bz2
WORKDIR /src/w_scan_cpp-${VERSION}
RUN make download
RUN make -j4
FROM debian:10-slim
ARG VERSION
WORKDIR /
COPY --from=build  /src/w_scan_cpp-${VERSION}/w_scan_cpp .
RUN apt-get update
RUN apt-get install -y --no-install-recommends libjpeg62 libcap2 libfreetype6 libfontconfig1 libpugixml1v5 libcurl4 ca-certificates
ENTRYPOINT ["/w_scan_cpp"]