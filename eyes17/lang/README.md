sudo apt-get install qt4-linguist-tools
sudo apt install qttools5-dev-tools
language-pack-fr-base qt5-qmake

language support -> add language -> add the language you need
logout and login

First select the languages you need to translate to


sudo dpkg-reconfigure locales

Then set the locale you want to use

LC_ALL=fr.FR_UTF8
export LC_ALL
