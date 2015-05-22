# This is all in the right hand reference frame. (Hold out your right hand and shape it so that your thumb is the robotiq middle finger)
PINKY_FLAG = 1
INDEX_FLAG = 2
MIDDLE_FLAG = 4
PALM_FLAG = 8
ERR_CODE = -1

# An easy-to-reference model of the hand's takktile arrays.
#	Meant to be filled with float data between 0 and 1
#	or an error for each finger.
class TactileState:
	def __init__(self, err_code):
		self.middle = err_code
		self.pinky = err_code
		self.index = err_code
		self.palm = err_code

def mk_lut():
	global PINKY_FLAG, INDEX_FLAG, MIDDLE_FLAG, PALM_FLAG
	takk_lut = [None] * (2 ** 4)
	takk_lut[PALM_FLAG + INDEX_FLAG] = palm_index
	return takk_lut

def get_idx(sensor_info):
	global PINKY_FLAG, INDEX_FLAG, MIDDLE_FLAG, PALM_FLAG
	
	idx = 0
	if index_present(sensor_info):
		idx += INDEX_FLAG
	if pinky_present(sensor_info):
		idx += PINKY_FLAG
	if middle_present(sensor_info):
		idx += MIDDLE_FLAG
	if palm_present(sensor_info):
		idx += PALM_FLAG

	return idx
	
def pinky_present(cur_indices):
	return (3 in cur_indices)

def index_present(cur_indices):
	return (8 in cur_indices)

def middle_present(cur_indices):
	return (14 in cur_indices)

def palm_present(cur_indices):
	return (25 in cur_indices)


# Currently just a straight average
def aggregate(pad_pressure_list):
        summy = 0
        for value in pad_pressure_list:
                summy += value
	
        return summy / (len(pad_pressure_list))

## LUT ENTRIES
def palm_index(pressures):
	global ERR_CODE
	state = TactileState(ERR_CODE)
	state.palm 	= aggregate(pressures[0:4] + pressures[10:])
	state.index 	= aggregate(pressures[4:10])

	return state
