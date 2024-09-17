# Keysight P50xxA/P5004A Streamline Series USB VNA
# Joao Barbosa <j.barbosa.1@research.gla.ac.uk>, 2021

from qkit.core.instrument_base import Instrument
from qkit import visa
from time import sleep
import logging
import numpy as np

class Keysight_VNA_E5080A_2(Instrument):
    '''
    Driver class for Keysight P50xxA/P5004A Streamline Series USB VNA
    Usage:
        vna=qkit.instruments.create("vna", "Keysight_VNA_P50xxA", address=<TCPIP address>)
        vna.gets_()
        vna.sets_()
        vna.some_function()
        ...
    Address for this instrument is only available after initializing the instrument through the "Network Analyzer" software. Currently it is not possible to communicate with it without this proxy software.
    '''
    def __init__(self, name, address, channel_id=1, cw_mode=False): 
        logging.info(__name__ + ' : Initializing instrument')
        super().__init__(name, tags=["physical"])
        
        self._address=address
        self._visainstrument = visa.instrument(self._address)
        self._zerospan = False
        self._ci=int(channel_id)
        self.cw_mode=cw_mode
        self._edel=0
        self._freqpoints=0
        self._nop=0
        
        self._start = 0
        self._stop = 0

        self.add_parameter('nop', type=int,
            flags=Instrument.FLAG_GETSET,
            minval=2, maxval=20001,
            tags=['sweep'])
            
        self.add_parameter('bandwidth',     type=float, minval=0,   maxval=1e9, units='Hz')
        self.add_parameter('averages',      type=int,   minval=1,   maxval=1024)
        self.add_parameter('Average',       type=bool)
        self.add_parameter('centerfreq',    type=float, minval=0, maxval=20e9,  units='Hz')
        self.add_parameter('cwfreq',        type=float, minval=0, maxval=20e9,  units='Hz')
        self.add_parameter('startfreq',     type=float, minval=0, maxval=20e9,  units='Hz')
        self.add_parameter('stopfreq',      type=float, minval=0, maxval=20e9,  units='Hz')
        self.add_parameter('span',          type=float, minval=0, maxval=20e9,  units='Hz')
        self.add_parameter('power',         type=float, minval=-85, maxval=10,  units='dBm')
        self.add_parameter('startpower',    type=float, minval=-85, maxval=10,  units='dBm')
        self.add_parameter('stoppower',     type=float, minval=-85, maxval=10,  units='dBm')
        self.add_parameter('cw',            type=bool)
        self.add_parameter('zerospan',      type=bool)
        self.add_parameter('channel_index', type=int)
        self.add_parameter('sweeptime',     type=float, minval=0, maxval=1e3,   units='s',flags=Instrument.FLAG_GET)
        self.add_parameter('sweeptime_averages', type=float,minval=0, maxval=1e3,units='s',flags=Instrument.FLAG_GET)
        self.add_parameter('edel',          type=float,minval=-10, maxval=10,units='s') #JB 2021
        #self.add_parameter('edel',          type=float,minval=-10, maxval=10,units='s',channels=(1, self._pi), channel_prefix = 'port%d_') # the channel option for qtlab's Instument class is used here to easily address the two VNA ports
        self.add_parameter('edel_status',   type=bool) # legacy name for parameter. This corresponds to the VNA's port extension values.
        self.add_parameter('sweep_mode',    type=str)  #JDB This parameter switches on/off hold. The hold function below does the same job, this is just for code compatibility to the agilent and anritsu drivers.
        self.add_parameter('sweep_type',    type=str)
        self.add_parameter('active_trace',  type=int)
        self.add_parameter('meas_parameter', type=str)
        
        

        self.add_parameter('trigger_source', type=str)
        
        # Implement functions
        self.add_function('get_freqpoints')
        self.add_function('get_tracedata')
        self.add_function('init')
        self.add_function('avg_clear')
        self.add_function('avg_status')
        self.add_function('def_trig')
        self.add_function('get_hold')
        self.add_function('hold')
        self.add_function('get_sweeptime')
        self.add_function('get_sweeptime_averages')
        self.add_function('pre_measurement')
        self.add_function('start_measurement')
        self.add_function('ready')
        self.add_function('post_measurement')
        self.get_all()

    
    def get_all(self):
        self.get_averages()
        self.get_nop()
        self.get_power()
        self.get_startfreq()
        self.get_stopfreq()
        self.get_centerfreq()
        self.get_sweeptime()

        
        self.get_edel()
        self.get_cwfreq()
        self.get_sweeptime()
        self.get_sweeptime_averages()
    ###

    def reset(self):
        self.write("*RST")
        return

    def ready(self):
        '''
        This is a proxy function, returning True when the VNA has finished the required number of averages.
        Averaging must be on (even if it is just one average)
        Trace1 -> 0b10
        Trace2 -> 0b100
        ...
        Trace14 ->0b100 0000 0000 0000
        '''
        return (int(self.ask("STAT:OPER:AVER1:COND?")) & 0b10) 
    
    def hold(self, status):
        self.write(":TRIG:SOUR MAN")
        if status:
            self.write(':INIT%i:CONT OFF'%(self._ci))
        else:
            self.write(':INIT%i:CONT ON'%(self._ci))
            
    def get_hold(self):
        return self.ask(':INIT%i:CONT?'%(self._ci))
    
            
    def init(self):
        
         if self._zerospan:
           self.write('INIT1;*wai')
         else:
           if self.get_Average():
             for i in range(self.get_averages()):
               self.write('INIT1;*wai')
           else:
               self.write('INIT1;*wai')   
               
    def def_trig(self):
        self.write(':TRIG:AVER ON')
        self.write(':TRIG:SOUR bus')    
        
    def avg_status(self):
        return 0 == (int(self.ask('STAT:OPER:COND?')) & (1<<4))    
       
    def avg_clear(self):
        self.write("SENS{}:AVER:CLE".format(self._ci))

    def data_format(self, value="REAL, 64"):
        if value=="ASC": self.write("FORM ASC")
        elif value =="REAL32": self.write("FORM REAL,32")
        elif value =="REAL64": self.write("FORM REAL,64")
        else: raise ValueError("Incorrect data format. Use: ['ASC','REAL32','REAL64']")

    def set_sweeptime_auto(self):
        self.write("SENS{}:SWE:TIME:AUTO ON".format(self._ci))
    
    def get_tracedata(self, format="AmpPha"):
        self.write("FORM:DATA REAL") #for now use Real 32 bit data format
        self.write('FORM:BORD SWAPPED') #byte order for GPIB data transfer

        data=self.ask_for_values("CALC{}:MEAS:DATA:SDATA?".format(self._ci))
        data_size = np.size(data)
        datareal=np.array(data[0::2])
        dataimag=np.array(data[1::2])

        if format == 'RealImag':
          if self._zerospan:
            return np.mean(datareal), np.mean(dataimag)
          else:
            return datareal, dataimag
        elif format == 'AmpPha':
          if self._zerospan or self.get_cw(False):
            datacomplex = [np.mean(datareal + 1j*dataimag)]
            dataamp = np.abs(datacomplex)
            datapha = np.angle(datacomplex)
          else:
            dataamp = np.sqrt(datareal*datareal+dataimag*dataimag)
            datapha = np.arctan2(dataimag,datareal)
          return dataamp, datapha
        else:
          raise ValueError('get_tracedata(): Format must be AmpPha or RealImag')


    def get_freqpoints(self, query = False):
      if query:
           self.write("FORM:DATA REAL; FORM:BORD SWAPPED;")
           self._freqpoints = self.ask_for_values(':SENS%i:FREQ:RDAT? A'%(self._ci))
      elif self.get_cw():
           self._freqpoints = np.atleast_1d(self.get_cwfreq())
      else:
           self._freqpoints = np.linspace(self._start,self._stop,self._nop)
      return self._freqpoints

    ### GETs / SETs ###
    def do_get_Average(self):
        return self.ask("SENS{}:AVER?".format(self._ci))
    def do_set_Average(self, value):
        value = 1 if value else 0
        self.write("SENS{}:AVER {}".format(self._ci, value))
        return 

    def do_get_averages(self):
        return self.ask("SENS{}:AVER:COUN?".format(self._ci))
    def do_set_averages(self, value):
        self.write("SENS{}:AVER:COUN {}".format(self._ci, value))

    def do_get_bandwidth(self):
        return self.ask("SENS{}:BWID?".format(self._ci))
    def do_set_bandwidth(self, value):
        self.write("SENS{}:BWID {}".format(self._ci, value))
        return

    def do_get_centerfreq(self):
        return self.ask("SENS{}:FREQ:CENT?".format(self._ci))
    def do_set_centerfreq(self, value):
        self.write("SENS{}:FREQ:CENT {}".format(self._ci,value))

    def do_get_cw(self):
        return self.cw_mode
    def do_set_cw(self, status=1):
        if status:
            self.write("SENS{}:SWEEP:TYPE CW".format(self._ci))
            self.cw_mode=True
        else:
            self.write("SENS{}:SWEEP:TYPE LIN".format(self._ci))
            self.cw_mode=False
        return

    def do_get_cwfreq(self):
        return self.ask("SENS{}:FREQ:CW?".format(self._ci))
    def do_set_cwfreq(self, value):
        if(self.cw_mode):
            self.write("SENS{}:FREQ:CW {}".format(self._ci,value))
        else:
            raise ValueError("VNA not in CW mode.")
        return

    def do_set_edel(self, val):  # JB 2021

         '''
         Set electrical delay

         '''
         logging.debug(__name__ + ' : setting port extension to %s sec' % ( val))
         #self.write('SENS1:CORR:EXT:PORT%i:TIME %.12f' % (channel, val))
         self.write("CALC:MEAS:CORR:EDEL:TIME %.12f"%(val))
         self._edel=val
         return
         
     
    def do_get_edel(self):   # JB 2021

         '''
         Get electrical delay

         '''
         logging.debug(__name__ + ' : getting port extension')
         #self._edel = float(self.ask('SENS1:CORR:EXT:PORT%i:TIME?'% channel))
         self._edel = float(self.ask("CALC:MEAS:CORR:EDEL:TIME?"))
         return self._edel
         
    def do_set_edel_status(self, status):   # AS 04/2019

         '''
         Set electrical delay

         '''
         logging.debug(__name__ + ' : setting port extension status to %s' % (status))
         self.write('SENS:CORR:EXT:STAT %i' % (status))
         
     
    def do_get_edel_status(self):   # AS 04/2019

         '''
         Get electrical delay

         '''
         logging.debug(__name__ + ' :  port extension status')
         return  self.ask('SENS:CORR:EXT:STAT?').strip() == "1"

    def do_get_nop(self):
        return self.ask("SENS{}:SWE:POIN?".format(self._ci))
    def do_set_nop(self, value):
        return self.write("SENS{}:SWE:POIN {}".format(self._ci, value))

    def do_get_rf_output(self):
        return self.ask("OUTP?")
    def do_set_rf_output(self, state=True):
        return self.write("OUTP {}".format(state))

    def do_get_power(self, port=1):
        return self.ask("SOUR{}:POW{}?".format(self._ci,port))
    def do_set_power(self, value, port=1):
        return self.write("SOUR{}:POW{} {}".format(self._ci,port,value))

    def do_get_span(self):
        return self.ask("SENS{}:FREQ:SPAN?".format(self._ci))
    def do_set_span(self, value):
        self.write("SENS{}:FREQ:SPAN {}".format(self._ci, value))
        return

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
        self.get_centerfreq()
        self.get_stopfreq()
        self.get_span()
        
    def do_get_startfreq(self):
        '''
        Get Start frequency
        
        Input:
            None

        Output:
            span (float) : Start Frequency in Hz
        '''
        logging.debug(__name__ + ' : getting start frequency')
        self._start = float(self.ask('SENS%i:FREQ:STAR?' % (self._ci)))
        return  self._start

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
        self.get_startfreq()
        self.get_centerfreq()
        self.get_span()
    def do_get_stopfreq(self):
        '''
        Get Stop frequency
        
        Input:
            None

        Output:
            val (float) : Start Frequency in Hz
        '''
        logging.debug(__name__ + ' : getting stop frequency')
        self._stop = float(self.ask('SENS%i:FREQ:STOP?' %(self._ci) ))
        return  self._stop 



    def do_get_sweepmode(self):
        return self.ask("SENS{}:SWE:MODE?".format(self._ci))
    
    
    
    
    def do_set_sweepmode(self, value):
        if value in ["CONT","HOLD","SING","GRO"]: return self.write("SENS{}:SWE:MODE {}".format(self._ci, value))
        else:
            raise ValueError('Sweep mode unknown. Use: ["CONT","HOLD","SING","GRO"]')
        return

    def do_get_sweeptime(self):
        return self.ask("SENS{}:SWE:TIME?".format(self._ci))
    def do_get_sweeptime_averages(self):
        return self.get_sweeptime() * self.get_averages()

    ### COMM ###
    def write(self,msg):
        return self._visainstrument.write(msg)
    
    if visa.qkit_visa_version == 1:
        def ask(self, msg):
            return self._visainstrument.ask(msg)
    
        def ask_for_values(self, msg, **kwargs):
            return self._visainstrument.ask_for_values(kwargs)
    else:
        def ask(self, msg):
            return self._visainstrument.query(msg)
    
        def ask_for_values(self, msg, format=None, fmt=None):
            dtype = format if format is not None else fmt if fmt is not None else visa.single
            dtype = visa.dtypes[dtype]
            return self._visainstrument.query_binary_values(msg,datatype=dtype,container=np.array)
        
    def do_get_meas_parameter(self):
        '''
        Gets the current measurement parameter
        Input:
            None
        Output:
            String, one of:
                S11|S21|S31|S41|S12|S22|S32|S42|S13|S23|S33|S43|S14|S24|S34|S44|A|B|C|D|R1|R2|R3|R4|AUX1|AUX2
        '''
        return self.ask("CALC{}:PAR:CAT:EXT?".format(self._ci))

    def do_set_meas_parameter(self, value):
        '''
        Sets the current measurement parameter
        Input:
            String, one of:
                S11|S21|S31|S41|S12|S22|S32|S42|S13|S23|S33|S43|S14|S24|S34|S44|A|B|C|D|R1|R2|R3|R4|AUX1|AUX2
        Output:
           None
        '''
        self.write(":CALC:MEAS{}:PAR {}".format(self._ci,value))

    def pre_measurement(self):
        self.write("TRIG:SOUR MAN")
        self.write("SENS{}:AVER ON".format(self._ci))

    def start_measurement(self):
        self.avg_clear()
        self.write("TRIG:SOUR MAN")
        self.write("TRIG:SOUR IMM")
        sleep(0.1)
     


    def post_measurement(self):
        self.write("TRIG:SOUR IMM")
        self.write("SENS{}:AVER OFF".format(self._ci))
        self.hold(False)

