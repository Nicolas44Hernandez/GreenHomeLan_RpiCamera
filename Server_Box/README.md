# **Partie Box : Procédure d'installation et de configuration**

## **1. Installation de l'OS Raspbian sur rapsberry**
Nous allons installer un OS au raspebrry pi simulant la box. Dans toute la procédure, ce raspberry pi sera nommé rpi_box.
Afin de faciliter l'accès au dépôt et de bénéficier des derniers correctifs de l'OS raspbian, il est judicieux de prendre la dernière version Bullseye. 
- [raspios_lite_Bullseye](https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2022-04-07/)


Flasher l'image raspios_lite sur la cartes sd du raspberry via l'outil Etcher : https://www.balena.io/etcher/

## **2. Configuration de l'OS Raspbian**

Connectez le rpi_box par par Ethernet et branchez y un clavier, et un écran via le port HDMI.
Pour accéder aux commandes du raspberrypi, nous avons laissé par défaut (dentifiant : pi et mot de passe : raspberry)


Il est possible de changer le mot de passe (non expliqué dans ce document). Déterminez l'adresse IP du rpi_box par la commande

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

Nous allons ici installer les paquets issues de dépot linux :

`sudo apt update`

`sudo apt upgrade`

`sudo apt install python3-pip` (est ce nécessaire?)

`sudo apt install dnsmasq`

`sudo apt install iptables`



## **4. Configuration du rpi_box en tant que point d'accès Wi-Fi**

le rpi_box doit être configuré comme point d'accès Wi-Fi. Les commandes pour la configuration sont les suivantes :

`sudo apt install hostapd`		

`sudo systemctl unmask hostapd`	

`sudo systemctl enable hostapd	`	

`sudo DEBIAN_FRONTEND=noninteractive apt install -y netfilter-persistent iptables-persistent`	

`sudo reboot`
		
Par la suite, le fichier dhcpcd.conf est configuré pour l'attribution d'une adresse statique

`sudo nano /etc/dhcpcd.conf`

Les 3 lignes de code ci-dessous doit être copier dans le fichier (ctr+x pour sortir du mode nano)

```
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
```

Le rpi_box aura donc une adresse ip fixe wifi dont l'adresse est : 192.168.4.1 en plus de son adresse Ethernet. On peut le vérifier par la commande: 

`sudo ifconfig`

où etho et wlan0 on chacun une adresse ip attribué avec wlan0 valant 192.168.4.1

Ensuite, il faut activer le routage	en éditant un nouveau fichier : 

`sudo nano /etc/sysctl.d/routed-ap.conf`

en copiant/collant cette ligne

```
net.ipv4.ip_forward=1				
```

Les 2 commandes suivent la manière dont le routage du traffic HTTP doit être réaliser par le rpi-box en le redirigeant vers vers le rapsberry pi de la camera dont l'adresse est 192.168.4.12 et sur le port 4000. Cette indication est à modifier si l'adresse IP du raspberry camera est différente.

`sudo iptables -t nat -A PREROUTING -i eth0 -p tcp --dport 4000 -m conntrack --ctstate NEW -j DNAT --to 192.168.4.12:4000`

`sudo iptables -t nat -A PREROUTING -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT`

Puis les 2 commandes suivantes servent à finaliser le routage

`sudo iptables -t nat -A POSTROUTING -o eth0 -j MASQUERADE`

Pour rendre les règles de routage persistente:

`sudo netfilter-persistent save`	


Ensuite, on configure les services DHCP et DNS par les commandes suivantes :

`sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig`
`sudo nano /etc/dnsmasq.conf`

les 4 lignes ci-dessous sont à copier coller dans le fichier dnsmasq.conf en remplacement de l'existant. On indique ici, la plage des adresses IP de tout éléments venant se connecter sur le point d'acceès rpi_box avec une durée de 300 jours. 

```
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,300d
domain=wlan
address=/gw.wlan/192.168.4.1
```

Pour finaliser la configuration du point d'accès, on configure les paramètres réseau en proposant un nom de réseau et un mot de passe		

`sudo nano /etc/hostapd/hostapd.conf`

puis copier coller les lignes ci-dessous. 
```    
interface=wlan0
driver=nl80211
ssid=rpibox
hw_mode=g
channel=7
macaddr_acl=0
wmm_enabled=1
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_passphrase=greenhomelan
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
country_code=FR
```

Puis on indique l'emplacement de la configuration

`sudo nano /etc/default/hostapd`

```
DAEMON_CONF="/etc/hostapd/hostapd.conf"
```

On valide le tout par le redémarrage du rpi-box

`sudo reboot`

Le point d'accès de la rpi_box sera maintenant visible par `rpibox` avec comme mot de passe `greenhomelan` 
(un autre mot de passe est possible du moment qu'il est renseigné dans le fichier hostapd.conf)

## **5. Installation du serveur Nodejs**

Une fois connecté à la box RPI via SSH il ests necessaire d'installer installer NodeJS.

Télécharger NodeJS
```bash
sudo su
curl -fsSL https://deb.nodesource.com/setup_17.x | bash -
``` 

Installer NodeJS
```bash
sudo apt install nodejs
``` 

Verifier l'installation 
``` bash
$ node --version
v17.9.0
$ npm --version
8.5.5
``` 

Installer et configurer git

``` bash
sudo apt install git
git config --global user.name <your user name>
git config --global user.email <your email>
``` 

Créer un clé SSH et l'ajouter au compte github

[Procédure détaillée](https://docs.github.com/es/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account)


Récupérer le répertoire sur GitHub:

```bash
git clone git@github.com:clemanthkar/GreenHomeLan_Camera.git
```

TODO: Delete this after merge
Checkout branch
```bash
git checkout feature/npm_dependencies_in_package_file
```

Aller dans le répertoire GreenHomeLan/Server_Box qui correspond à notre environnement de travail pour le rpi_box. Installer les dépendances:

```bash
cd GreenHomeLan_Camera/Server_Box
npm install
```

Avant de lancer le server il faut renseigner une information contenue dans le fichier config.js

```
MSERV_ADR : {
        "e4:5f:01:0e:34:3f" : "http://192.168.1.29:8000",
        "e4:5f:01:0e:31:ed" : "http://172.16.57.127:8000"
    }
```
L'obejt MSERV_ADR prend comme clé l'adresse mac du rpi-cloud et la valeur l'adresse IP du cloud. Cela signifie que le rpi-cloud doit être entièrement configuré er fonctionnel pour récuéprer ces informations par l'intermédiaire de la commande suivante : 

`sudo arp -a`

Le serveur est ensuite prêt à être lancé : 

`node server_box.js`

A noter qu'il faut lancer le server_box.js au préalable et qu'il faut faire un ping sur le cloud pour favoriser la découverte qui n'est pour l'instant pas systématique.