import os
import time
import json
import logging
import utils
import SerialRFID as sr

logging.basicConfig(
	level=logging.INFO,
	format="%(levelname)s: %(message)s",
)
log = logging.getLogger("rfideadbolt")

START = None
FAILED_ATTEMPTS = 0

########################################################
# RFIDeadbolt Gnome Unlock
log.info("RFIDeadbolt: Gnome Unlock")
if __name__ == "__main__":

	############################
	# Open Config Files
	log.info("Initializing...")
	with open("config.json") as f:
		config = json.load(f)

	# Open Device
	scanner = sr.SerialRFID(
				device=config["device"],
				baudrate=config["baudrate"]
			  )

	############################
	# Begin Listening
	log.info("Scanner Active...")
	for data in scanner.listen():

		# Enforce 3 second timer
		if START and (time.time() - START) < 3:
			continue

		# Skip if data empty
		if data is None:
			continue

		# Check Hash
		if utils.check_password(config["hash_file"], data):

			# Successful Auth, check lock screen status
			log.info("Authorization Successful.")
			screen_status = os.popen(config["session_query"]).read()
			if "false" in screen_status:
				log.info("Session Already Unlocked.")
			elif "true":
				os.system(config["session_unlock"])
				log.info("Session Unlocked.")

			# Reset timer and failed attempts
			START = None
			FAILED_ATTEMPTS = 0

		else:

			# Handle Failure and start time
			FAILED_ATTEMPTS += 1
			log.warning("Authorization Failed. (attempt %d/3)", FAILED_ATTEMPTS)
			if FAILED_ATTEMPTS > 2:
				log.error("Max failed attempts reached. Exiting.")
				exit()
			START = time.time()
