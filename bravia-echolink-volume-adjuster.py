import logging, subprocess, time, os
import configparser, json
from bravia_tv import BraviaRC

#####Logging Stuff#####

logger = logging.getLogger()
logger.setLevel(logging.DEBUG) #most permissive level cross both handlers
logFormatter = logging.Formatter("%(asctime)s [%(levelname)-5.5s]  %(message)s")

#Console-only (initially)
consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
consoleHandler.setLevel(logging.DEBUG)
logger.addHandler(consoleHandler)

#####Config Reading####

configFileName = './config/bravia-echolink-volume-adjuster.conf'
logger.info(f"Program started. Reading configuration file from {configFileName}")
configreader = configparser.RawConfigParser()
configreader.read(configFileName)
config = {}
for section in configreader.sections():
    config[section] = dict(configreader.items(section))

####Adding File Logging####

if 'LOGGING' in config:
    if "file_log_path" in config["LOGGING"]:
        if "file_log_name" in config["LOGGING"]:
            fileHandler = logging.FileHandler(f"{config['LOGGING']['file_log_path']}/{config['LOGGING']['file_log_name']}")
            fileHandler.setFormatter(logFormatter)
            logger.addHandler(fileHandler)
            if "file_log_level" in config["LOGGING"]:
                fileLogLevel = config["LOGGING"]["file_log_level"]
                fileHandler.setLevel(logging.getLevelName(fileLogLevel))
                logger.info(f"Added file log appender at level {fileLogLevel}")
    if "console_log_level" in config["LOGGING"]:
        logConsoleLevel = config["LOGGING"]["console_log_level"]
        consoleHandler.setLevel(logging.getLevelName(logConsoleLevel))
        logger.info(f"Console logging at level {logConsoleLevel}")

#####Config dump to log####

logger.info("Configuration: " + json.dumps(config))

###########################

os.environ["AMAZON"] = config["ALEXA"]["amazon"]
os.environ["ALEXA"]  = config["ALEXA"]["alexa"]
os.environ["EMAIL"] = config["ALEXA"]["email"]
os.environ["PASSWORD"] = config["ALEXA"]["password"]
os.environ["MFA_SECRET"] = config["ALEXA"]["mfa_secret"]
os.environ["REFRESH_TOKEN"] = config["ALEXA"]["refresh_token"]

###########################

polling_interval = float(config['ADJUSTER']['polling_interval_sec'])                   #sec
exception_sleep_interval = float(config['ADJUSTER']['exception_sleep_interval_sec'])   #sec

def set_echolink_volume (vol):
    cmd=f"{config['ALEXA']['alexa_remote_control_command']} -d {config['ALEXA']['alexa_device']} -e vol:{vol}"
    http_code = subprocess.call(cmd, shell=True)  # returns the exit code in unix
    logger.info(f"HTTP Response Code: {http_code}")    
    if http_code == 200:
        return 0
    else:
        return 1

#Initial connection at startup
braviarc = BraviaRC(config["TV"]["tv_ip"])
braviarc.connect (config["TV"]["pin"], config["TV"]["device_id"], config["TV"]["device_id"])

logger.info("BraviaRC.connect succesful")

previousVol = -1                # Bravia volume on a previous poll cycle - to track continous volume change
currentVol = -1                 # Bravia volume = desired volume
lastEcholinkVolume = -1         # Setting after successful volume change command
currentMuteStatus = False       # Bravia mute status = desired mute status



while True:

    time.sleep(polling_interval)
    
    try:
        vol_info = braviarc.get_volume_info()

        if 'volume' not in vol_info or 'mute' not in vol_info:
            logger.debug("Volume/Mute info not received. Waiting 5 seconds")
            time.sleep(exception_sleep_interval)
            continue
        
        currentVol = vol_info.get('volume')
        currentMuteStatus = vol_info.get('mute')
    
    except Exception as exc:
        logger.exception(exc)
        logger.info("Volume/Mute info not received (exception). Waiting 5 seconds")
        time.sleep(exception_sleep_interval)
        continue

    
    if currentVol != previousVol:
        logger.info(f"Volume changing: vol={currentVol}, previousVol={previousVol}; Mute={currentMuteStatus}")  
        previousVol = currentVol

    elif currentVol == previousVol and currentVol != lastEcholinkVolume:
        logger.info(f"Volume changed and stable: vol={currentVol}, lastEcholinkVolume={lastEcholinkVolume}; Mute={currentMuteStatus}")
        if currentMuteStatus == False:
            logger.info(f"[not muted] Setting echolink volume to {currentVol}...")
            try:
                rc = set_echolink_volume(currentVol)
                if rc==0:
                    lastEcholinkVolume = currentVol
            except Exception as exc:
                logger.exception(exc)
        else:
            logger.info(f"[currently muted] Ignoring volume change until unmuted")

    if currentMuteStatus == True and lastEcholinkVolume != 0:
        logger.info(f"Bravia is Muted but EchoLink is not. Setting EchoLink volume to 0")
        set_echolink_volume(0)
        if rc==0:
            lastEcholinkVolume = 0   

    elif currentMuteStatus == False and currentVol != 0 and lastEcholinkVolume == 0:
        logger.info(f"Bravia is unmuted but EchoLink volume is still 0. Restorong EchoLink volume to {currentVol}")
        set_echolink_volume(currentVol)
        if rc==0:
            lastEcholinkVolume = currentVol