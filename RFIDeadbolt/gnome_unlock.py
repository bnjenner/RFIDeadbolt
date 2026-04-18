import os
import time
import json
import utils
import SerialRFID as sr

START = None
FAILED_ATTEMPTS = 0

########################################################
# RFIDeadbolt Gnome Unlock
print(f"// RFIDeadbolt: Gnome Unlock")
if __name__ == "__main__":

	############################
	# Open Config Files
	print(f"// Initializing...")
	with open("config.json") as f:
		config = json.load(f)

	# Open Device
	scanner = sr.SerialRFID(
				device=config["device"],
				baudrate=config["baudrate"]
			  )

	############################
	# Begin Listening
	print(f"// Scanner Active...")
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
			print(f"// Authorization Successful.")
			screen_status = os.popen(config["session_query"]).read()
			if "false" in screen_status:
				print(f"// Session Already Unlocked.")
			elif "true":
				os.system(config["session_unlock"])
				print(f"// Session Unlocked.")
				pass

			# Reset timer and failed attempts
			START = None
			FAILED_ATTEMPTS = 0

		else:

			# Handle Failure and start time
			print(f"// Authorization Failed.")
			FAILED_ATTEMPTS += 1
			if FAILED_ATTEMPTS > 2:
				exit()
			START = time.time()
