# w_scan_cpp-container
This repo provides a multiarch Docker container for w_scan_cpp.

## Acknowledgments
**w_scan_cpp** itself is written by Winfried Koehler `<nvdec A.T. quantentunnel D.O.T. de>`

You can find the official homepage here: https://www.gen2vdr.de/wirbel/w_scan_cpp/index2.html

It uses parts of the following projects:
* **wirbelscan plugin** by Winfried Koehler (https://www.gen2vdr.de/wirbel/wirbelscan/index2.html)
* **VDR** by Klaus Schmidinger (www.tvdr.de) 
* **VDR satip Plugin** by Rolf Ahrenberg (https://github.com/rofafor/vdr-plugin-satip)  

## Image Tag structure
w_scan_cpp:*architecture*-*locale*

latest == latest-*en_US*

## Available architecures
* `armv6` 
* `armv7` 
* `arm64` 
* `386` 
* `amd64`

## Available locales

* `en_US` 
* `de_DE`

## How to use
You have to make the dvb device available to the docker container with the `--device` option:

```bash
docker run --device /dev/dvb/adapter0 ghcr.io/urfin78/w_scan_cpp:latest-de_DE -fc -cDE
```

# License Info
The Dockerfile and code to build the container is distributed under GPLv3 (see the [license file](LICENSE)).

**w_scan_cpp** by Winfried Koehler and the used parts of:
* **wirbelscan plugin** by Winfried Koehler
* **VDR** by Klaus Schmidinger
* **VDR satip Plugin** by Rolf Ahrenberg

are distributed under GPLv2 (see the [license file](LICENSE.GPLv2)).