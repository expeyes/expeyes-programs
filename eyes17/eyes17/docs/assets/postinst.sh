#!/bin/sh
if [ "$1" = "configure" ]; then
	echo "Setting permissions for examples folder"
	chmod -R 777 /usr/share/kuttypy-gui/examples
fi

echo "Setting User Permissions for USB port for KuttyPy: AVR, FT232 and MCP2200"

echo "SUBSYSTEM==\"usb\",ATTRS{idVendor}==\"03eb\", ATTRS{idProduct}==\"21ff\", MODE=\"666\"" > /etc/udev/rules.d/99-kuttypy.rules
echo "SUBSYSTEM==\"tty\",ATTRS{idVendor}==\"0403\", ATTRS{idProduct}==\"6001\", MODE=\"666\"" >> /etc/udev/rules.d/99-kuttypy.rules
echo "SUBSYSTEM==\"tty\",ATTRS{idVendor}==\"04d8\", ATTRS{idProduct}==\"00df\", MODE=\"666\"" >> /etc/udev/rules.d/99-kuttypy.rules
echo "SUBSYSTEM==\"tty\",ATTRS{idVendor}==\"1a86\", ATTRS{idProduct}==\"7523\", MODE=\"666\"" >> /etc/udev/rules.d/99-kuttypy.rules

echo "ATTRS{idVendor}==\"03eb\", ATTRS{idProduct}==\"21ff\", ENV{ID_MM_DEVICE_IGNORE}=\"1\""  >> /etc/udev/rules.d/99-kuttypy.rules
echo "ATTRS{idVendor}==\"0403\", ATTRS{idProduct}==\"6001\", ENV{ID_MM_DEVICE_IGNORE}=\"1\""  >> /etc/udev/rules.d/99-kuttypy.rules
echo "ATTRS{idVendor}==\"04d8\", ATTRS{idProduct}==\"00df\", ENV{ID_MM_DEVICE_IGNORE}=\"1\""  >> /etc/udev/rules.d/99-kuttypy.rules
echo "ATTRS{idVendor}==\"1a86\", ATTRS{idProduct}==\"7523\", ENV{ID_MM_DEVICE_IGNORE}=\"1\""  >> /etc/udev/rules.d/99-kuttypy.rules

cat /etc/udev/rules.d/99-kuttypy.rules
service udev restart
/etc/init.d/udev restart
echo "Reconnect KuttyPy board on USB Port for permissions to take effect"
