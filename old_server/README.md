# **Partie Camera : Procédure d'installation et de configuration**

## **1. Installation de l'OS Raspbian sur rapsberry**
Nous allons installer un OS au raspebrry pi simulant la box. Dans toute la procédure, ce raspberry pi sera nommé rpi_camera.
Afin de faciliter l'accès au dépôt et de bénéficier des derniers correctifs de l'OS raspbian, il est judicieux de prendre la dernière version Bullseye. 
- [raspios_lite_Bullseye](https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2022-04-07/)

**NB** : Cependant cette dernière version a profondément modifié la partie logicielle gérant la caméra. C'est pourquoi, il est recommandé d'installer la dernière version Buster, même s'il semble que la pertinence d'une telle action est à reconsidéré
- Pour rpi_box et rpi_cloud : [raspios_lite_Bullseye](https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2021-11-08/)


Flasher l'image raspios_lite sur la cartes sd du raspberry via l'outil Etcher : https://www.balena.io/etcher/

## **2. Configuration de l'OS Raspbian**

Connectez le rpi_camera par par Ethernet et branchez y un clavier, et un écran via le port HDMI.
Pour accéder aux commandes du raspberrypi, nous avons laissé par défaut (dentifiant : pi et mot de passe : raspberry)

Il est possible de changer le mot de passe (non expliqué dans ce document). Déterminez l'adresse IP du rpi_camera par la commande

`ifconfig`

Notez le. Ensuite, il est important d'activer l'option ssh (désactivé par défaut). Pour cela:

`sudo raspi-config`

Puis activer l'option ssh et  redémarrer par 

` sudo reboot`

Par la suite, l'écran et le clavier ne sont plus utiles. On peut se connecter par SSH via l'outil Putty en indiquant l'adresse ip préalabelement récupérée.

Une fois connecté en  SSH, il est utile si cela est nécessaire, de changer le clavier en mode azerty, on peut le configurer de la manière suivante :

`sudo nano /etc/default/keyboard`			

puis modifier la ligne XKBLAYOUT="gb" par XKBLAYOUT="fr"	

## **3. Installation des packages**

Nous allons ici installer les paquets issues de dépot linux utiles et communs au 3 raspberrypi

    sudo apt update
    sudo apt upgrade
    sudo apt install python3-pip
    sudo apt install dnsmasq
    sudo apt install iptables

## **4. Installation de la bibliothèque cv2**

La bibliothèque cv2 de python est indispensable pour la transmission de la vidéo au raspberrypi voisin. L'installation de cette bibliothèque est assez complexe 
et il est utile d'en décrire les différentes étapes : 

le site : https://qengineering.eu/install-opencv-lite-on-raspberry-pi.html présente les détails de l'installation à suivre à la lettre.

Ensuite, il reste les commandes suivantes : 

`sudo pip3 install opencv-python`

`sudo apt install libatlas3-base`

`sudo pip3 install -U numpy`

Afin de tester la bonne installation de cv2, testons son import : 

`python3`

`import cv2`

Si aucune message d'erreur est visible, la procédure s'est alors bien passée.

### **5. Configuration de la connexion Wifi pour le rpi_camera**

Cette partie vise à configurer la connexion Wifi du rpi_camera, afin qu'elle ne puisse se connecter automatiquement et seulement au rpi_box, créant ainsi le réseau wan
du domicile. Si le rpi_camera est branché sur ethernet, pour que la liaison Wi-FI soit effective, il faudra se déconnecter. Dans le cas où seul la liaison Wi-Fi est effective, le ssh est impossible sauf si le pc se connecte en Wi-FI sur le point d'accès rpi_box. 
			
`sudo nano /etc/network/interfaces`	

Toutes les lignes sont à commenter sauf celles indiquées ci-dessous :
	
```
auto lo		
iface lo inet loopback		
allow-hotplug wlan0 		
auto wlan0		
wpa-conf /etc/wpa_supplicant/wpa_supplicant.conf
```

`sudo nano /etc/wpa_supplicant/wpa_supplicant.conf`


```
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=FR
# AP scanning
ap_scan=1
network={
ssid="rpibox"
psk="mot2passe"
proto=RSN
key_mgmt=WPA-PSK
pairwise=CCMP
auth_alg=OPEN
}	
```
Après un reboot du rpi_camera, ce raspberrypi se connectera automatiquement en wifi sur le rpi_box

## **6. Installation et lancement du serveur Nodejs**

Dans un premier temps, il faut récupérer le répertoire sur GitHub:

`git clone git@github.com:clemanthkar/GreenHomeLan_Camera.git`

Aller dans le répertoire GreenHomeLan/Server_Camera qui correspond à notre environnement de travail pour le rpi_camera. Installer les dépendances suivantes:

`npm init` (valider chaque lignes)

 Puis installation des toutes les dépendances : 

`npm i express`

`npm i onoff`

Pour lancer le serveur camera : 

`node server_camera.js`

## **7. Installation et lancement du programme captureVideo.py**

Ce programme python premet de récupérer les images issue de la camera et des les envoyer sur un serveur. Pour cela, il faut installer les bibliothèques suivantes : 

`sudo pip3 install pybase64`

`python3 -m pip install requests`

On lance le programme de la manière suivante : 

`python3 captureVideo.py`

**NB** : On peut lancer sur une même ligne le serveur et la capture vidéo :

`python3 captureVideo.py & node server_cam.js`

si tout ce passe bien on devrait voir apparaître le log suivant : 

    posting frame : http://127.0.0.1:4000

