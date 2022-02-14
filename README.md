# A fork of [GarageWeb by shrocky2](https://github.com/shrocky2/GarageWeb)
### This fork works with Homekit via a [Homebridge plugin](https://www.npmjs.com/package/homebridge-garage-door-shelly1) for a Shelly1 relay switch.
**NOTE: I had to set the timeout to 30000 manually in config.json**

---
#### YouTube Video Instructions found here: https://youtu.be/Fcx6wANw9KM
#### Products they used in the video:
---
- Raspberry Pi Zero W with case on Amazon: https://amzn.to/34ujK5C
- Raspberry Pi Zero W on Adafruit: https://www.adafruit.com/product/3400
- 4 Channel Relay (to Open Garage Door): https://amzn.to/3b4lHbD
- Magnetic Reed Switch (You need 2): https://amzn.to/39YG7kU
- Jumper/Breadboard wire 120ct: https://amzn.to/2V3fFlV
- Hammer Header & Install Kit on Amazon: https://amzn.to/3b5RbxX
- Hammer Headers on Adafruit: https://www.adafruit.com/product/3662
---
#### Setup Instructions:
---
1. First setup your Raspberry Pi: https://www.youtube.com/watch?v=EeEU_8HG9l0 
2. Lets upgrade the apt-get program: 
`sudo apt update`

3. Next install the Flask Web Server: 
`sudo apt install python3-flask` 

4. Install the GIT application so you can download my Github code: 
`sudo apt install git` 

5. Download the Github code:
```
cd
git clone https://github.com/rchiechi/GarageWeb
```
 
**NOTE: It is important that you clone the repo to /home/pi/GarageWeb**
 
6. Test out setup and webpage (default port is 5000)
`cd GarageWeb`
- Test Relay connections
`python relaytest.py`
- Test Magnetic Reed Switches
`python log.py`
- Test out Webpage (Rasp_Pi_IP_Address:5000)
```
export FLASK_APP=web
export FLASK_ENV=development
flask run --host=0.0.0.0
```
7. Change the default password of "12345678"
`echo "<your password>" > pw`

 7. To Setup this code to run automatically on system boot up:
```
sudo cp systemd/* /etc/systemd/system/
sudo cp tmpfiles.d/* /etc/tmpfiles.d/
sudo systemctl enable garageweb-log
sudo systemcl enable garageweb
sudo reboot
```

---
Wiring Diagram:
---
<img src="https://github.com/rchiechi/GarageWeb/blob/master/Wiring_Diagram.jpg">

**Note: I had to reverse the HIGH/LOW states in `getGarageDoorState()` in [util.py](https://github.com/rchiechi/GarageWeb/blob/master/util.py) of the reed switches (GPIO 16/18) to make my NO connectors work.**

---
#### Additional Videos:
---

- Sonoff Garage Door Opener: https://youtu.be/f1JeKHraDf8
- How to set up your Raspberry Pi: https://youtu.be/EeEU_8HG9l0
- How to set up Port Forwarding on your Router: https://youtu.be/VhVV25zCFrQ
