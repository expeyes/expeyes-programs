.. eyes17 documentation master file, created by
   sphinx-quickstart on Sat Jan  6 00:43:37 2018.


Manuel Utilisateur d'expEYES-17
*******************************

Introduction
============

La science est l'étude du monde physique par des observations systématiques
et des expériences. Une bonne éducation scientifique est essentielle
pour cultiver une société où le raisonnement et la pensée logique
prévalent au lieu de la superstition et des croyances irrationnelles.
L'éducation scientifique est aussi essentielle pour former suffisamment
de techniciens, d'ingénieurs et de scientifiques pour l'économie du
monde moderne. On admet largement que l'expérience personnelle issue
d'expérimentations et d'observations réalisées soit par les étudiants,
soit par des enseignants à titre de démonstration, soit essentielle
à la pédagogie de la science. Cependant, presque partout la science
est enseignée en grande partie à partir de livres de cours sans donner
d'importance à l'expérimentation, en partie à cause du manque d'équipements.
Sans surprise, la plupart des étudiants échouent à corréler leurs
connaissance acquise en classe aux problèmes rencontrés dans la vie
quotidienne. On peut jusqu'à un certain point corriger cela en enseignant
la science à l'aide de questionnements et d'expériences.

L'avènement des ordinateurs personnels et leur banalisation a ouvert
une nouvelle voie pour faire des expériences de laboratoire. L'ajout
d'un peu de matériel à un ordinateur ordinaire peut le convertir en
un laboratoire de sciences. Réaliser des mesures rapides avec une
bonne précision autorise l'étude une large palette de phénomènes.
Les expériences scientifiques impliquent en général la mesure et le
contrôle de certains paramètres physiques comme la température, la
pression, la vitesse, l'accélération, la force, la tension, le courant,
etc. Si la grandeur physique étudiée évolue rapidement, il faut automatiser
la mesure et un ordinateur devient utile. Par exemple, comprendre
la variation de la tension alternative du secteur nécessite de la
mesurer à chaque milliseconde.

La possibilité de réaliser des expériences avec une précision raisonnable
ouvre aussi la possibilité d'une éducation scientifique orientée sur
la recherche. Les étudiants peuvent comparer les données expérimentales
avec des modèles mathématiques et examiner les lois fondamentales
qui régissent de nombreux phénomènes. Le kit expEYES ( expEriments
for Young Engineers & Scientists) est conçu pour permettre une grande
variété d'expériences, de l'école à l'université. Il est aussi utilisable
comme un équipement de test pour des ingénieurs en électronique ou
des bricoleurs. L'architecture simple et ouverte d'expEYES permet
aux utilisateurs de développer de nouvelles expériences, sans rentrer
dans les détails de l'électronique et de la programmation d'ordinateurs.
Ce manuel utilisateur décrit *expEYES-17* avec plusieurs expériences,
et il y a aussi un manuel du programmeur.

.. toctree::
   :maxdepth: 1

   1.2
   1.3
   1.4
   1.5
	 
Expériences « scolaires »
=========================

Dans ce chapitre on discutera des expériences et démonstrations sans
beaucoup d'analyse des données, qui sont comprises dans le menu
« Expériences scolaires ». Des tâches simples comme mesurer une
tension, une résistance, une capacité, etc. seront faites en utilisant
des résistances variant avec la température ou la lumière. Le concept
de courant alternatif est introduit en traçant la courbe d'une tension
en fonction du temps. La génération et la numérisation d'un son seront
pris en compte. Quand une expérience est sélectionnée, la fenêtre
d'aide correspondante surgit, si on l'y a autorisée.

.. toctree::
   :maxdepth: 1

   2.1
   2.2
   2.3
   2.4
   2.5
   2.6
   2.7
   2.8
   2.9
   2.10
   2.11
   2.12
   2.13
   2.14
   2.15
   2.16
   2.17
   2.18
   2.19
   2.20
   2.21

Expériences d'électronique
==========================

Ce chapitre explique plusieurs expériences d'électronique. La plupart
d'entre elles sont faites avec l'interface utilisateur
oscilloscope. Certaines d'entre elles comme les caractéristiques d'une
diode ou d'un transistor ont leur interface utilisateur dédiée.

.. toctree::
   :maxdepth: 1

   3.1
   3.2
   3.3
   3.4
   3.5
   3.6
   3.7
   3.8
   3.9
   3.10
   3.11
   3.12
   3.13
   3.14
   3.15

Expériences d'électricité et magnétisme
=======================================

Ce chapitre contient principalement des expériences sur le
comportement en régime stationnaire et en régime transitoire pour des
dipôles RLC. Il confronte les résultats expérimentaux avec la
théorie. Il donne aussi une expérience sur l'induction
électromagnétique.

.. toctree::
   :maxdepth: 1

   4.1
   4.2
   4.3
   4.4
   4.5
   4.4
   4.6
   4.7
   4.8

Expériences sur le son
======================

Les variations de pression, de part et d'autres d'une pression
d'équilibre, transmises par un milieu s'appellent un son. Ce sont des
ondes longitudinales. Si on déplace une feuille de papier d'avant en
arrière dans l'air on peut générer ce type d'ondes de pression, comme
avec le cône en papier d'un haut-parleur. Quand la fréquence est dans
l'intervalle de 20 à 20000 Hz, on peut entre le son. Dans ce chapitre,
on va générer du son à partir de signaux électriques, le détecter à
l'aide du microphone (un capteur de pression !) et étudier des
propriétés telles que l'amplitude et la fréquence. La vitesse du son
est mesurée en observant le déphasage d'un son numérisé, avec la
distance.

.. toctree::
   :maxdepth: 1

   5.1
   5.2
   5.3

Expériences de mécanique
========================

Les phénomènes de résonance sont étudiés avec le pendule forcé. On
mesure la valeur de l'accélération due à la pesanteur à l'aide d'un
pendule

.. toctree::
   :maxdepth: 1

   6.1
   6.2
   6.3
   6.4
   6.5

Autres expériences
==================
.. toctree::
   :maxdepth: 1

   7.1
   7.2
   7.3

Modules I2C
===========
.. toctree::
   :maxdepth: 1

   8.1
   8.2
   8.3
   8.4



Coder en Python pour expEYES-17
===============================

.. toctree::
   :maxdepth: 3

   9.0
