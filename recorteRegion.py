#Importacion de numpy, opencv y otros
import sys
import cv2
import ctypes
import numpy as np
from functools import partial

#Importaciones de PyQt5
from PyQt5 import QtWidgets,QtGui,QtCore
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.uic import loadUi

#Importacion de Clases
from ClasesTicket import *
from recorteImg import *

from recorteRegion import *

class recorteRegion(QDialog):
    def __init__(self,parent):
        super(recorteRegion,self).__init__(parent)
        loadUi("msgRecorte2.ui",self)
        self.imagen = None
        self.aux = None
        self.nombreRegion=""
        self.indiceTicket = 0
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        self.anchowin, self.alturawin = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        self.anchoImg = round(85/100*self.anchowin)
        self.alturaImg = round(85/100*self.alturawin)
        self.recorteLabel.setMaximumWidth(self.anchoImg)
        self.recorteLabel.setMaximumHeight(self.alturaImg)
        self.cortarImagenbtn.hide()
        self.guardarbtn.hide()
        self.comboNuevasRegiones.hide()
        self.labelRegionMsg.hide()
        self.continuarbtn.clicked.connect(self.cortarImagen)
        self.cortarImagenbtn.clicked.connect(self.cortarImagen)
        self.guardarbtn.clicked.connect(partial(self.gurdar,parent))
        self.comboNuevasRegiones.activated.connect(self.cambioRegion)

    #Evento para cerrar/guardar la imagen cortada
    def gurdar(self,parent):
        #Falta agregar el codigo para guardar las regiones seleccionadas mediante el metodo ROIs
        pass

    def cambioRegion(self):
        self.aux = self.imagen.copy()
        index = self.comboNuevasRegiones.currentIndex()
        img = recortarImagen(self.aux,self.puntos[index])
        img = formatoPixMap(img)
        img = img.scaled(self.anchoImg,self.alturaImg)
        self.recorteLabel.setPixmap(img)

    #Evento para cortar la imagen
    def cortarImagen(self):
        self.comboNuevasRegiones.clear()
        self.continuarbtn.hide()
        self.puntos=[]
        self.aux = self.imagen.copy()
        cv2.namedWindow("Imagen",cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Imagen",self.anchoImg,self.alturaImg)
        ROIs = cv2.selectROIs("Imagen",self.aux)
        cv2.destroyWindow("Imagen")
        for x in range (len(ROIs)):
            listaPuntos = [
                [ROIs[x][0],ROIs[x][1]],[ROIs[x][2],ROIs[x][1]],[ROIs[x][0],ROIs[x][3]],[ROIs[x][2],ROIs[x][3]]
            ]
            self.puntos.append(listaPuntos)
        for i in range (len(ROIs)):
            self.comboNuevasRegiones.addItem("Region "+str(i+1))
        self.dst = recortarImagen(self.aux,self.puntos[0])
        self.cortarImagenbtn.show()
        self.guardarbtn.show()
        self.comboNuevasRegiones.show()
        self.labelRegionMsg.show()
        self.imagenPixMap = formatoPixMap(self.dst)
        self.imagenPixMap = self.imagenPixMap.scaled(self.anchoImg,self.alturaImg)
        self.recorteLabel.setPixmap(self.imagenPixMap)
        self.recorteLabel.show()
        self.move(50,50)
        self.textLabel.hide()
        #nombreRegion = "Region_"+str(x+1)+"_"+nomticket#Nombre del ticket