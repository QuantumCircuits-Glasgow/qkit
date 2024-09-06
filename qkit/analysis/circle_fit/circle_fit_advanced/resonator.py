
import numpy as np
import pandas as pd
import scipy as sp
import matplotlib.pyplot as plt
import logging
import os


class Resonator:

    '''
    Theretical Resonator class holds a resonator model information
    Ideally complex S21/S11 data
    Attributes:
    1. fr: float -> Resonance frequency
    1a. _fr: float ->frequency Range
    2. Ql: float -> Loaded/External Q
    3. Qc: float -> Coupling Q
    4. Qi: float -> Internal Q
    5. Sij: [complexIQ]/(amplitude,phase) -> Sij data ; either for a single power or multiple power levels
    6. Pow: float -> Power level
    7. Temp: float -> Temperature
    8. photon: float -> Number of photons/ corresponding and calculated from power level 

    Methods :
    1. __init__ : Constructor

    2. generate(nop=5000, start_f, stop_f,fr,fano_b) : Generate the resonator model from the given parameters

    3. generate_mw_model(nop=5000, start_f, stop_f,fr,fano_b) : Generate the resonator model from the given parameters using scipy.mw

    4. save(filename) : Save the model to a file using pandas

    5. plot() : Plot the model

    6. load(filename) : Load the model from a file using pandas


    Note: # powers < the freqeuncy span of the resonator
    either 1D or 2D Sij data

    '''

#GLOBAL VARS



    # def __init__(self):
    #     #Object Vars
    #     self.fr=0.0
    

    def generate(self,nop=5000, start_f=4.5e9, stop_f=5.5e9,fr=5.0e9,fano_b=1.0e6):
        '''
        Generate the resonator model from the given parameters
        '''
        #TODO : Implement the function
        pass

    def generate_mw_model(self,nop=5000, start_f=4.5e9, stop_f=5.5e9,fr=5.0e9,fano_b=1.0e6):

        '''
        Generate the resonator model from the given parameters using scipy.mw
        '''
        #TODO : Implement the function
        pass

    def save(self,filename)->None:
        '''
        Save the model to a file using pandas
        '''
        #TODO : improve the saving format
        # pd.DataFrame.from_dict(self.__dict__).to_csv(str(filename))
        # return None

        

    def plot(self):
        '''
        Plot the model
        '''
        #TODO : Implement the  phase plot
        fig1, ax1 = plt.subplots(figsize=(10, 6))
        ax1.plot(self.f, np.abs(self._sij)) # type: ignore
        ax1.set_xlabel('Frequency (Hz)')
        ax1.set_ylabel('|Sij|')
        ax1.set_title('Resonator amplitude vs frequency')
        plt.show()

    def load(self,filename):
        '''
        Load the model from a file using pandas
        '''
        #TODO : Implement the function
        pass



    @property
    def sij(self):
        return self._sij
    
    @sij.setter
    def sij(self,s):
        '''
        Sij should be a list or a tuple
        if tuple, it should be a tuple of two lists (amplitude,phase)
        amplitude in form of [[pow1],[pow2],[pow3]...] <-> [powers , freqs] : each col is a power level from h5 file
        '''

        if (isinstance(s,(tuple,list)) and len(s) ==2)| (isinstance(s[0],list) and np.size(s)==2): #2D

            if np.shape(s[0][0]) == np.shape(s[1][0]) and np.shape(s[0][1]) == np.shape(s[1][1]):
                amps= np.array(s[0][:])
                phas= np.array(s[1][:])
                self._sij=np.array(np.multiply(amps,np.cos(phas))+(1j*np.multiply(amps,np.sin(phas))),dtype='complex')

            else :
                self._sij=None
                raise ValueError("Amplitude and Phase should be of same size")
        
            
        elif isinstance(s,(list,np.ndarray)): #1D

            if np.ndim(s)>=1:
                self._sij=np.array(np.reshape(s,-1),dtype='complex')

            else:
                self._sij=None
                raise ValueError("Sij should be a list or a tuple")
 
        else:
            self._sij=None
            raise ValueError("Sij should be a list or a tuple")

    @property
    def f(self):
        return self._f
    
    @f.setter
    def f(self,f):
        if np.size(f)!=np.max(np.shape(self._sij)):
            # logging.warning("Frequency should be of same size as Sij")
            self._f=np.arange(np.max(np.shape(self._sij)))
        elif np.size(f)>=1: 
            if (isinstance(f,list) or isinstance(f,np.ndarray)) :
                self._f=f

        else:
            # logging.warning("Frequency should be a list")
            self._f=None
            # raise ValueError("Frequency should be a list/numpy array")
            


    @property
    def fr(self):
        return self._fr


    @fr.setter
    def fr(self, f):
        if isinstance(self.fr, (np.ndarray, list)):
            if isinstance(f, (np.ndarray, list)):
                if np.size(f) < self._powers:
                    self._fr[:np.size(f)] = f
                else:
                    self._fr = f[:self._powers]
            elif isinstance(f, tuple):  # scalar #PASS INDEX AS TUPLE
                fval, idx = f
                self._fr[idx] = fval
            else:
                self._fr[-1] = f
        else:  # scalar
            if isinstance(f, (np.ndarray, list)):
                f = f[0]
            self._fr = f



    @property
    def Qi(self):
        return self._Qi

    @Qi.setter
    def Qi(self, q):
        if isinstance(self.Qi, (np.ndarray, list)):
            if isinstance(q, (np.ndarray, list)):
                if np.size(q) < self._powers:
                    self._Qi[:np.size(q)] = q
                else:
                    self._Qi = q[:self._powers]
            elif isinstance(q, tuple):  # scalar #PASS INDEX AS TUPLE
                qval, idx = q
                self._Qi[idx] = qval
            else:
                self._Qi[-1] = q
        else:  # scalar
            if isinstance(q, (np.ndarray, list)):
                q = q[0]
            self._Qi = q


    @property
    def Ql(self):
        return self._Ql

    @Ql.setter
    def Ql(self, q):
        if isinstance(self.Ql, (np.ndarray, list)):
            if isinstance(q, (np.ndarray, list)):
                if np.size(q) < self._powers:
                    self._Ql[:np.size(q)] = q
                else:
                    self._Ql = q[:self._powers]
            elif isinstance(q, tuple):  # scalar #PASS INDEX AS TUPLE
                qval, idx = q
                self._Ql[idx] = qval
            else:
                self._Ql[-1] = q
        else:  # scalar
            if isinstance(q, (np.ndarray, list)):
                q = q[0]
            self._Ql = q

    # @property
    # def Qc(self):
    #     Qci = np.divide(np.ones(self._powers), self._Ql) - np.divide(np.ones(self._powers), self._Qi)
    #     return np.divide(np.ones(self._powers), Qci)
    @property
    def Qc(self):
        return self._Qc

    @Qc.setter
    def Qc(self, q):
        if isinstance(self.Qc, (np.ndarray, list)):
            if isinstance(q, (np.ndarray, list)):
                if np.size(q) < self._powers:
                    self._Qc[:np.size(q)] = q
                else:
                    self._Qc = q[:self._powers]
            elif isinstance(q, tuple):  # scalar #PASS INDEX AS TUPLE
                qval, idx = q
                self._Qc[idx] = qval
            else:
                self._Qc[-1] = q
        else:  # scalar
            if isinstance(q, (np.ndarray, list)):
                q = q[0]
            self._Qc = q


    # @property #no setter
    # def Qc(self):
    #     Qci= np.divide(np.ones(self._powers),self._Ql)-  np.divide(np.ones(self._powers),self._Qi)
    #     return np.divide(np.ones(self._powers),Qci)
    


    @property
    def temp(self):
        return str(self._temp)
    
    @temp.setter
    def temp(self,t):
        self._temp=t

    @property
    def pow(self):
        return self._pow

    @pow.setter
    def pow(self,p):
        if isinstance(p,(list,np.ndarray)) and  np.ndim(self._sij)==1:
            self._pow=p[-1] # last element of the list
            self._powers=1
        elif isinstance(p,(list,np.ndarray))  and  np.ndim(self._sij)==2 and (np.size(p)!=np.min(np.shape(self._sij))):
            self._pow=p[:np.min(np.shape(self._sij))]
            self._powers=np.size(self._pow)

        else:
            # logging.warning("Power should be a list")
            self._pow=p # TODO : fix this; for now taking the first element of the list
            self._powers=np.size(self._pow)
        
    

    


    def __str__(self):
        return f"Resonator Model : \n fr : {self.fr} Hz \n Qi : {self.Qi} \n Ql : {self.Ql} \n Qc: {self.Qc} \n Temp : {self.temp} K \n Power : {self.pow} dBm\n"

    def __repr__(self):
        return f"Resonator Model : {type(self)} \n fr : {self._fr} Hz \n Qi : {self.Qi} \n Ql : {self.Ql} \n  Qc: {self.Qc} \n Temp : {self.temp} K \n Power : {self.pow} dBm \n"




    
    def __init__(self,Sij,f:list,fr:float=5.0e9 ,pow=20.0, Qi:float=1.0e6,Ql:float=1.0e6,Qc:float=50000,temp:float=26e-3)->None:
        # TODO :
        # 1. compare and fix the size of Sij with Power
        # 2. check Sij is complex or not
 
        self.sij=Sij# calls the setter
        self.f=f
        self.Qc:float
        self.pow=pow

        if (self._powers>1):
            self._fr=np.zeros(self._powers)
          
            self._Qi=np.zeros(self._powers)
   
            self._Ql=np.zeros(self._powers)

            self._Qc=np.zeros(self._powers)
               #TODO change this
            self.temp=temp
            # self.temp=np.zeros(self._powers)
        else :
            self._fr=0.
            self._Qi=0.
            self._Ql=0.
            self._Qc=0.

            self._temp=0.


        self.fr=fr
        self.Qi=Qi
        self.Ql=Ql
        self.Qc=Qc
        self.temp=temp


    
    
#-------------------TESTING-------------------#

if __name__ ==  "__main__":
    s=[[1+1.1j,3.2j],[1.1+7j,3.6j],[1.7+1j,3.2j]]
    s2=[[1+1.1j,3.2j],[1.1+7j,3.6j]]
    f=[3,4,5]
    r1=Resonator((np.abs(s),np.angle(s)),[1,2,3],[6e9,4e5,6e5,7e5],pow=[20,23,24],Qi=[2e6,3.4e6],Ql= [1e5,1e4])
    r2=Resonator(s,[1,2,3],[6e9,4e5,6e5,7e5],pow=[20,23,24],Qi=[2e6,3.4e6],Ql= [1e5,1e4])

    print(r1)
    print(r2)
    # print(r1.sij)
    r1.plot()
    # print(type(r1.Ql))
