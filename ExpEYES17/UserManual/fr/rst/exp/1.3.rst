Installation du logiciel
========================

ExpEYES peut fonctionner sur tout ordinateur disposant d'un interpréteur
Python et d'un module Python pour accéder au port série. L'interface
USB est prise en charge par le programme pilote qui présente le port
USB comme un port RS232 aux programmes d'applications. La communication
avec le boîtier expEYES est réalisée à l'aide d'une bibliothèque écrite
en langage Python.

Des programmes avec une interface utilisateur graphique ont été écrits
pour de nombreuses expériences. Le logiciel Eyes17 dépend des paquets
logiciels suivants :

  *  ``python3-serial``
  *  ``python3-numpy``
  *  ``python3-scipy``
  *  ``python3-qt5``
  *  ``python3-pyqtgraph``


Pour toute distribution GNU/Linux :
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Télécharger **eyes17-x.x.x.zip** (la dernière version) depuis
**http://expeyes.in** et dézipper ce fichier, puis aller dans
le nouveau dossier. Taper les commandes ::

    $ sudo sh postinst       # donne la permission d'accès à tous

    $ python main.py

Vous aurez des messages d'erreur pour tout paquet manquant qui pourrait
être nécessaire à expeyes. Installer ces paquets et réessayer. Les
programmes Python nécessaires pour de nombreuses expériences sont
dans le même répertoire, ils sont appelés par ``main.py``.

Distributions GNU/Linux Debian ou Ubuntu
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Télécharger **eyes17-x.x.x.deb** (la dernière version) depuis
la zone de téléchargement de **http://expeyes.in** et l'installer
à l'aide de la commande ::

    $ sudo gdebi eyes17-x.x.x.deb

alors qu'on est connecté à Internet

Le paquet ``eyes17`` (de version supérieure à 3) ne dépend
pas de versions antérieures d'ExpEYES, comme expeyes-junior. Pendant
l'installation ``gdebi`` téléchargera automatiquement et installera
les paquets requis.

**N.B. :** on peut aussi utiliser la commande ::

    $ sudo apt install eyes17

alors qu'on est connecté à Internet ; le paquet ``eyes17`` disponible
dans la distribution (actuellement dans debian/buster ou ubuntu/bionic)
ainsi que toutes ses dépendances sera téléchargé et installé.

Le CD vif expEYES / La clé USB vive
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

L'image ISO qui offre le support pour eyes17 est disponible ICI pour
téléchargement. Créer un DVD ou une clé USB démarrables à l'aide cette
image ISO (télécharger rufus depuis https://rufus.akeo.ie pour faire
ça sous MSWindows)

Éteindre le PC et brancher la clé USB ou insérer le CD vif, puis démarrer
l'ordinateur. Entrer dans le BIOS durant la phase de démarrage, et
faire en sorte que le CD ou la clé USB soit prise en compte comme
premier média de démarrage. Redémarrer en enregistrant ce réglage.
Un bureau apparaîtra et on peut lancer expEYES-17 depuis le menu **Applications->Éducation**->ExpEYES-17.

On peut aussi le lancer depuis un terminal à l'aide de la commande ::

    $ python /usr/share/expeyes/eyes17/main.py


Sous MSWindows
^^^^^^^^^^^^^^

Il faut tout d'abord installer le logiciel pilote pour le convertisseur
USB Série MCP2200, disponible sur le site de Microchip (et aussi disponible
sur le site expeyes). Après installation de ce pilote apparaîtra un
port COM, qu'on peut tester à l'aide du gestionnaire de périphériques
de MSWindows. Ensuite il y a deux options.

Un fichier zip contenant toutes les choses nécessaires pour ExpEYES
est disponible sur le site expeyes, sous le nom ``eyes17win.zip``.
Télécharger et dézipper ce fichier puis lancer ``main.py``
à partir de là. En utilisant cette méthode, on ne pourra pas écrire
soi-même de code Python pour accéder à expeyes ; pour ce faire il
faut installer comme suit :

  *  ``Python version 2.x``
  *  ``python-serial``
  *  ``python-qt4``
  *  ``python-pyqtgraph``
  *  ``python-numpy``
  *  ``python-scipy``

Télécharger le fichier ``eyes17-x.x.x.zip`` (la dernière version)
depuis le site web. En dézippant ce fichier on obtient un dossier
nommé ``**eyes17**``, lancer ``**main.py**``
depuis là.

