# Keysight EDU33210 Waveform Generator
# Joao Barbosa <j.barbosa.1@research.gla.ac.uk>, 2023

import qkit
from qkit.core.instrument_base import Instrument

from qkit import visa 

import logging
import numpy as np


class Keysight_EDU33210(Instrument):
    '''
    Driver for Keysight EDU33210 Waveform Generator

    '''

    def __init__(self, name, address):
        '''
        '''
        logging.info(__name__ + ': Initializing instrument Keysight EDU33210')
        super().__init__(name, tags=['physical'])

        self._address=address
        self._visainstrument = visa.instrument(self._address)

        self.add_parameter("frequency", type=float, flag=Instrument.FLAG_GETSET, units="Hz")
        self.add_parameter('amplitude', type=float,
            flags=Instrument.FLAG_GETSET, minval=0, maxval=2, units='Volts')
        self.add_parameter('offset', type=float,
            flags=Instrument.FLAG_GETSET, minval=-2, maxval=2, units='Volts')
        self.add_parameter('status', type=str,
            flags=Instrument.FLAG_GETSET)
        self.add_parameter('trigger_source', type=str,
            flags=Instrument.FLAG_GETSET)

        
        self.add_function("reset")
        self.add_function("trigger")
        self.get_all()

    def get_all(self):
        self.get("frequency")
        self.get("amplitude")
        self.get("offset")
        self.get("trigger_source")

    def reset(self):
        '''
        Resets instrument to factory default state
        '''
        return self.write("*RST")

    def trigger(self):
        return self.write("TRIG")

    def do_get_frequency(self):
        return self.ask("SOUR:FREQ?")

    def do_set_frequency(self, value=1):
        return self.write("SOUR:FREQ {}".format(value))

    def do_get_amplitude(self):
        return self.ask("SOUR:VOLT?")
    
    def do_set_amplitude(self, value=0):
        return self.write("SOUR:VOLT {}".format(value))
    
    def do_get_offset(self):
        return self.ask("SOUR:VOLT:OFFS?")
    
    def do_set_offset(self, value=0):
        return self.write("SOUR:VOLT:OFFS {}".format(value))
    
    def do_get_status(self):
        return self.ask("OUTP?")

    def do_set_status(self, value=0):
        if(value in [0,1,"ON","OFF"]):
            return self.write("OUTP {}".format(value))
        else:
            raise ValueError("Wrong Status Value. Pick from [0,1,'ON','OFF']")
    
    def do_get_trigger_source(self):
        return self.ask("TRIG:SOUR?")
    
    def do_set_trigger_source(self, value="IMM"):
        if(value in ["IMM","EXT","TIM","BUS"]):
            return self.write("TRIG:SOUR {}".format(value))
        else:
            raise ValueError("Wrong Trigger Source. Pick from [IMM,EXT,TIM,BUS]")

    

    

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