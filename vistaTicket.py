#Importacion de numpy, opencv y otros
import sys
import cv2
import ctypes
import numpy as np
from functools import partial
from fuzzywuzzy import process

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

class vistaTicket(QDialog):
    def __init__(self,parent):
        super(vistaTicket,self).__init__(parent)
        loadUi("vistaTicket.ui",self)
        self.imagenTicket = None
        self.auximg = None
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        self.recorteRegionD = recorteRegion(self)
        self.anchowin, self.alturawin = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        self.widthImg = round(85/100*self.anchowin)
        self.heightImg = round(85/100*self.alturawin)
        #Declaracion de eventos de los botones
        self.btnCortarRegion.clicked.connect(partial(self.cortarRegion,parent))
        self.comboRegion.activated.connect(partial(self.seleccionarRegion,parent))
        self.btnVerRegiones.clicked.connect(partial(self.mostrarRegiones,parent))
        self.btnGuardarTexto.clicked.connect(partial(self.guardarTexto,parent))
        self.btnEliminar.clicked.connect(partial(self.eliminarRegion,parent))

    def eliminarRegion(self,parent):
        indexRegion = self.comboRegion.currentIndex()
        self.comboRegion.removeItem(indexRegion)
        parent.listaTickets[parent.indice][parent.indiceTicket].eliminarRegionByIndex(indexRegion)

    def guardarTexto(self,parent):
        textoUsuario = self.txtUsuario.toPlainText()
        if textoUsuario == "":
            msg = QMessageBox()
            msg.setText("El texto no debe estar vacioo")
            msg.setInformativeText('Introduzca un texto')
            msg.setWindowTitle("Error")
            msg.exec_()
        else:
            indexRegion = self.comboRegion.currentIndex()
            textoOCR = self.txtOCR.toPlainText()
            parent.listaTickets[parent.indice][parent.indiceTicket].setTextOCRRegion(textoOCR,indexRegion)
            parent.listaTickets[parent.indice][parent.indiceTicket].setTextoUsuarioRegion(textoUsuario,indexRegion)
            msg = QMessageBox()
            msg.setText("El texto se guardo correctamente")
            #msg.setInformativeText('Seleccione un ticket para procesar')
            msg.setWindowTitle("Exito!")
            msg.exec_()

    def mostrarRegiones(self,parent):
        auxImagen = self.imagenTicket.copy()
        arrayRegionesCoords = parent.listaTickets[parent.indice][parent.indiceTicket].getCoordsRegiones()
        #print("Regiones encontradas")
        #print(len(arrayRegionesCoords))
        img = dibujarRegiones(auxImagen,arrayRegionesCoords)
        img = formatoPixMap(img)
        imgW = round(37/100*self.anchowin)
        imgH = round(78.7/100*self.alturawin)
        img = img.scaled(imgW,imgH)
        self.imagen_ticketlabel.setPixmap(img)


    def cortarRegion(self,parent):
        text = str(parent.comboTicket.currentText())
        self.recorteRegionD.nombreTicket=text
        self.recorteRegionD.imagen = self.imagenTicket.copy()
        self.recorteRegionD.setModal(True)
        self.recorteRegionD.show()
    
    def seleccionarRegion(self,parent):
        indexRegion = self.comboRegion.currentIndex()
        coords = parent.listaTickets[parent.indice][parent.indiceTicket].getCoordsRegionbyIndex(indexRegion)
        auxImagen = self.imagenTicket.copy()
        imgRegion = dibujarRegion(auxImagen,coords)
        imgRegionSola = recortarImagen(self.imagenTicket,coords)
        texto = procesarTexto(self.imagenTicket,coords)
        self.txtOCR.setPlainText(texto)
        imgRegionSola = recortarImagen(self.imagenTicket,coords)
        imgRegionSola = formatoPixMap(imgRegionSola)
        self.imagen_region.setPixmap(imgRegionSola)
        imgRegion = formatoPixMap(imgRegion)
        imgW = round(37/100*self.anchowin)
        imgH = round(78.7/100*self.alturawin)
        imgRegion = imgRegion.scaled(imgW,imgH)
        self.imagen_ticketlabel.setPixmap(imgRegion)
