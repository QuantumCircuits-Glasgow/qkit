# Rohde&Schwarz ZVA_40_VNA 
# Dmytro Bozhko <Dmytro.Bozhko@glasgow.ac.uk>, 2019
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
import types
import logging
import numpy

class ZVA_40_VNA(Instrument):
	'''
	This is the python driver for the Rohde&Schwarz ZVA40 Vector Network Analyzer

	Usage:
	Initialise with
	<name> = instruments.create('<name>', address='<GPIB address>', reset=<bool>)
	
	'''

	def __init__(self, name, address):
		'''
		Initializes 

		Input:
			name (string)	: name of the instrument
			address (string) : GPIB address
		'''
		
		logging.info(__name__ + ' : Initializing instrument')
		Instrument.__init__(self, name, tags=['physical'])

		self._address = address
		self._visainstrument = visa.instrument(self._address)
		self._ci = 1 
		self._start = 0
		self._stop = 0
		self._nop = 2
		self._ifbw= 1
		
		# LUKE
		self._cwfreq = None
		self._sweep = None


# Implement parameters
		self.add_parameter('nop', type=int, flags=Instrument.FLAG_GETSET, minval=2, maxval=60001, tags=['sweep'])
		self.add_parameter('centerfreq', type=float,flags=Instrument.FLAG_GETSET,minval=0, maxval=40e9,units='Hz', tags=['sweep'])
		self.add_parameter('startfreq', type=float,flags=Instrument.FLAG_GETSET,minval=0, maxval=40e9,units='Hz', tags=['sweep'])
		self.add_parameter('stopfreq', type=float,flags=Instrument.FLAG_GETSET,minval=0, maxval=43.5e9,units='Hz', tags=['sweep'])
		self.add_parameter('span', type=float,flags=Instrument.FLAG_GETSET,minval=0, maxval=40e9,units='Hz', tags=['sweep'])
		self.add_parameter('power', type=float,flags=Instrument.FLAG_GETSET,minval=-45, maxval=18,units='dBm', tags=['sweep'])
		self.add_parameter('averages', type=int,flags=Instrument.FLAG_GETSET,minval=1, maxval=1024, tags=['sweep'])
		self.add_parameter('Average', type=bool,flags=Instrument.FLAG_GETSET)
		self.add_parameter('sweeptime_averages', type=float, flags=Instrument.FLAG_GET, minval=0, maxval=1e3, units='s', tags=['sweep'])
		#self.add_parameter('sweeptime', type=float, flags=Instrument.FLAG_GET, minval=0, maxval=1e3, units='s', tags=['sweep'])
		self.add_parameter('ifbandwidth', type=float, flags=Instrument.FLAG_GETSET, minval=1, maxval=1e6, units='Hz')
		
		# LUKE
		self.add_parameter('cw', type=bool, flags=Instrument.FLAG_GETSET)
		self.add_parameter('sweep_type', type=str, flags=Instrument.FLAG_GETSET, tags=['sweep'])
		self.add_parameter('cwfreq', type=float,flags=Instrument.FLAG_GETSET,minval=0, maxval=40e9,units='Hz', tags=['sweep'])
		self.add_parameter('sweeptime', type=float, flags=Instrument.FLAG_GETSET, minval=0, maxval= 3456000, units='s', tags=['sweep'])   
	
		#self.add_function('get_sweeptime')
		self.add_function('get_sweeptime_averages')
        
		
		self.add_function('returnToLocal')
		self.add_function('get_freqpoints')
		self.add_function('get_tracedata')
		self.add_function('init')
		self.add_function('start_measurement')
		self.add_function('pre_measurement')
		self.add_function('post_measurement')
		self.add_function('ready')
		self.add_function('avg_clear')
		self.add_function('avg_status')
		self.add_function('set_measure_parameter')
		
		self.set_sweep_type('LIN') # Luke

	def get_all(self):		
		self.get_nop()
		self.get_startfreq()
		self.get_stopfreq()
		self.get_power()
		self.get_Average()
		self.get_averages()
		self.get_freqpoints()
		
		# LUKE
		self.get_cw()
		self.get_power()
		self.get_centerfreq()
		self.get_span()
		self.get_sweeptime()
		self.get_sweeptime_averages()
		

#Communication with device

	def returnToLocal(self):
		self._visainstrument.write('@LOC')

	def init(self):
		self._visainstrument.write('@REM')

	def do_set_nop(self, nop):
		'''
		Set Number of Points (nop) for sweep

		Input:
			nop (int) : Number of Points

		Output:
			None
		'''
		logging.debug(__name__ + ' : setting Number of Points to %s ' % (nop))
		self.write('SENS%i:SWE:POIN %i' %(self._ci,nop))
		self._nop = nop
		#self.get_freqpoints() #Update List of frequency points  

	def do_get_nop(self):
		'''
		Get Number of Points (nop) for sweep

		Input:
			None
		Output:
			nop (int)
		'''
		logging.debug(__name__ + ' : getting Number of Points')
		self._nop = int(self.query('SENS1:SWE:POIN?').strip())
		return self._nop

	def do_set_power(self,pow):
		'''
		Set probe power

		Input:
			pow (float) : Power in dBm

		Output:
			None
		'''
		logging.debug(__name__ + ' : setting power to %s dBm' % pow)
		self.write('SOUR%i:POW %.2f' % (self._ci,pow))

	def do_get_power(self):
		'''
		Get probe power

		Input:
			None

		Output:
			pow (float) : Power in dBm
		'''
		logging.debug(__name__ + ' : getting power')
		return float(self.query('SOUR%i:POW?' % (self._ci)))

	def do_set_centerfreq(self,cf):
		'''
		Set the center frequency

		Input:
			cf (float) :Center Frequency in Hz

		Output:
			None
		'''
		logging.debug(__name__ + ' : setting center frequency to %s' % cf)
		self._visainstrument.write('SENS%i:FREQ:CENT %f' % (self._ci,cf))
		self.get_startfreq();
		self.get_stopfreq();
		self.get_span();

	def do_get_centerfreq(self):
		'''
		Get the center frequency

		Input:
			None

		Output:
			cf (float) :Center Frequency in Hz
		'''
		logging.debug(__name__ + ' : getting center frequency')
		sweep_type = self.do_get_sweep_type()
		if sweep_type == 'LIN':
		    return float(self.query('SENS%i:FREQ:CENT?'%(self._ci)))
		else:
		    return float(self.query('SENS%i:FREQ:CW?'%(self._ci)))
    # LUKE
	def do_set_cwfreq(self,cf):
		'''
		Set the CW frequency

		Input:
			cf (float) :CW Frequency in Hz

		Output:
			None
		'''
		logging.debug(__name__ + ' : setting cw frequency to %s' % cf)
		self._visainstrument.write('SENS%i:FREQ:CW %f' % (self._ci,cf))
		

    #LUKE
	def do_get_cwfreq(self):
		'''
		Get the center frequency

		Input:
			None

		Output:
			cf (float) :Center Frequency in Hz
		'''
		logging.debug(__name__ + ' : getting center frequency')
		sweep_type = self.do_get_sweep_type()
		if sweep_type == 'LIN':
		    return float(self.query('SENS%i:FREQ:CENT?'%(self._ci)))
		else:
		    return float(self.query('SENS%i:FREQ:CW?'%(self._ci)))
	
	
	
	def do_set_span(self,span):
		'''
		Set Span

		Input:
			span (float) : Span in KHz

		Output:
			None
		'''
		logging.debug(__name__ + ' : setting span to %s Hz' % span)
		self.write('SENS%i:FREQ:SPAN %i' % (self._ci,span))   
		self.get_startfreq();
		self.get_stopfreq();
		self.get_centerfreq();

	def do_get_span(self):
		'''
		Get Span
		
		Input:
			None

		Output:
			span (float) : Span in Hz
		'''
		logging.debug(__name__ + ' : getting center frequency')
		sweep_type = self.do_get_sweep_type()
		if sweep_type == 'LIN':
		    span = self.query('SENS%i:FREQ:SPAN?' % (self._ci) ) #float( self.query('SENS1:FREQ:SPAN?'))
		else:
		    span = 0
		return span

	def do_set_startfreq(self,val):
		'''
		Set Start frequency

		Input:
			span (float) : Frequency in Hz

		Output:
			None
		'''
		logging.debug(__name__ + ' : setting start freq to %s Hz' % val)
		self.write('SENS%i:FREQ:STAR %f' % (self._ci,val))
		self._start = val
		self.get_centerfreq();
		self.get_stopfreq();
		self.get_span();

	def do_get_startfreq(self):
		'''
		Get Start frequency
		
		Input:
			None

		Output:
			span (float) : Start Frequency in Hz
		'''
		logging.debug(__name__ + ' : getting start frequency')
		sweep_type = self.do_get_sweep_type()
		if sweep_type == 'LIN':
		    self._start = float(self.query('SENS%i:FREQ:STAR?' % (self._ci),delay=1))
		else:
		    self._start = float(self.query('SENS%i:FREQ:CW?'%(self._ci)))
		return self._start

	def do_set_stopfreq(self,val):
		'''
		Set STop frequency

		Input:
			val (float) : Stop Frequency in Hz

		Output:
			None
		'''
		logging.debug(__name__ + ' : setting stop freq to %s Hz' % val)
		self.write('SENS%i:FREQ:STOP %f' % (self._ci,val))  
		self._stop = val
		self.get_startfreq();
		self.get_centerfreq();
		self.get_span();

	def do_get_stopfreq(self):
		'''
		Get Stop frequency
		
		Input:
			None

		Output:
			val (float) : Start Frequency in Hz
		'''
		logging.debug(__name__ + ' : getting stop frequency')
		sweep_type = self.do_get_sweep_type()
		if sweep_type == 'LIN':
		    self._stop = float(self.query('SENS%i:FREQ:STOP?' % (self._ci),delay=1))
		else:
		    self._stop = float(self.query('SENS%i:FREQ:CW?'%(self._ci)))
		return self._stop

	def do_get_ifbandwidth(self):
		logging.debug(__name__ + ' : getting IF bandwidth')
		self._ifbw= self.query('SENS%i:BAND?' %(self._ci))
		return self._ifbw
		
	def do_set_ifbandwidth(self, value):
		logging.debug(__name__ + ' : setting IF bandwidth to %f' %(value))
		self.write('SENS%i:BAND %f' %(self._ci,value))
		self._ifbw=value
		
	# LUKE
	def do_set_cw(self, val):
		""" Set instrument to CW (single frequency) mode and back"""
	
		if val:
			if self._cwfreq is None:
				self._cwfreq = self.get_centerfreq()
			self.set_nop(1)
			self.set_sweep_type("LIN")
			self.set_cwfreq(self._cwfreq)
		else:
			self._visainstrument.write('SENS%i:FREQ:CENT %f' % (self._ci,cf))
			self.set_startfreq(self._start)
			self.set_stopfreq(self._stop)
			
	# Luke
	def do_get_cw(self):
		""" retrieve CW mode status"""
		if (self.get_nop() == 1) and (self.get_sweep_type() == "LIN"): ret = True
		else: ret = False
		return ret
		
	# LUKE
	def do_get_sweep_type(self):
		"""
			Get the Sweep Type
			Input:
			None
		
		Output:
			Sweep Type (string). One of
			LIN:	Frequency-based linear sweep
			LOG:	Frequency-based logarithmic sweep
			SEGM:	Segment-based sweep with frequency segments 
			POW:	Power-based sweep with CW frequency
			CW:		Single frequency mode
		"""
		logging.debug(__name__ + ' : getting sweep type')
		return str(self._visainstrument.query('SENS%i:SWE:TYPE?' % self._ci))[:-1]
		
	#LUKE
	def do_set_sweep_type(self, swtype):
		"""
		Get the Sweep Type
		
		Input:
			Sweep Type (string). One of
			LIN:	Frequency-based linear sweep
			LOG:	Frequency-based logarithmic sweep
			SEGM:	Segment-based sweep with frequency segments 
			POW:	Power-based sweep with CW frequency
			CW:		Single frequency mode
			
		Output: 
			None
		"""
		if swtype in ('LIN','LOG','SEGM','POW','CW'):
			logging.debug(__name__ + ': Setting sweep type to %s' % swtype)
			return self._visainstrument.write('SENS%i:SWE:TYPE %s' %(self._ci,swtype))
		else:
			logging.error(__name__ + ' : Illegal argument %s' % swtype)
			return False
		
	
	def get_tracedata(self, format = 'AmpPha', single=False,chn=1):
		'''
		Get the data of the current trace

		Input:
			format (string) : 'AmpPha': Amp and Phase, 'RealImag', 'dB': get current trace values as on the screen of VNA

		Output:
			'AmpPha':_ Amplitude and Phase
		'''
		if format.upper() == 'DB':
			data = self._visainstrument.ask_for_values('FORM REAL,32;*CLS;CALC'+str(chn)+':DATA:ALL? FDAT;*OPC',fmt=1)
		else:
			data = self._visainstrument.ask_for_values('FORM REAL,32;*CLS;CALC'+str(chn)+':DATA:ALL? SDAT;*OPC',fmt=1)
		data_size = numpy.size(data)
		datareal = numpy.array(data[0:data_size:2])
		dataimag = numpy.array(data[1:data_size:2])
		  
		if format.upper() == 'REALIMAG':
			return datareal, dataimag
		elif format.upper() == 'AMPPHA':
				dataamp = numpy.sqrt(datareal*datareal+dataimag*dataimag)
				datapha = numpy.arctan2(dataimag,datareal)
				return dataamp, datapha
		elif format.upper() == 'DB':
				dataamp = numpy.array(data)
				return dataamp
		else:
			raise ValueError('get_tracedata(): Format must be AmpPha or RealImag or dB') 

	def do_get_sweeptime(self):
		'''
			Get total sweeptime in s
		'''
		q=float(self.query('SENS%i:SWE:TIME?' %(self._ci) ))
		return q
	
	#LUKE
	def do_set_sweeptime(self, swtype):
		"""
		Set the Sweeptime
		"""
		sweep_type = self.do_get_sweep_type()
		logging.debug(__name__ + ' : setting time to %f' %(swtype))
		self.write('SENS%i:SWE:TIME %f' %(self._ci,swtype))
		self._sweeptime = swtype
		
		

	def do_get_Average(self):
		'''
		Get status of Average

		Input:
			None

		Output:
			Status of Averaging (bool)
		'''
		logging.debug(__name__ + ' : getting average status')
		return bool(int(self.query('SENS%i:AVER:STAT?' %(self._ci))))

	def do_get_averages(self):
		'''
		Get number of averages
		Input:
			None
		Output:
			number of averages
		'''
		logging.debug(__name__ + ' : getting Number of Averages')
		#return int(self.query('SENS%i:AVER:COUN?' % self._ci))
		return int(self._visainstrument.query('SENS%i:AVER:COUN?' % self._ci)) #LUKE

	def avg_clear(self):
		self.write('SENS%i:AVER:CLE' %(self._ci))

	def do_set_Average(self, status):
		'''
		Set status of Average

		Input:
		status (boolean)

		Output:
			None
		'''
		logging.debug(__name__ + ' : setting Average to "%s"' % (status))
		if status:
			self.write('SENS%i:AVER:STAT 1' % (self._ci))
		else:
			self.write('SENS%i:AVER:STAT 0' % (self._ci))

	def do_set_averages(self, av):
		'''
		Set number of averages
		Input:
			av (int) : Number of averages
		Output:
			None
		'''
		self.write('INIT:CONT 0')
		self.write('SENS%i:SWE:COUN %i' % (self._ci,av))
		#self.write('SENS%i:AVER:COUN %i' % (self._ci,av)
		#logging.debug(__name__ + ' : setting Number of averages to %i ' % av) #LUKE
		#self.write('SENS%i:AVER:COUN %i' % (self._ci,av)) #LUKE
		self.write('SENS%i:AVER:COUN %i' % (self._ci,av)) #LUKE (set CLE back to COUN like above commented line)

	def do_get_sweeptime_averages(self):
		if self.get_Average():
			return self.get_sweeptime() * self.get_averages()
		else:
			return self.get_sweeptime()

	def get_freqpoints(self, query = False):
		self._freqpoints = numpy.linspace(self._start,self._stop,self._nop)
		return self._freqpoints

	def set_measure_parameter(self, s_par):
		# CALC:PAR:CAT?
		# CALC:PAR:SEL? active trace
		# CALC:PAR:MEAS 'Trc1', 'S11'
		active_trace= self.query("CALC:PAR:SEL?")
		self.write("CALC:PAR:MEAS %s, '%s'" %(active_trace.rstrip(), s_par))
		
	def start_measurement(self):
		'''
		This function is called at the beginning of each single measurement in the spectroscopy script.
		Here, it resets the averaging.  
		'''
		self.avg_clear()
		self.write('INIT:IMM')

	def pre_measurement(self):
		'''
		Set everything needed for the measurement
		Averaging has to be enabled.
		'''
		
		if not self.get_Average():
			self.set_averages(1)
			self.set_Average(True)
		else:
			self.write('INIT:CONT 0')
			self.write('SENS%i:SWE:COUN %i' % (self._ci,self.get_averages()))

	def post_measurement(self):
		'''
		Bring the VNA back to a mode where it can be easily used by the operater.
		For this VNA and measurement method, no special things have to be done.
		'''
		pass

	def avg_status(self):
		return int(self.query('CALC%i:DATA:NSW:COUN?' %(self._ci)))

	def ready(self):
		'''
		This is a proxy function, returning True when the VNA has finished the required number of averages.
		'''
		return self.avg_status() == self.get_averages(query=False)
#
#    def set_return_format(self):
#		'''specifies the number of significant digits'''
#		self.write('INIT:CONT ON')
#
	def query(self, msg, delay=None):
		return self._visainstrument.query(msg, delay=delay)
	def write(self, msg):
		return self._visainstrument.write(msg)
