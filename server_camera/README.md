# Install nmap
Install nmap for ip autmatic discover

```bash
sudo apt install -y nmap
```

# TODO: complete readme file

Create logfiles

Log files defined in configuration file located in *server_box/server/config/logging-config.yml* must be created before launching the application

```bash
mkdir logs
mkdir logs/manager
mkdir logs/interface
mkdir logs/notification
touch logs/app.log logs/api-rest.log
touch logs/manager/thread.log logs/manager/doorbell.log logs/manager/video.log logs/manager/wifi_connection.log logs/manager/ip_discovery.log
touch logs/interface/gpio.log logs/interface/thread.log logs/interface/video_capture.log
touch logs/notification/cloud_notifier.log
```



## **Set the rpi-camera application as a service**

Copy the service file
```bash
sudo cp server_camera/service/rpi-camera.service /etc/systemd/system/
```

Register service
```bash
sudo systemctl daemon-reload
sudo systemctl enable rpi-camera
sudo systemctl restart rpi-camera
```
