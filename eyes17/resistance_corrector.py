import struct
import eyes17.eyes
dev = eyes17.eyes.open()

def stoa(s):
	return [a for a in s]


calibrator_resistance = 1000. #Resistance of connected resistor used for calibration

cap_and_pcs = dev.read_bulk_flash(dev.CAP_AND_PCS, 5 + 8 * 4)  # READY+calibration_string

if cap_and_pcs[:5] == b'READY':  # PYTHON3
	scalers = list(struct.unpack('8f', cap_and_pcs[5:]))  # #socket cap , C0,C1,C2,C3,PCS,SEN
	resistanceScaling = scalers[6]  # SEN
	print('resistance scaling factor =',resistanceScaling)
	print('scalers:',scalers)
	#dev.resistanceScaling = 1. #Reset scaling factor

	res_sum=0.
	for a in range(10):
		res_sum += dev.get_resistance()
	newres = res_sum/10.
	new_resistance_scaling = calibrator_resistance/newres

	print('new resistance',newres, ' new scaling:', new_resistance_scaling)
	scalers[6] *= new_resistance_scaling
	print('new scalers:',scalers)
	if abs(newres-calibrator_resistance)<calibrator_resistance/10.: #Only 10% variation allowed
		cap_and_pcs=dev.write_bulk_flash(dev.CAP_AND_PCS, stoa(b'READY') + stoa(struct.pack('8f',*scalers)) )  #READY+calibration_string
	else:
		print('resistance out of range. check connections. ', newres)
else:
	print('Cap and PCS calibration invalid')
