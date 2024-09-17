# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 14:59:13 2024

@author: weideslab-admin
"""



import qkit
from qkit.core.instrument_base import Instrument
from qkit import visa
import types
import logging
from time import sleep
import numpy

class thinkrf_R5550(Instrument):
    '''
    This is the python driver for the Anritsu MS4642A Vector Network Analyzer

    Usage:
    Initialise with
    <name> = instruments.create('<name>', address='<GPIB address>', reset=<bool>)
    
    '''

    def __init__(self, name, address):
        '''
        Initializes 

        Input:
            name (string)    : name of the instrument
            address (string) : GPIB address
        '''
        
        logging.info(__name__ + ' : Initializing instrument')
        Instrument.__init__(self, name, tags=['physical'])

        self._address = address
        self._visainstrument = visa.instrument(self._address)
        if visa.qkit_visa_version > 1:
            # we have to define the read termination chars manually for the newer version
            idn = self._visainstrument.query('*IDN?')
            self._visainstrument.read_termination = idn[len(idn.strip()):]
        
        
    
        self.start_freq = 1e9
        self.stop_freq = 18e9
        
        self.add_parameter('centrefreq',  type=float, minval=0, maxval=18e9,  units='Hz')
        self.add_parameter('start_freq',  type=float, minval=0, maxval=18e9,  units='Hz')
        self.add_parameter('stop_freq',  type=float, minval=0, maxval=18e9,  units='Hz')
        
        
        #self.get_all()
        
    def reset(self):
        """
        Resets the RTSA to its default configuration. It does not affect
        the registers or queues associated with the IEEE mandated commands.
        """
        self.write("*RST")
    
        
    def abort(self):
        """
        This command will cause the RTSA to stop the data capturing,
        whether in the manual trace block capture, triggering or sweeping
        mode.  The RTSA will be put into the manual mode; in other
        words, process such as streaming, trigger and sweep will be
        stopped.  The capturing process does not wait until the end of a
        packet to stop, it will stop immediately upon receiving the command.
        """
        self.write(":SYSTEM:ABORT")

    def flush(self):
        """
        This command clears the RTSA's internal data storage buffer of
        any data that is waiting to be sent.  Thus, it is recommended that
        the flush command should be used when switching between different
        capture modes to clear up the remnants of captured packets.
        """
        self.write(":SYSTEM:FLUSH")
        
        
        
        
    def request_read_perm(self):
        """
        Acquire exclusive permission to read data from the RTSA.

        :returns: True if allowed to read, False if not
        """
        buf = yield self.ask(":SYSTEM:LOCK:REQUEST? ACQ")
        yield bool(int(buf))
        
        
    def identify(self):
        return self.ask('*IDN?')

        
    def write(self,msg):
        return self._visainstrument.write(msg)
    
    if qkit.visa.qkit_visa_version == 1:
        def ask(self, msg):
            return self._visainstrument.ask(msg)
    
        def ask_for_values(self, msg, **kwargs):
            return self._visainstrument.ask_for_values(kwargs)
    else:
        def ask(self, msg):
            return self._visainstrument.query(msg)
    
        def ask_for_values(self, msg, format=None, fmt=None):
            dtype = format if format is not None else fmt if fmt is not None else qkit.visa.single
            dtype = qkit.visa.dtypes[dtype]
            return self._visainstrument.query_binary_values(msg,datatype=dtype,container=numpy.array)
    
          
    
        
    def do_set_centrefreq(self, centrefreq):
        
        
        self.write(":sense:freq:center %f") % (self.centrefreq)
        
    def do_get_centrefreq(self):
        
        
        return self.ask(':sense:freq:center?')
        #self.write(':')
    
    
        