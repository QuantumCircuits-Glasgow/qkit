# filename: Keithley_2450.py
# version 0.1 written by 
# QKIT driver for a Keithley Multimeter 2450



import qkit
from qkit.core.instrument_base import Instrument

from qkit import visa 

import logging
import numpy
import time,sys
import atexit
#import serial #used for GPIB connections

class Keithley_2450_gla(Instrument):
    '''
    This is the driver for the Keithley 2450 Source Meter
    Set ip address manually on instrument, e.g. TCPIP::10.22.197.50::5025::SOCKET
    Usage:
    Initialize with
    <name> = qkit.instruments.create('<name>', 'Keithley_2450', address='<IP address>', reset=<bool>)
    '''

    def __init__(self, name, address, reset=False):
        '''
        Initializes the Keithley, and communicates with the wrapper.
        
        Input:
            name (string)    : name of the instrument
            address (string) : IP address
            reset (bool)     : resets to default values, default=False
        '''
        # Start VISA communication
        logging.info(__name__ + ': Initializing instrument Keithley 2450')
        Instrument.__init__(self, name, tags=['physical'])
        self._address = address
        self._visainstrument = visa.instrument(self._address)
        self._visainstrument.read_termination="\n"
        self._visainstrument.timeout = 5000
        self._rvol = 1
        self.rvc_mode   = False #resistance via current
        self.four_wire  = False
        #self.setup(address) #used for GPIB connections

    #def setup(self, device="COM1"):
     #   baudrate = 9600
     #   timeout = None #0.1
        
     #   self.ser = self._std_open(device,baudrate,timeout)
     #   atexit.register(self.ser.close)
        
    #def _std_open(self,device,baudrate,timeout):
        # open serial port, 9600, 8,N,1, timeout 0.1
      #  return serial.Serial(device, baudrate, timeout=timeout)
 

    # def remote_cmd(self, cmd):
    #     cmd += "\r"

    #     # clear queue first, old data,etc
    #     rem_char = self.ser.inWaiting()
    #     if rem_char:
    #         self.ser.read(rem_char)
        
    #     # send command
    #     self.ser.write(str.encode(cmd))
    #     # wait until data is processed
    #     time.sleep(1)
    #     # read back
    #     rem_char = self.ser.inWaiting()
        
    #     retval = self.ser.read(rem_char)
    #     #print(retval)
    #     return retval #str(retval)#.strip('\r')

    def reset(self):
        '''
        Resets the instrument to default values

        Input:
            None

        Output:
            None
        '''
        logging.info(__name__ + ' : resetting instrument')
        self._visainstrument.write('*RST')
        #self.get_all()     
    
    # def get_current_dc(self):   #Return DC Current in auto-range
    #     value = self.remote_cmd(":MEAS:CURR:DC?")
    #     try:
    #         return float(value)
    #     except Exception as m:
    #         print(m)
    #         return 

    def trigger(self):   #Return DC Current in auto-range
        self._visainstrument.write("*TRG")        




    def get_current_dc(self):   #Return DC Current in auto-range
        value = self._visainstrument.query(":MEAS:CURR:DC?")
        try:
            return float(value)
        except Exception as m:
            print(m)
            return         
    
    def get_voltage_dc(self):   #Return DC Current in auto-range
        value = self._visainstrument.query(":MEAS:VOLT:DC?")
        try:
            return float(value)
        except Exception as m:
            print(m)
            return       

    def get_resistance(self):
        if self.rvc_mode:
            return self._rvol/self.get_data()
        else:
            if self.four_wire:
                return self.get_resistance_4W()
            else:
                return self.get_resistance_2W()
                
    def get_data(self, startindex, endindex):
        '''Ending index of the buffer has to be specified'''
        try:
            ret = self._visainstrument.query(":TRACe:DATA? {}, {}".format(startindex,endindex))
            return float(ret)
        except ValueError as e:
            print(e)
            print(ret)
            return numpy.NaN        

    def get_resistance_2W(self):
        try:
            self._visainstrument.write(":OUTP ON")
            ret = self._visainstrument.query(":MEAS:RES?")
            self._visainstrument.write(":OUTP OFF")
            return float(ret)
            
        except ValueError as e:
            print(e)
            print(ret)
            return numpy.NaN

    def get_resistance_4W(self):
        try:
            self._visainstrument.write(":OUTP ON")
            ret = self._visainstrument.query(":MEAS:RES?")
            self._visainstrument.write(":OUTP OFF")
            return float(ret)
        except ValueError as e:
            print(e)
            print(ret)
            return numpy.NaN

    def set_4W(self,N=1):
        ''' Sets 2 or 4 wire measurement mode 
        0 - 2-wire measurement, and 1 - 4-wire measurement'''
        self._visainstrument.write(':VOLT:RSEN {}'.format(N))

 
        
    # def set_resistance_via_current(self, status):
    #     self.rvc_mode = status
    #     self._visainstrument.write(str.encode(":SENS:CURR \r"))  
    #     self._visainstrument.write(str.encode(":SENS:CURR:DC:RANG:AUTO OFF \r"))
    #     self._visainstrument.write(str.encode(":SENS:CURR:DC:RANG 1e-3 \r"))

    def set_resistance_via_current(self, status):
        self.rvc_mode = status
        self._visainstrument.write(":SENS:FUNC:CURR")  
        self._visainstrument.write(":SENS:CURR:DC:RANG:AUTO OFF")
        self._visainstrument.write(":SENS:CURR:DC:RANG 1e-3")

    def set_reverence_voltage(self, voltage):
        self._rvol = voltage
        
    # def set_current_range(self, range_value):
    #     if 1e-3 <= range_value <= 1:
    #         self._visainstrument.write(str.encode(":CURR:DC:RANG %.04f \r"%(range_value)))
    #     else:
    #         print("Range must be decimal power of 10 between 1A and 10mA")

    def set_current_range(self, range_value):
        self._visainstrument.write(":SENS:CURR:RANG {}".format(range_value))

    def set_output(self, output):
        if output:
            self._visainstrument.write(":OUTP ON")
        else:
            self._visainstrument.write(":OUTP OFF")

    def set_voltage_source(self, volt):
        #self._visainstrument.write("SENS:FUNC 'CURR'") 
        self._visainstrument.write("SOUR:FUNC VOLT")
        self._visainstrument.write("SOUR:VOLT {}".format(volt))

    def set_current_source(self, curr):
        #self._visainstrument.write("SENS:FUNC 'VOLT'")
        self._visainstrument.write("SOUR:FUNC CURR")
        self._visainstrument.write("SOUR:CURR {}".format(curr))

    def set_voltage_range(self, range_value):
        self._visainstrument.write(":SENS:VOLT:RANG {}".format(range_value))

    def set_current_range_auto(self, auto):
        if auto:
            self._visainstrument.write(":SENS:CURR:RANG:AUTO ON")
        else:
            self._visainstrument.write(":SENS:CURR:RANG:AUTO OFF")

    def set_voltage_range_auto(self, auto):
        if auto:
            self._visainstrument.write(":SENS:VOLT:RANG:AUTO ON")
        else:
            self._visainstrument.write(":SENS:VOLT:RANG:AUTO OFF")

    bufferElementTable = {#table of the possible options for bufferElements when used (specified in manual)
        "DATE": "The date when the data point was measured",
        "FORM":"The measured value as it appears on the front panel",
        "FRAC":"The fractional seconds for the data point when the data point was measured",
        "READ":"The measurement reading based on the SENS:FUNC setting; if no buffer elements are defined, this option is used",
        "REL":"The relative time when the data point was measured",
        "SEC":"The seconds in UTC (Coordinated Universal Time) format when the data point was measured",
        "SOUR":"The source value; if readback is ON, then it is the readback value, otherwise it is the programmed source value",
        "SOURFORM":"The source value as it appears on the display",
        "SOURSTAT":"The status information associated with sourcing",
        "SOURUNIT":"The unit of value associated with the source value",
        "STAT":"The status information associated with the measurement The time for the data point",
        "TIME":"The timestamp for the data point",
        "UNIT":"The unit of measure associated with the measurement"}
    possibleModes = ["CURR","VOLT","RES"]#keithley can only be in these modes
    possibleBoundaries=["MIN","MAX","DEF"]
    def printBufferElementTable(self,includeDetails=False):
        '''Print out the buffer element table, with an option to include the details of each element'''
        if includeDetails:
            print("Possible buffer elements, including descriptions:")
            for elmt, desc in self.bufferElementTable.items():
                print("'{element}': {description}".format(element=elmt,description = desc))
        else:
            print("Possible buffer elements:")
            print("\n".join(self.bufferElementTable.keys()))

    def _validateParameters(self, mode:str=None,readingElements:"tuple[str,...]"=None,boundary:str=None)-> "tuple[bool, str]":
        '''
        For each scpi function, call this method and provide the relevant parameters to validate entries

        Returns a (bool,str) tuple, where 1st element (bool) indicates true/false for success/failure 
         and 2nd element (str) indicates description of failure
        
        Leave the unwanted parameters = None if you dont want to validate them

        Supported parameters:
        - readingElements (refer to bufferElementsTable)
        - mode ('CURR', 'VOLT' 'RES')
        - boundary ('DEF', 'MIN', 'MAX')
        '''
        logging.debug("Validating Parameters")
        if (mode!=None):
            mode=mode.upper()
            if (mode not in self.possibleModes):
                return (False,"Invalid mode")

        if readingElements!= None or len(readingElements)==0:
            for i in readingElements:#making sure each buffer element is correct
                if i.upper() not in self.bufferElementTable:
                    return (False,"Invalid Buffer Element")
        
        if (boundary != None) & (boundary.upper() not in self.possibleBoundaries):
            return (False,"Invalid boundary values")

        return (True,"")
        #then return true if all checks go fine
   
    def get_latest_reading(self,bufferName:str="defbuffer1",*readingElements:str):
        '''
        Returns the latest reading from a given/default reading buffer

        - 'bufferName': (optional) name of buffer where 'defbuffer1' is the default buffer

        - 'readingElements': (optional) variadic paramters (up to of 14) determining what aspects of the reading get returned
            E.g: 'DATE', 'UNIT'
        
        Note: if you want to add readingElements, you need to specify bufferName first
        
        If you're not sure what bufferName to use, use 'defbuffer1' (default)
        '''
        logging.debug("Getting latest reading")
        #preventive error handling
        test = self._validateParameters(None,readingElements)
        if test[0]==False:
            print("Error:",test[1])
            return None
        if len(readingElements)>0:#for correct formatting of query, need to handle differently if no elements passed 
            return self._visainstrument.query(':FETCh "{bName}", {elements}'.format(bName = bufferName,elements = ", ".join(readingElements)))
        else:
            return self._visainstrument.query(':FETCh "{bName}"'.format(bName = bufferName))#just get the plain reading as it is
    

    def make_measurement(self,mode:str,bufferName:str="defbuffer1",*readingElements:str):
        '''
        Makes a measurement using the specified function mode, stores and returns the measurement in a reading buffer

        - 'mode': specify either 'CURR', 'RES', 'VOLT' to get a current, resistance or voltage measurement respectively

        - 'bufferName': (optional) name of buffer where 'defbuffer1' is the default buffer

        - 'readingElements': (optional) variadic paramters (up to 14) determining what aspects of the reading get returned (look up bufferElementTable)
        
        Note: 

            - if you want to add readingElements, you need to specify bufferName first

            - If you're not sure what bufferName to use, use 'defbuffer1' (default)

            - the 'mode' parameter will change the measurement function to the specified one, and this change will persist
        '''
        logging.debug("Making measurement")
        test = self._validateParameters(mode,readingElements)
        if test[0]==False:
            print("Error:",test[1])
            return None
        if len(readingElements)>0:
            return self._visainstrument.query(':MEAS:{mode}? "{bName}", {elements}'.format(mode=mode, bName = bufferName,elements = ", ".join(readingElements)))
        else:
            return self._visainstrument.query(':MEAS:{mode}? "{bName}"'.format(mode=mode,bName=bufferName))

    #Display (:DISPlay) function
    def set_display_digits(self,numDigits:int,mode:str=None):
        '''
        Set the number of digits displayed on the front panel for a given measurement function (changes will persist)
         - 'mode': specify either 'CURR', 'RES', 'VOLT' to get current, resistance or voltage measurement functions respectively
                - if mode is set to None, then all 3 measurement functions will be changed 
         - 'numDigits': the number of digits to set the display to. Use an integer value
        
        Note: this does NOT affect the accuracy or speed of measurements.
        '''
        logging.debug("Setting display digits")
        test = self._validateParameters(mode)
        if test[0]==False:
            print("Error:",test[1])
            return None
        numDigits=str(numDigits)
        if mode == None:#then all 3 measurement functions get changed
            self._visainstrument.write(':DISP:DIG {digits}'.format(digits=numDigits))
        else:
            self._visainstrument.write(':DISP:{mode}:DIG: {digits}'.format(mode = mode,digits=numDigits))
    def get_display_digits(self,mode:str,boundary:str=None):
        '''
        Get the number of digits dispayed for a given measurement function
        - 'mode': specify either 'CURR', 'RES', 'VOLT' to get current, resistance or voltage measurement functions respectively
        - 'boundary': (optional) specify the following string values to get the relevant data:
                - DEF to get to the default number of digits
                - MIN to get to the minimum number of digits allowed
                - MAX to get to the maximum number of digits allowed 
        '''
        logging.debug("getting number of digits displayed")
        test = self._validateParameters(mode,None,boundary)
        if test[0]==False:
            print("Error:",test[1])
            return None
        if boundary==None:
            return float(self._visainstrument.query(':DISP:{mode}:DIG?'.format(mode=mode)))
        else:
            return float(self._visainstrument.query(':DISP:{mode}:DIG? {boundary}'.format(mode=mode,boundary=boundary)))
              

if __name__ == "__main__":
    KEITH = Keithley_2450(name = "Keithley_2450", address="10.22.197.8")
    print("DC current: {:.4g}A".format(KEITH.get_current_dc()))
