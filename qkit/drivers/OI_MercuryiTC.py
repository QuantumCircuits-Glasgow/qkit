# Oxford Instruments MercuryiTC driver
# Joao Barbosa <j.barbosa.1@research.gla.ac.uk>, 2023
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

import qkit
from qkit.core.instrument_base import Instrument
from qkit import visa
from qkit.storage import store as hdf
from qkit.measure.measurement_class import Measurement
from qkit.gui.plot import plot as qviewkit

import types
import logging
from time import sleep, localtime, strftime
import numpy as np


class OI_MercuryiTC(Instrument):
    '''
    This is the python driver for the OI MercuryiTC temperature controller

    Usage:
    Initialise with
    <name> = qkit.instruments.create('<name>', address='<TCPIP address with port>')
    <name>.gets_()
    <name>.sets_()
    <name>.some_function()
    

    '''
    def __init__(self, name, address):
        logging.info(__name__ + ' : Initializing instrument')
        Instrument.__init__(self, name, tags=['physical'])

        self._address = address
        self._visainstrument = visa.instrument(self._address)
        self._visainstrument.read_termination="\n"

        #Plotting
        self._measurement_object = Measurement()
        self._data_file=None
        self.comment=''

        self.open_qviewkit = True
        self.qviewkit_singleInstance = False


        #List of Temperature Sensors and Heaters IDS
        self.list_temp={}
        self.list_htr={}

        self.add_parameter("temperature", flag=Instrument.FLAG_GET, type=float, units="K")
        self.add_parameter("htr_power", flag=Instrument.FLAG_GETSET, type=float, units="W")
        self.add_parameter("htr_resistance", flag=Instrument.FLAG_GETSET, type=float, units="Ohm")

        self.add_function("init_boards")
        self.add_function("assign_htr_temp_control")
        self.add_function("temp_setpoint")
        self.add_function("temp_control")
        self.add_function("set_pid_settings")
        self.add_function("get_all")

        self.init_boards()
    
    #GETSETS
    def do_get_temperature(self, temp_board=None):
        if(temp_board):
            return float(self.ask("READ:DEV:"+temp_board+":SIG:TEMP").split("SIG:TEMP:")[1].strip("K"))
        else:
            return None
    
    def do_get_htr_power(self, htr_board=None):
        if(htr_board):
            return float(self.ask("READ:DEV:"+htr_board+":SIG:POWR").split("SIG:POWR:")[1].strip("W"))
        else:
            return None
    
    def do_get_htr_resistance(self, htr_board=None):
        '''
            Gets heater board resistance.
        '''
        if(htr_board):
            return float(self.ask("READ:DEV:"+htr_board+":RES").split("RES:")[1])
        else:
            return None


    def do_set_htr_power(self, value=0, htr_board=None):
        '''
            Sets heater power, based on applied voltage(!)

            Inputs:
                -> htr_board ID  (string)

                -> Power (in Watts)
            
        '''
        res=self.do_get_htr_resistance(htr_board=htr_board)
        voltage= np.sqrt(res*value)
        #print(voltage)
        return self.ask("SET:DEV:"+htr_board+":SIG:VOLT:"+str(voltage))



    def do_set_htr_resistance(self, value=50, htr_board=None):
        '''
            Sets the heater board resistance.
            Note: it seems when the resistance is set for one htr board, the other htr board also gets assigned the same resistance
        '''
        if(htr_board):
            return (self.ask("SET:DEV:"+htr_board+":RES:"+str(value)))
        else:
            return None
        
    
    # def do_set_htr_power(self, htr_board=None, power):
    #     if(htr_board):
    #         res=float(self.ask("READ:DEV:"+htr_board+":RES"))
    #         return float(self.ask("READ:DEV:"+htr_board+":RES").split("SIG:POWR:")[1].strip("W"))
    #     else:
    #         return None


    #Other functions

    def init_boards(self):
        self.list_temp={}
        self.list_htr={}

        out=self.ask("READ:SYS:CAT").split("DEV:")
        out=out[1:]
        for dev in out:
            if(dev.split(".")[1].startswith("T")):
                name=self.ask("READ:DEV:"+dev.strip(":")+":NICK").split("NICK:")[1]
                self.list_temp[(dev.strip(":"))] = name
            elif(dev.split(".")[1].startswith("H")):
                name=self.ask("READ:DEV:"+dev.strip(":")+":NICK").split("NICK:")[1]
                self.list_htr[(dev.strip(":"))] = name
            else:
                raise Exception("Board not identified")
        return self.list_temp,self.list_htr
    
    def assign_htr_temp_control(self, temp_board, htr_board):
        '''
            Assigns a heater board to a temperature sensor.
            By default, VT sensor and GGHS sensor already have this assigned
        '''
        return self.ask("SET:DEV:"+temp_board+":LOOP:HTR:"+htr_board)

    def temp_setpoint(self, temp_board, value):
        return self.ask("SET:DEV:"+temp_board+":LOOP:TSET:"+str(value))

    def temp_control(self, temp_board, htr_board, status="OFF"):
        '''
            Starts/Stops temperature PID control loop for specific temperature/heater loop

            Inputs:
                -> temp_board ID  (string)
                -> status ("ON" or "OFF")
        '''
        if (status=="OFF" or status=="ON"):
            if(status == "OFF"):
                self.do_set_htr_power(0,htr_board)
            return self.ask("SET:DEV:"+temp_board+":LOOP:ENAB:"+status)
        else:
            return "Wrong status: either ON or OFF"

    def set_pid_settings(self, temp_board,  P, I, D, auto=False):
        '''
            Sets PID settings for temp-htr control loop
        '''
        if(auto):
            self.ask("SET:DEV:"+temp_board+":LOOP:P:"+str(P))
            self.ask("SET:DEV:"+temp_board+":LOOP:I:"+str(I))
            self.ask("SET:DEV:"+temp_board+":LOOP:D:"+str(D))
        else:
            return self.ask("SET:DEV:"+temp_board+":LOOP:PIDT:ON")


    def get_all(self):
        out_str=""
        for key in self.list_temp:
            a=self.do_get_temperature(temp_board=key)
            out_str=out_str+"{} : {}K\n".format(self.list_temp[key],a)

        out_str=out_str+"\n"
        for key in self.list_htr:
            a=self.do_get_htr_power(htr_board=key)
            out_str=out_str+"{} : {}W\n".format(self.list_htr[key],a)
        print(out_str)
        return
    
    #COMM functions
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
