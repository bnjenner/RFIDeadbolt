import time
import json
import utils
import SerialRFID as sr

print(f"// RFIDeadbolt: Create Key")
if __name__ == "__main__":

	# Open Config Files
	with open("config.json") as f:
		config = json.load(f)

	# Open Device
	scanner = sr.SerialRFID(
				device=config["device"],
				baudrate=config["baudrate"]
			  )

	# Begin Listening
	print(f"// Scan RFID")
	for data in scanner.listen():

		if data is None:
			continue

		# Save Password
		utils.save_password(config["hash_file"], data)
		print(f"// RFID Scanned Successfully")
		print(f"// Hash written to: {config["hash_file"]}")
		exit()
