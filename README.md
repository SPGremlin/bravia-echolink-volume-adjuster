**SONY Bravia TVs (2013+) to Alexa (Echo) Volume Adjuster**

Amazon Echo Link is a very cool and not-so-well-known device that wirelessly streams music to your amp/speaker system with very high fidelity. At the same time, it has an optical input allowing you to also connect a TV to the same amp/speaker system.

The beauty of this device is that it automatically switches the sources: you do not need to operate your receiver/amp to switch the source. If you're playing music from Alexa, music will go through. If the TV is on, TV sound will take over, automatically.

Unfortunately, the optical SPDIF sound interface has no volume control (by design). The volume and mute buttons on your TV remote become useless, and you need to adjust the volume on Echo Link separately (with a knob, a separate Echo Remote, or by voice commands to Alexa).

This little project connects together the Sony Bravia TV Rest API (from 2013 models and beyond) with the undocumented Alexa API to integrate volume controls together.  Basically, it is polling the TV volume and mute status and sets Alexa volume accordingly.

The script has been validated to run on Raspberry PI.

Deployment and Validation:

1. **pip** install bravia-tv
2. **sudo** **apt** install -y jq
3. Upload the project files (repository) folder to RaspberryPI or whatever machine you intend running it on
4. Create the **config/bravia-echolink-volume-adjuster.conf** file based on the provided sample file. Populate your account-specific and TV-specific values in the config file.
5. Use https://github.com/Apollon77/alexa-cookie/ or https://github.com/Apollon77/alexa-cookie-cli/ (easier) to manually log into your Amazon account and obtain a Refresh Token.  For additional security, consider reconfiguring your Echo devices to a fresh new throwaway "less sensitive" Amazon account only used for Alexa and not for shopping, payments, or AWS.
6. Run **bravia-echolink-volume-adjuster.sh**, validate if it works

Installation as a Service:

 - Edit the **bravia-echolink-volume-adjuster.service** descriptor file to specify  correct Working Directory (where the project folder was placed on the machine)
 - Move or Copy this descriptor file to the **/etc/systemd/user/** folder
 - **sudo systemctl enable** /etc/systemd/user/bravia-echolink-volume-adjuster.service
 - **sudo systemctl start** bravia-echolink-volume-adjuster

Attribution Notes:

 - Alexa-Remote-Control shell CLI shamelessly cloned from (but had a few
   small changes) https://github.com/thorsten-gehrig/alexa-remote-control 
    -- thanks, @adn77
   
 - Bravia TV Python API (installed as a package) is from
   https://github.com/dcnielsen90/python-bravia-tv/


License:

 - MIT license for the code created in this project (except the bundled alexa-remote-control.sh script, its license needs to be checked on the original project repository)