# w_scan_cpp-container

This repo tries to provide a multiarch Docker container for w_scan_cpp.

# How to use

You have to make the dvb device available to the docker container with the `--device` option:

```bash
docker run --device /dev/dvb/adapter0 wscan-cpp:latest -fc -cDE
```

# License Info
The Dockerfile and code to build the container is distributed under GPLv3 (see the [license file](LICENSE)).

w_scan_cpp itself is written by  Winfried Koehler <nvdec A.T. quantentunnel D.O.T. de> and distributed under GPLv2 (see the [license file](LICENSE.GPLv2)).  
You can find the official homepage of the project here: https://www.gen2vdr.de/wirbel/w_scan_cpp/index2.html

w_scan_cpp uses parts from the following projects:

* VDR by Klaus Schmidinger (www.tvdr.de) 
* VDR satip Plugin by Rolf Ahrenberg (https://github.com/rofafor/vdr-plugin-satip)  

which are also distributed under GPLv2 (see the [license file](LICENSE.GPLv2)).