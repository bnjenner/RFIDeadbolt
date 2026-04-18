import serial

########################################################
# SerialRFID Class
class SerialRFID:

	def __init__(self, device: str, baudrate: int):
		self.device = device
		self.baudrate = baudrate
		self.serial_in = None

	############################
	# Private Methods
	def __open(self):
		try:                                                                                                                         
			self.serial_in = serial.Serial(                                                                                          
				port=self.device,                                                                                                    
				baudrate=self.baudrate,                                                                                              
			)                                                                                                                        
		except (serial.SerialException, ValueError) as e:                                                                            
			raise RuntimeError(                                                                                                      
				f"Failed to open serial device {self.device!r} at {self.baudrate} baud: {e}"                                         
			) from e

	############################
	# Start Listening
	def listen(self):
		if not self.serial_in:
			self.__open()
		while True:
			data = self.serial_in.readline().decode('utf-8').strip()
			if data == "None":
				yield None
			else:
				yield data