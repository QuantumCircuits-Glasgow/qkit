# Main Driver for 3K fridge (Ocnus)
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


class Oxford_Ocnus(Instrument):
    '''
    This is the central python driver to control OI 3K Fridge (Ocnus)
    Uses:
        -Real time plotting and logging of temperatures
        -Start/Stop Pulse Tube Cooler

    Usage:
    Initialise with
    <name> = qkit.instruments.create('<name>', "Oxford_Ocnus", therm = <qkit instrument object>, pt = <qkit_instrument object>)
    <name>.gets_()
    <name>.sets_()
    <name>.some_function()
    

    '''
    def __init__(self, name, therm=None, pt=None):
        logging.info(__name__ + ' : Initializing instruments')
        Instrument.__init__(self, name, tags=['physical'])

        self.therm = therm #thermometry instrument
        self.pt = pt #pulse tube instrument

        #Plotting
        self._measurement_object = Measurement()
        self._data_file=None
        self._comment=''

        self.open_qviewkit = True
        self.qviewkit_singleInstance = False


        self.add_function("start_cooldown")
        self.add_function("stop_cooldown")
        self.add_function("start_pt")
        self.add_function("stop_pt")
        self.add_function("get_thermometry")
        self.add_function("set_temp_gghs")
        self.add_function("set_temp_vt")
        self.add_function("plotview")
        self.add_function("get_VTplate_Temp")
        self.add_function("get_PT2plate_Temp")
        self.add_function("get_PT1plate_Temp") 
        self.add_function("get_GGHS_Temp")


    def start_cooldown(self):
        '''
        Starts the cooldown by turning on Pulse Tube and starting the temperature logging and plotting
        '''
        self.start_pt() 
        self.plotview() 
        return

    def stop_cooldown(self):
        '''
        Stops the cooldown by turning off Pulse Tube.
        Temperature log [plotview function] must be interrupted before (interrut jupyter kernel with II)
        '''
        self.stop_pt() 
        return

    def start_pt(self):
        '''
        Starts Pulse Tube
        '''
        
        return 
    
    def stop_pt(self):
        '''
        Stops Pulse Tube
        '''
        return

    def get_thermometry(self):
        '''
        Returns all information from thermometry
        '''
        return self.therm.get_all()
    
    def get_VTplate_Temp(self):
        '''
        Returns all information from thermometry
        '''
        return self.therm.get_temperature(temp_board="MB1.T1:TEMP")
    
    def get_PT1plate_Temp(self):
        '''
        Returns all information from thermometry
        '''
        return self.therm.get_temperature(temp_board="DB8.T1:TEMP")
    
    def get_PT2plate_Temp(self):
        '''
        Returns all information from thermometry
        
        '''
        PT2_Temp = self.therm.get_temperature(temp_board="DB7.T1:TEMP")
        return PT2_Temp
    
    def get_GGHS_Temp(self):
        '''
        Returns all information from thermometry
        '''
        return self.therm.get_temperature(temp_board="DB6.T1:TEMP")

    def set_temp_gghs(self, value, status="ON"):
        '''
        Sets temperature set point for GGHS and turns on or off PID loop
        Input:
            -> value (float)
            -> status (string)
        '''
        self.therm.temp_setpoint("DB6.T1:TEMP", value)
        self.therm.temp_control("DB6.T1:TEMP",'DB1.H1:HTR', status=status)
    
    def set_temp_vt(self, value, status="ON"):
        '''
        Sets temperature set point for VT stage and turns on or off PID loop and heater power
        Input:
            -> value (float)
            -> status (string)
        '''
        self.therm.temp_setpoint("MB1.T1:TEMP", value)
        self.therm.temp_control("MB1.T1:TEMP", 'MB0.H1:HTR', status=status)

    def plotview(self, file=None, meas_delay=5):
        '''
        Plot temperature data in real time using qviewkit gui
        Must be interrupted manually (in jupyter kernel)
        '''
        if not file:
            self._file_name = "Cooldown_"+strftime("%Y%b%d", localtime())
            self._data_file = hdf.Data(name=self._file_name, mode='a')
            self._measurement_object.uuid = self._data_file._uuid
            self._measurement_object.hdf_relpath = self._data_file._relpath
            self._measurement_object.instruments = qkit.instruments.get_instrument_names()

            self._measurement_object.save()
            self._mo = self._data_file.add_textlist('measurement [cooldown]')
            self._mo.append(self._measurement_object.get_JSON())

            #add time coordinate
            self._data_time=self._data_file.add_coordinate('time', unit='s')
            self._data_time.add(np.array([]))
            
            self._data_time_=self._data_file.add_textlist('time_')
            self._data_time_.add(np.array([]))


            #add temperature vectors
            self._data_pt1 = self._data_file.add_value_vector('PT1', x=self._data_time, unit='K', save_timestamp=False)
            self._data_pt2 = self._data_file.add_value_vector('PT2', x=self._data_time, unit='K', save_timestamp=False)
            self._data_vt = self._data_file.add_value_vector('VT', x=self._data_time, unit='K', save_timestamp=False)
            self._data_gghs = self._data_file.add_value_vector('GGHS', x=self._data_time, unit='K', save_timestamp=False)

            self._data_test = self._data_file.add_view("Multiplot",x=self._data_time,y=self._data_pt1, view_params={"labels":["Time","Temperature"]})
            self._data_test.add(x=self._data_time, y=self._data_pt2)
            self._data_test.add(x=self._data_time, y=self._data_vt)
            self._data_test.add(x=self._data_time, y=self._data_gghs)

            if self.qviewkit_singleInstance and self.open_qviewkit and self._qvk_process:
                self._qvk_process.terminate()  # terminate an old qviewkit instance

            if self.open_qviewkit:
                self._qvk_process = qviewkit.plot(self._data_file.get_filepath(), datasets=['PT1', 'PT2', 'VT', 'GGHS'])

            try:
                timev=0
                while(1):
                    self._data_pt1.append(self.therm.get_temperature(temp_board="DB8.T1:TEMP"))
                    self._data_pt2.append(self.therm.get_temperature(temp_board="DB7.T1:TEMP"))
                    self._data_vt.append(self.therm.get_temperature(temp_board="MB1.T1:TEMP"))
                    self._data_gghs.append(self.therm.get_temperature(temp_board="DB6.T1:TEMP"))
                    self._data_time.append(timev)
                    self._data_time_.append(strftime("%d/%b/%Y, %H:%M:%S", localtime()))
                    sleep(meas_delay)
                    timev=timev+meas_delay
            except KeyboardInterrupt:
                print("Interrupted. Saving data ...")

            print(self._data_file.get_filepath())
            self._data_file.close_file()

        else:
            self._data_file=hdf.Data(name=file, mode="a")
            self._data_file.hf.ds_type=1
            self._data_time=self._data_file.get_dataset("/entry/" + "data" + "0/" + "time")
            self._data_pt1=self._data_file.get_dataset("/entry/" + "data" + "0/" + "pt1")
            self._data_pt2=self._data_file.get_dataset("/entry/" + "data" + "0/" + "pt2")
            self._data_vt=self._data_file.get_dataset("/entry/" + "data" + "0/" + "vt")
            self._data_gghs=self._data_file.get_dataset("/entry/" + "data" + "0/" + "gghs")
            
            self._data_time_=self._data_file.get_dataset("/entry/" + "data" + "0/" + "time_")
            
            #Get last time value and add 100 to distinguish plot breaks
            timev=self._data_file.data.time[-1]+100
            
            if self.qviewkit_singleInstance and self.open_qviewkit and self._qvk_process:
                self._qvk_process.terminate()  # terminate an old qviewkit instance
            
            #if self.open_qviewkit:
            #    self._qvk_process = qviewkit.plot(self._data_file.get_filepath(), datasets=['PT1', 'PT2', 'VT', 'GGHS'])

            try:
                while(1):
                    self._data_file.hf.ds_type=1 #quick fix
                    self._data_pt1.append(self.therm.get_temperature(temp_board="DB8.T1:TEMP"))
                    self._data_pt2.append(self.therm.get_temperature(temp_board="DB7.T1:TEMP"))
                    self._data_vt.append(self.therm.get_temperature(temp_board="MB1.T1:TEMP"))
                    self._data_gghs.append(self.therm.get_temperature(temp_board="DB6.T1:TEMP"))
                    self._data_time.append(timev)
                    
                    self._data_file.hf.ds_type=10 #quick fix
                    self._data_time_.append(strftime("%d/%b/%Y, %H:%M:%S", localtime()))
                    sleep(meas_delay)
                    timev=timev+meas_delay
            except KeyboardInterrupt:
                print("Interrupted. Saving data ...")

            print(self._data_file.get_filepath())
            self._data_file.close_file()

        return
