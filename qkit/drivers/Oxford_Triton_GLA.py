# Oxford_Triton.py
# Joao B. @UofG 02/2023
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
import socket
import logging


class Oxford_Triton_GLA(Instrument):
    '''
    Updated and simplified driver for OI Triton Dil Fridge (2023)
    Mostly to be used for temperature readings (to be combined with Spectroscopy/TimeDomain/IV/Scope sweeps)
    [TODO] Adding control functions for valves/pumps/...

    Usage:
    Initialise with
    <name> = instruments.create('<name>', address='<IP address>')

    '''
    
    def __init__(self, name, address) -> None:
        '''
        Initializes

        Input:
            name (string)    : name of the instrument
            address (string) : TCP/IP address (this address should have the port number, e.g. TCPIP0::10.22.197.64::22518::SOCKET")
                                This port number can be found in the registry editor on the Triton Control PC
        '''
        
        logging.info(__name__ + ' : Initializing instrument')
        super().__init__(name, tags=["physical"])
        
        self._address=address
        self._visainstrument = visa.instrument(self._address)
        self._visainstrument.read_termination = "<end>" #
        self._visainstrument.timeout=10000

        self._channels=8 # Default number of thermometry channels 

        #Temperature Channels
        self.temps=[0]*self._channels
        self._temp_dic={}

        #Heaters
        self.mxc_heater=0
        self.still_heater=0

        #Pressures 
        self.forepump=0
        self.condense=0
        self.tank=0

        #Valves
        self.v1=None
        self.v2=None
        self.v3=None
        self.v7=None
        self.v8=None

        #Pumps
        self.compressor=None
        self.fore=None
        self.turbo=None

        # Implement parameters
        self.add_parameter('temperature', type=float,
                           flags=Instrument.FLAG_GET,
                           minval=0, maxval=350,
                           units='K')
        
        # Implement functions
        self.add_function('get_all')
        self.add_function('get_status')
        self.add_function('get_pressures')
        self.add_function('get_thermometry')

        self.add_function("read_thermometry")
        self.add_function("read_pressures")
        self.add_function("read_status")
        

        self.get_all()
    
    
    ###
    # Communication with device
    ###

    def get_all(self):
        self.read_status()
        self.read_pressures()
        self.read_thermometry()
        

    def get_status(self):
        '''
            Gets status of pumps and valves
        '''
        a=self._ask(b"status\n")
        self.compressor=a[0].split(" ")[2]
        self.fore=a[1].split(" ")[2]
        self.turbo=a[2].split(" ")[2]
        self.v1=a[3].split(" ")[2]
        self.v2=a[4].split(" ")[2]
        self.v3=a[5].split(" ")[2]
        self.v7=a[6].split(" ")[2]
        self.v8=a[7].split(" ")[2]
        return

    def get_pressures(self):
        '''
            Gets pressures (tank, condense, forepump)
        '''
        a=self._ask(b"press\n")
        self.condense=float(a[1].split(" ")[1][:-3])
        self.tank=float(a[2].split(" ")[1][:-3])
        self.forepump=float(a[3].split(" ")[1][:-3])
        return 
    
    def get_thermometry(self):
        '''
            Gets all temperature readings of all channels defined (in K) + heater power (in W)
            Channels:
            1 -> PT2 HEAD [0]
            2 -> PT2 PLATE [1]
            3 -> STILL PLATE [2]
            4 -> COLD PLATE [3]
            5 -> MXC CERNOX [4]
            6 -> PT1 HEAD [5]
            7 -> PT1 PLATE [6]
            8 -> MXC RU02 [7]
        '''
        a=self._ask(b"thermometry\n")
        for i in range(self._channels):
            self.temps[i] = float(a[i].split(";")[7].split()[1])
        self.mxc_heater=float(a[-2].split(" ")[-1][:-1])
        self.still_heater=float(a[-1].split(" ")[-1][:-1])
        return


    def read_thermometry(self):
        self.get_thermometry()
        print("PT1 HEAD : {}K\nPT1 PLATE : {}K\nPT2 HEAD : {}K\nPT2 PLATE : {}K\nSTILL PLATE : {}K\nCOLD PLATE : {}K\nMXC CERNOX : {}K\nMXC RU02 : {}K\nMXC HEATER: {}W\nSTILL HEATER: {}W\n".format(self.temps[5],self.temps[6],self.temps[0],self.temps[1],self.temps[2],self.temps[3],self.temps[4],self.temps[7],self.mxc_heater,self.still_heater))
        
        return 
    
    def read_pressures(self):
        self.get_pressures()
        print("Tank: {}bar\nForepump : {}bar\nCondense: {}bar\n".format(self.tank,self.forepump,self.condense))
        return

    def read_status(self):
        self.get_status()
        print("Compressor: {}\nForepump: {}\nTurbo: {}\nV1: {}\nV2: {}\nV3: {}\nV7: {}\nV8: {}\n".format(self.compressor,self.fore,self.turbo,self.v1,self.v2,self.v3,self.v7,self.v8))
        return

    ###
    # GET and SET functions
    ###
    
    def do_get_temperature(self,channel=7):
        self.get_thermometry()
        return self.temps[channel]

    
    def _ask(self, cmd, debug=False):
        '''
            cmd -> bytestring
        '''
        self._visainstrument.write_raw(cmd)
        self._visainstrument.read_raw()
        if(debug):
            return self._visainstrument.read_raw().decode("utf-8").split("\n")
        else:
            return self._visainstrument.read_raw().decode("utf-8").split("\n")[1:-1]
