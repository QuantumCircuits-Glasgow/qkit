# -*- coding: utf-8 -*-
"""
Created on Tue May  7 12:44:06 2024

@author: weideslab-admin
"""

import qkit
from qkit.core.instrument_base import Instrument
from qkit import visa
import types
import logging
import math
from time import sleep

class Rigol_DS7054(Instrument):
    '''
    This is the python driver for the Rigol_DS7054 Oscillioscope.
    

    Usage:
    Initialise with
    <name> = instruments.create('<name>', address='<GPIB address>')
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

        # Implement parameters
        
    def reset(self):
        self.write('*RST')
    def clear(self):
        self.write(':CLE')
    def write(self, command):
        self._visainstrument.write(command)    
    
    def ask(self, command):
        self._visainstrument.query(command)
        
    
    def identify(self):
        #return(self._visainstrument.query('*IDN?'))
        return( self._visainstrument.query('*IDN'))
    
    def run(self):
        self.write(':RUN')
        
    def stop(self):
        self.write(':STOP')    
    #def set_impedance(self):
        
    def SINGLE(self):
        self.write(':SING')
        
    def set_trigger(self, voltage, channel):
        self.write(':TRIGger:EDGE:SOURce CHAN%i' %channel)
        self.write(':TRIGger:EDGE:LEVel %f' %voltage)
        
    def set_timescale(self, timescale):
        self.write(':TIM:MAIN:SCAL %f' %(timescale))
    
    
    def set_timerefmode(self,mode):
        '''
        Set the timeref of the oscilloscope:
        CENTer
        LB
        RB
        TRIG
        USER
        '''
           
        if not mode in ("CENT","LB","RB","TRIG","USER"):
            raise ValueError("The selected mode is not supported, your choice was %s, but I have CENTer, LB, RB, TRIG, USER"%mode)
        return self.write(":TIM:HREF:%s",mode)
    
    def get_data(self, channel):
        #self.write(':STOP')
        self.write(':WAV:SOUR CHAN%i' %channel)
        self.write(':WAVeform:MODE NORM')
        self.write(':WAV:FORM ASCii')
        return  self._visainstrument.query(':WAVeform:DATA?')
    
    def get_dataRAW(self, channel, points):
        self.write(':SING')
        sleep(5)
        self.write(':WAV:SOUR CHAN%i' %channel)
        self.write(':WAVeform:MODE RAW')
        self.write(':WAV:FORM ASCii')
        self.write(':WAVeform:POINts %i' %points)
        return  self._visainstrument.query(':WAVeform:DATA?')