#!/bin/sh
echo "Setting User Permissions for USB port for EXPEYES: AVR, FT232 and MCP2200"

echo "SUBSYSTEM==\"usb\",ATTRS{idVendor}==\"03eb\", ATTRS{idProduct}==\"21ff\", MODE=\"666\"" > /etc/udev/rules.d/99-phoenix.rules
echo "SUBSYSTEM==\"tty\",ATTRS{idVendor}==\"0403\", ATTRS{idProduct}==\"6001\", MODE=\"666\"" >> /etc/udev/rules.d/99-phoenix.rules
echo "SUBSYSTEM==\"tty\",ATTRS{idVendor}==\"04d8\", ATTRS{idProduct}==\"00df\", MODE=\"666\"" >> /etc/udev/rules.d/99-phoenix.rules


echo "ATTRS{idVendor}==\"03eb\", ATTRS{idProduct}==\"21ff\", ENV{ID_MM_DEVICE_IGNORE}=\"1\""  >> /etc/udev/rules.d/99-phoenix.rules
echo "ATTRS{idVendor}==\"0403\", ATTRS{idProduct}==\"6001\", ENV{ID_MM_DEVICE_IGNORE}=\"1\""  >> /etc/udev/rules.d/99-phoenix.rules
echo "ATTRS{idVendor}==\"04d8\", ATTRS{idProduct}==\"00df\", ENV{ID_MM_DEVICE_IGNORE}=\"1\""  >> /etc/udev/rules.d/99-phoenix.rules

cat /etc/udev/rules.d/99-phoenix.rules
service udev restart
/etc/init.d/udev restart
echo "Reconnect EXEYES on USB Port for permissions to take effect"
