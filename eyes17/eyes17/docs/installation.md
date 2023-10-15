
## Using PIP  [![PyPI version](https://badge.fury.io/py/eyes17lib.svg)](https://badge.fury.io/py/eyes17lib)

### Windows
```
py -3 -m pip install eyes17lib
```

### Linux
```
pip install eyes17lib
```

## Linux

Accessing the hardware on linux requires certain permissions to be set.
Due to an apparent bug with pip3, the install script may fail to do this.

For a permanent fix for regular users, please download and execute this
[post installation script](../assets/postinst.sh)

```bash
chmod +x postinst.sh
sudo ./postinst.sh
```

*If this is too hard, please install the deb file linked in the following section*

---
!!! success
    This should be sufficient, and you can now proceed to [using the library](../programming/intro)


## On Ubuntu:

### Installing from the deb file
+ download the [latest deb](https://csparkresearch.in/seelab3)
+ use gdebi to install it.

### Installing from the Ubuntu repository  ![Docs](https://img.shields.io/ubuntu/v/eyes17-manuals? color=darkgreen&style=plastic)

+ sudo apt install eyes17

This will install the library as well as the graphical interface for eyes17 

## Installing on windows.

+ To just install the library, the best option is to use pip as shown in the first section.
+ To also install the graphical software, you can pip install the eyes17 package.

!!! info "Install eyes17 [![PyPI version](https://badge.fury.io/py/eyes17.svg)](https://badge.fury.io/py/eyes17)"
	py -3 -m pip install eyes17


