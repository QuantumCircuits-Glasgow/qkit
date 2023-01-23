# Qkit driver for Magnet-Physik FH-54
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


class Magnet_Physik_FH_54(Instrument):
	'''
		Main class for Magnet-Physik FH-54 driver
		
		Usage:
		Initialize with
		<name> = instruments.create('name', 'Magnet_Physik_FH_54', address=<SERIAL address>)
	'''

	def __init__(self, name, address):
		'''
		Initialize the driver by creating a pyvisa instrument with a SERIAL INST address.
		
		Input:
			<name> (string): Name of the device
			<address> (string): SERIAL INST address (example: ASRL1[::INSTR])
		
		'''
		logging.info(__name__ + ' : Initializing instrument Magnet-Physik FH-54')
		Instrument.__init__(self, name, tags=['physical'])
		
		self.name=name
		self.address=address
		self._visainstrument=visa.instrument(self.address)
		self._visainstrument.baud_rate=19200
		#add Instrument class parameters
		self.add_parameter('field', type=float, flags=self.FLAG_GET)
		self.add_parameter('units', type=bytes, flags=self.FLAG_GET)
		self.add_parameter('temperature', type=float, flags=self.FLAG_GET)
		
		self.get_all()

	def get_all(self):
		'''
		Get all device parameters in one function call.
		'''
		logging.debug(__name__ + ' : get all')
		self.get_field()
		self.get_units()
		self.get_temperature()

	# GET and SET functions
	def do_get_field(self):
		'''
		Get current magnetic field measurement.
		
		Input: None
		Output (float) : Value of the field in device current units
		'''
		logging.debug(__name__ + ' : get magnetic field')
		return float(self.query('?MEAS\r').strip().split(' ')[0])

	def do_get_units(self):
		'''
		Get current physical unit of measuring value.
		
		Input: None
		Output (string) : Units
		'''
		logging.debug(__name__ + ' : get units')
		return self.query('?MEAS\r').strip().split(' ')[1]

	def do_get_temperature(self):
		'''
		Get current temperature in C.
		
		Input: None
		Output (float) : Temperature in degrees C
		'''
		logging.debug(__name__ + ' : get temperature')
		return float(self.query('?TEMP\r').strip().split(' ')[0])

	#Interface to pyvisa
	def query(self, msg):
		return self._visainstrument.query(msg, delay=None)
