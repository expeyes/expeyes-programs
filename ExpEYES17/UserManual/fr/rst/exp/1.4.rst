Le programme graphique principal
================================

Démarrer Applications->Éducation->ExpEYES-17 depuis le menu. Un écran
d'oscilloscope à quatre canaux avec de nombreuses fonctionnalités
en plus, s'ouvrir comme affiché sur la figure \ref{fig:The-scope17-screen}.
On peut choisir de nombreuses expériences depuis le menu.

.. figure:: pics/scope17.*

    L'écran scope17 affichant deux traces \label{fig:The-scope17-screen}


La fenêtre principale apparaît comme un oscilloscope à basse fréquence
avec quatre canaux, et plusieurs fonctionnalités en plus, à droite
de l'écran. On peut sélectionner des applications pour plusieurs expériences
du menu de la barre supérieure. Une brève description du programme
d'oscilloscope est donnée ci-dessous.

  * On peut activer chacune des quatre entrées (A1, A2, A3 ou MIC) en
    utilisant sa case à cocher. On peut sélectionner les calibres en cliquant
    sur le bouton à menu à droite de la case à cocher. Le calibre voulu
    se choisit dans le menu surgissant.
  * Il y a une autre case à cocher pour activer l'ajustement mathématique
    des données à l'aide d'un
    modèle :math:`V = V_{0} \sin (2\pi ft + \theta) + C`
    pour afficher l'amplitude et la fréquence.
  * L'échelle horizontales (la base de temps) peut être réglées par un
    curseur, depuis 0,5 ms pleine échelle jusqu'à 500 ms pleine échelle.
  * Le bouton à cocher **Geler**, permet de faire une pause ou de
    revenir à la marche normale de l'oscilloscope.
  * Le niveau de synchronisation (trigger) peut être réglé grâce à un
    curseur, et il y a un bouton à menu pour sélectionner la source de
    synchronisation.
  * Pour enregistrer les traces dans un fichier, éditer le nom de fichier
    voulu est cliquer le bouton **Enregistrer sous**.
  * Quand on clique sur **FFT** les spectres de fréquence des canaux
    sélectionnés sont affichés dans des fenêtres surgissantes.

En plus de l'oscilloscope, il y a plusieurs options de contrôle/mesure
disponibles dans l'interface utilisateur, qui sont expliqués ci-dessous :

  *  Si on les sélectionne, les tensions présentes aux entrées A1, A2 et
     A3 sont échantillonnées chaque seconde et affichées.
  *  La résistance connectée entre SEN et GND est mesurée et affiché chaque
     seconde.
  *  Si on clique **Capacité en IN1**, on mesure la valeur du condensateur
     connecté entre IN1 et GND.
  *  Si on clique **Fréquence en IN2**, on mesure la fréquence d'une
     source externe (au standard TTL) connectée à IN2
  *  On peut choisir la forme du générateur de signal WG à l'aide d'un
     bouton de menu, la forme par défaut étant sinusoïdale. On peut
     changer en triangulaire. Quand l'option de signal carré est
     choisie, la sortie est déplacée sur SQ2. On ne peut pas utiliser
     un signal sinusoïdal/triangulaire et utiliser SQ2 en même temps.
  *  On peut ajuster la fréquence du signal de WG à l'aide du curseur ou
     bouton de menu, la forme par défaut étant sinusoïdale. On peut changer
     avec l'entrée texte. Les deux méthodes de saisie sont asservies l'une
     à l'autre : quand on bouge le curseur le texte est modifié, et quand
     on saisit un texte le curseur s'ajuste. La fréquence s'ajuste à la
     plus proche valeur possible et elle est affichée dans la fenêtre de
     message dessous. L'amplitude de la sortie WG peut être réglée à 3 V,
     1 V ou 80 mV.
  *  On peut régler SQ1 en utilisant la même méthode que ci-dessus. Le
     rapport cyclique peut être réglé entre 1\% et 99\%, sa valeur par
     défaut est 50\%.
  *  Les deux sorties de tension programmables PV1 et PV2 sont aussi réglées
     d'une façon similaire.
  *  Des boutons à cocher sont fournis pour contrôler OD1 et CCS.


