#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author: Wridhdhisom Karar (w.karar.1@research.gla.ac.uk) / 2024

inspired by and based on resonator tools of Sebastian Probst
https://github.com/sebastianprobst/resonator_tools

an update to all the circle fit models
- iterative with scipy-curvefit / gradient based
- iterative with lmfit
- algebric moments method
- ML,model based (yet to implement)
"""

import numpy as np
import logging
import scipy.optimize as spopt
from scipy import stats
from scipy.interpolate import splrep, splev
from scipy.ndimage.filters import gaussian_filter1d
plot_enable = False
try:
    import qkit
    if qkit.module_available("matplotlib"):
        import matplotlib.pyplot as plt
        plot_enable = True
except (ImportError, AttributeError):
    try:
        import matplotlib.pyplot as plt
        plot_enable = True
    except ImportError:
        plot_enable = False

class resonator:
    """
    Resonator class to define resonator model, with basic parameters and advanced fit parameters
    Essentially its a 2 port network object/ one port
    Initial Model parameters : 
        f_res : Resonant frequency
        type : series, parallel, notch_type
        Qi : 
        Qc :
        space for more ---

    The idea of the resonator class is to provide a data_structure model for fits.
    Each resonator measured will fit into this model by :
        - frequency array over which the resonator exists
        - holding 2D data of Qi @ P over a range of freqeuncies
        - with P, estimate the Photon numbers in the resonator
        - fit_params for each P for the model
        - fit_param_errors for a std_dev for each fit
        - can build a resonator from a model file
        - export to a touchstone format for scikit_rf two port network file / read from

    """


    def __init__(self) -> None:
        pass