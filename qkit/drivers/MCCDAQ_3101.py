from qkit.core.instrument_base import Instrument
import qkit.drivers
import logging
import numpy as np

try:
	from mcculw import ul
	from mcculw.enums import InterfaceType, ULRange, InfoType, BoardInfo, DigitalPortType, DigitalIODirection
	from mcculw.ul import ULError

except ImportError:
	logging.error("Could not find mcculw library.")
	print("Could not find mccuwl library.")

class MCCDAQ_3101(Instrument):
	'''
	Qkit driver for MCCDAQ USB 3101 Digital-to-Analog Converter
	Communication with device is done using MCC's python library: https://github.com/mccdaq/mcculw
	Dependencies required: InstaCal application 	!! actually not needed
	'''

	def __init__(self, name, dac_board_number=0, nchannels=4):
		'''
		Initializes qkit instrument for DAC


		Input:
		
		'''
		Instrument.__init__(self, name, tags=['physical'])

		self.dac_board_number=0
		self.channels=nchannels
		self.ul_range=[ULRange.UNI10VOLTS]*self.channels #default range
		
		self.add_parameter('voltage', type=float, flags=Instrument.FLAG_SET, 
                units='V')# , channels=(0, self.channels-1), channel_prefix='ch%d_')


		#Initialize DAQ object
		self.create_dac_object()
		
		self.add_function('set_ul_range')
		self.add_function('config_DIO')
		self.add_function('get_DIO')
		self.add_function('set_DIO')
		
	

	def create_dac_object(self, interface_type=InterfaceType.USB, number_of_devices=10):
		'''
		'''
		try:
			self.dac_descriptor=ul.get_daq_device_inventory(interface_type,number_of_devices)[0]
			#self.dac_board_number=ul.get_board_number(self.dac_descriptor)
			
			if self.dac_descriptor.product_name != 'USB-3101':
				raise Exception('Does not match USB-3101')
			ul.create_daq_device(self.dac_board_number, self.dac_descriptor)
		except ULError as e:
			print("Error code: {}. Message: {}\n".format(e.errorcode, e.message))	


	def _do_set_voltage(self, value, channel=0):
		'''

		Input:
			channel:
			value:  -10:10V or 0:10V depending on range chosen, see set_ul_range
		'''
		try:
			ul.v_out(self.dac_board_number, channel, self.ul_range[channel], value)
			#ul.a_out(self.dac_board_number, channel, self.ul_range, value)
		except ULError as e:
			print("Error code: {}. Message: {}\n".format(e.errorcode, e.message))	

	def set_ul_range(self, int_range=0, channel=0):
		'''
		Resets voltage output
		Unipolar(0) 0:10V UNI10VOLTS (int value:100)
		Bipolar(1) -10:10V BIP10VOLTS (int value: 1)
		'''
		ul_range= ULRange.UNI10VOLTS if (int_range == 0) else ULRange.BIP10VOLTS
		try:
			ul.set_config(InfoType.BOARDINFO, self.dac_board_number,channel, BoardInfo.DACRANGE, ul_range)
		except ULError as e:
			print("Error code: {}. Message: {}\n".format(e.errorcode, e.message))	
		self.ul_range[channel]=ul_range
	
	def get_DIO(self, bit_num=None):
		'''
		Output: int value (0-255 or 0-1)
		'''
		try:
			if bit_num:
				return ul.d_bit_in(self.dac_board_number, DigitalPortType.AUXPORT, bit_num)
			else:
				return ul.d_in(self.dac_board_number, DigitalPortType.AUXPORT)	
		except ULError as e:
			print("Error code: {}. Message: {}\n".format(e.errorcode, e.message))	

	def set_DIO(self, value, bit_num=None):
		'''
		Input: int value (0-255 or 0-1)
		'''
		try:
			if bit_num:
				ul.d_bit_out(self.dac_board_number, DigitalPortType.AUXPORT, bit_num, value)
				return True
			else:
				ul.d_out(self.dac_board_number, DigitalPortType.AUXPORT, value)	
				return True
		except ULError as e:
			print("Error code: {}. Message: {}\n".format(e.errorcode, e.message))	

	def config_DIO(self, config_type, IODirection, bit_num=None):
		'''

		Input:
			config_type: config either whole port ('port') or individual pins/bits ('bit')
			bit_num: specifies which DIO pin to configure (only relevant when config_type='bit') 1-8
			IODirection: config to either input or output ports
		'''
		try:
			IODirection = DigitalIODirection.IN if (IODirection == 'input') else DigitalIODirection.OUT
			if(config_type == 'port'):
				ul.d_config_port(self.dac_board_number, DigitalPortType.AUXPORT, IODirection)
				self.DIO_direction= IODirection
			elif(config_type == 'bit'):
				ul.d_config_bit(self.dac_board_number, DigitalPortType.AUXPORT, bit_num, IODirection)
		except ULError as e:
			print("Error code: {}. Message: {}\n".format(e.errorcode, e.message))	


	def clear_voltage(self):
		for i in range(self.channels):
			self._do_set_voltage(0, channel=i)
		return True
	def release_dac_object(self):
		'''
		'''
		try:
			ul.release_daq_device(self.dac_board_number)
		except ULError as e:
			print("Error code: {}. Message: {}\n".format(e.errorcode, e.message))	


