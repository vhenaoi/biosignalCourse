'''
Created on 2020

@author: Verónica Henao Isaza

'''
import numpy as np
import scipy.signal as signal
import os
from datetime import datetime
import pandas as pd
import serial, time
# -*- coding: utf-8 -*-
"""
Created on Thu Nov 22 12:56:57 2018

@author: SALASDRAI
"""
import numpy as np
class Biosenal(object):
    def __init__(self,data=None):
        if not data==None:
            self.asignarDatos(data)
        else:
            self.__data=np.asarray([])
    def asignarDatos(self,data):
        self.__data=data
    #necesitamos hacer operacioes basicas sobre las senal, ampliarla, disminuirla, trasladarla temporalmente etc
    def devolver_segmento(self,x_min,x_max):
        #prevengo errores logicos
        if x_min>=x_max:
            return None
        #cojo los valores que necesito en la biosenal
        return self.__data[x_min:x_max]

    def escalar_senal(self,x_min,x_max,escala):
        copia_datos=self.__data[x_min:x_max].copy()
        return copia_datos*escala
    
