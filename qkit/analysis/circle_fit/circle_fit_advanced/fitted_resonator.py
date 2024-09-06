
# from resonator import Resonator
# import numpy as np
from .resonator import Resonator
from .circle_fitter import *
import scipy.constants as const

class FittedResonator(Resonator):
    '''
    builds upon the resonator class and adds the fitting and photon pproperties
    Attributes:

    

    Methods:
    1. __init__ : Constructor
    
    #TODO update so that its an array of resonator objects at different powers
    #TODO : Update the attributes useing a property so that its either a list or a single value if one power.
    '''

    
    def __init__(self, sij,frequency, power=20.0, delay:float=None,temp:float =26e-3,fit:bool=False):
        
        super().__init__(sij,frequency,pow=power,temp=temp)
        # Resonator.Ql=0.0 # does not change the local variable

        # LOCAL vars
        
        self.beta=0
        self.centers:complex = []
        self.radii:float = []
        self.photon_number = self.pow #update this later

        self._fit=fit # flag to check if the fitting has been done
        self._fit_params = [] # list of fitting parameters



        self.delay= delay # electrical delay FIXED for all the resonators, depends on wire
        self.A = np.zeros(self._powers) # to update when fitting
        self.alpha =np.zeros(self._powers)# to update when fitting #TODO: update that its arg(A) and make A complex while fitting
        self.phi = np.zeros(self._powers) # impedance mismatch
        # self.Ql = 0.0 # list for all the Qls
        self.theta = np.zeros(self._powers)# to update when fitting
        self.Qc = np.zeros(self._powers)
        self.Qc_err = np.zeros(self._powers)  # errors for Qcx
        self.Qi = np.zeros(self._powers, dtype=float)
        self.Qi_err = np.zeros(self._powers, dtype=float)
        self.Ql = np.zeros(self._powers, dtype=float)
        self.Ql_err = np.zeros(self._powers, dtype=float)
        self.fr = np.zeros(self._powers, dtype=float)
        self.fr_err = np.zeros(self._powers, dtype=float)

        self.delay_remaining = np.zeros(self._powers, dtype=float)
        
        self.Qi_absqc = np.zeros(self._powers, dtype=float)
        self.Qi_absqc_err = np.zeros(self._powers, dtype=float)
        

        #update these internally/privately


    @classmethod
    def photon_from_P(self,P:float,fr:float,Ql:float,Qc:float)->float: #fr in GhZ
        '''
        Returns the photon number from the input power
        '''
        hbar = const.hbar
        pw = (10**(P/10))/1e3 # mW down to chip level
        # photnum_1p = 2*pw/(hbar*(2*3.14159*frvec_1p*1e9)**2)*(Qlvec_1p**2)/(Qcvec_1p)
        return 2*pw/(hbar*(2*const.pi*fr)**2)*(Ql**2)/(Qc)


    def fit(self,sij,f,power=None,delay=None)->dict:
        '''
        Fits the resonator using circle fit only with the complex data provided
        and returns the result dictionary,
        data flows from the fit->circle_fitter->notch_port and the results are retured back
        '''
        return notch_port(f,sij,delay=delay).fit_result(plot=True)
        
        

    def fit_all(self,index:int=-1):
        '''
        Fits the resonator for all the powers
        and updates all the object attributes
        from the result of the fit

        '''
        if self._powers>1 and index: # here sij is 2D
            for i,power in enumerate(self._pow):
                result=self.fit(self._sij[:,i],self._f,power,delay=self.delay) #result is a dictionary #FIX this which index to take later TODO
                self._fit_params.append({"power":power,
                                         "result":result})
                self.A[i]=result["a"]
                self.alpha[i]=result["alpha"]
                self.phi[i]=result["phi"]
                self.theta[i]=result["theta"]
                self.Qc=(result["Qc"],i)
                self.Qc_err=result["absQc_err"]

                self.Qi=(result["Qi"],i)
                self.Qi_err[i]=result["Qi_err"]


                self.Ql=(result["Ql"],i)
                self.Ql_err[i]=result["Ql_err"]

                self.fr=(result["fr"],i)
                self.fr_err[i]=result["fr_err"]

                self.delay_remaining[i]=result["delay_remaining"]

                self.Qi_absqc[i]=result["Qi_no_dia_corr"]
                self.Qi_absqc_err[i]=result["Qi_no_dia_corr_err"]

                self.photon_number[i]=self.photon_from_P(power,self._fr[i],self._Ql[i],np.abs(self.Qc[i]))
                self.centers.append(result["c"])
                self.radii.append(result["r0"])


        else:
            result=self.fit(self._sij,self._f,self._pow,delay=self.delay) #result is a dictionary but all the inputs are 1D
            self._fit_params.append({"power":self._pow,
                                         "result":result})
            self.A[0]=result["a"]
            self.alpha[0]=result["alpha"]
            self.phi[0]=result["phi"]
            self.theta[0]=result["theta"]
            self.Qc=result["Qc"] # setting will update the local variable, in setter fixed.
            self.Qc_err[0]=result["absQc_err"]

            self.Qi=result["Qi"] #TODO updates only the local this-class variable directly
            self.Qi_err[0]=result["Qi_err"]

            self.Ql=result["Ql"]
            self.Ql_err[0]=result["Ql_err"]

            self.fr=result["fr"]
            self.fr_err[0]=result["fr_err"]

            self.delay_remaining[0]=result["delay_remaining"]

            self.Qi_absqc[0]=result["Qi_no_dia_corr"]
            self.Qi_absqc_err[0]=result["Qi_no_dia_corr_err"]


            self.centers.append(result["c"])
            self.radii.append(result["r0"])



        self._fit=True
        

#-------------------Test-------------------
# #Test the FittedResonator class
if __name__== "__main__":
    fr = FittedResonator([1+1j,2+2j,3+3j],5.0e9,power=[1.0,2.0])
    print(fr.__dict__)
    fr.plot()
# fr = FittedResonator([1+1j,2+2j,3+3j],5.0e9,1.0,300)