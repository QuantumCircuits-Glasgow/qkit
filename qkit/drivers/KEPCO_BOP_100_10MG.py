# Qkit driver for KEPCO BOP 100-10MG power supply
# Dmytro Bozhko <dmytro.bozhko@glasgow.ac.uk> 2019
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from qkit.core.instrument_base import Instrument
from qkit import visa
import logging
import numpy as np
import time
from qkit.drivers.visa_prologix import instrument

class KEPCO_BOP_100_10MG(instrument, Instrument):
	'''
		Main class for KEPCO BOP 100-10MG power supply driver
		
		Usage:
		Initialize with
		<name> = instruments.create('name', 'KEPCO_BOP_100_10MG', address=<SERIAL address>)
	'''

	def __init__(self, name, address, **kwargs):
		'''
		Initialize the driver by creating a pyvisa instrument with a SERIAL INST address.
		
		Input:
			<name> (string): Name of the device
			<address> (string): SERIAL INST address (example: ASRL1[::INSTR])
		
		'''
		logging.info(__name__ + ' : Initializing instrument KEPCO BOP 100-10MG power supply')
		self.ip = kwargs.get("ip", "10.22.197.63")
		super(KEPCO_BOP_100_10MG, self).__init__(address, timeout=10, chunk_size=4096, delay=0.05, ip=self.ip)
		Instrument.__init__(self, name, tags=['physical'])
		
		self.name=name
		self.address=address
		self._visainstrument=visa.instrument(self.address)
		#add Instrument class parameters
		self.add_parameter('current', flags=Instrument.FLAG_GET, units='A', minval=-10, maxval=10, type=float)
		self.add_parameter('voltage', flags=Instrument.FLAG_GET, units='V', type=float)
		self.add_parameter('setcurrent', flags=Instrument.FLAG_GETSET, units='A', minval=-10, maxval=10, type=float)
		self.add_parameter('output_mode', flags=Instrument.FLAG_GETSET, type=str)
		self.add_parameter('status', flags=Instrument.FLAG_GETSET, type=str)
		self.add_function('on')
		self.add_function('off')
		self.add_function('ramp_current')

		self.get_all()

	def get_all(self):
		'''
		Get all device parameters in one function call.
		'''
		logging.debug(__name__ + ' : get all')
		self.get('current')
		self.get('voltage')
		self.get('setcurrent')
		self.get('output_mode')
		self.get('status')

	# GET functions
	def do_get_current(self):
		'''
		Measure current.
		
		Input: None
		Output (float) : Value of the measured current in A
		'''
		logging.debug(__name__ + ' : getting current')
		return float(self.ask('meas:curr?').strip())  #replace with self.ask

	def do_get_voltage(self):
		'''
		Measure voltage.

		Input: None
		Output (float) : Value of the measured voltage in V
		'''
		logging.debug(__name__ + ' : getting voltage')
		return float(self.ask('meas:volt?'.strip()))

	def do_get_setcurrent(self):
		'''
		Get set value for current.
		
		Input: None
		Output (float) : Value of the set current in A
		'''
		logging.debug(__name__ + ' : getting set current')
		return float(self.ask('curr?').strip())

	def do_get_output_mode(self):
		'''
		Get output mode.
		
		Input: None
		Output (int) : Output mode (0:voltage, 1:current)
		'''
		logging.debug(__name__ + ' : getting output mode')
		return int(self.ask('func:mode?').strip())

	def do_get_status(self):
		'''
		Get output status.
		
		Input: None
		Output (bool) : Output(true:on, false:off)
		'''
		logging.debug(__name__ + ' : getting output mode')
		return self.ask('outp?').strip()

	def get_all(self):
		'''
		Get all device parameters in one function call.
		'''
		logging.debug(__name__ + ' : get all')
		self.get('current')
		self.get('voltage')
		self.get('setcurrent')
		self.get('output_mode')
		self.get('status')

	# SET functions
	def do_set_setcurrent(self,setcurr):
		'''
		Set set current.
		
		Input: Current, A
		Output True
		'''
		logging.debug(__name__ + ' : setting setcurrent')
		val=round(setcurr,4)
		q=self.write(f'curr {val}')
		return True

	def do_set_output_mode(self,omode):
		'''
		Set output mode.
		
		Input: str 'curr', 'volt'
		Output True
		'''
		q=self.write('func:mode '+omode)
		return True

	def do_set_status(self,outps):
		'''
		Set output status.
		
		Input: str ('on','off')
		Output: True
		'''
		q=self.write('outp '+outps) # self.write
		return True

	def on(self):
		'''
		Set output on.
		
		Input: None
		Output: True
		'''
		q=self.write('outp on')
		return True

	def off(self):
		'''
		Set output off.
		
		Input: None
		Output: True
		'''
		q=self.write('outp off')
		return True
		
	def ramp_current(self, target, step=0.1, waittime=0.1):
		start = self.get_current()
		
		if target < start :
			step = - step
		
		curr_ramp_values = np.arange(start+step, target+step, step)
		
		for i in curr_ramp_values:
			self.set_setcurrent(i)
			time.sleep(waittime)
		
		
	#Interface to pyvisa
	def query(self, msg):
		return self._visainstrument.query(msg, delay=None)
		

	
