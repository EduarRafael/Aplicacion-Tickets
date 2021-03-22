#Importacion de numpy, opencv y otros
import sys
import cv2
import ctypes
import numpy as np
from functools import partial
from fuzzywuzzy import process
from sys import platform
import subprocess
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
        self.TicketAux = None
        self.nuevaRegion = False
        #Declaracion de variables e identificacion de tamaño de la ventana que se esta usando 
        if platform == "linux" or platform == "linux2":
            size = (None, None)
            args = ["xrandr", "-q", "-d", ":0"]
            proc = subprocess.Popen(args,stdout=subprocess.PIPE)
            for line in proc.stdout:
                if isinstance(line, bytes):
                    line = line.decode("utf-8")
                    if "Screen" in line:
                        size = (int(line.split()[7]),  int(line.split()[9][:-1]))
            self.anchowin, self.alturawin= size[0],size[1]
        elif platform == "darwin":
            pass # OS X
        elif platform == "win32":
            user32 = ctypes.windll.user32
            user32.SetProcessDPIAware()
            self.anchowin, self.alturawin = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        self.auxParent = parent
        self.recorteRegionD = recorteRegion(self)
        self.anchowin, self.alturawin = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        self.widthImg = round(85/100*self.anchowin)
        self.heightImg = round(85/100*self.alturawin)
        #Declaracion de eventos de los botones
        self.btnCortarRegion.clicked.connect(partial(self.cortarRegion,parent))
        self.comboRegion.activated.connect(self.seleccionarRegion)
        self.btnVerRegiones.clicked.connect(self.mostrarRegiones)
        self.btnGuardarTexto.clicked.connect(self.guardarTexto)
        self.btnEliminar.clicked.connect(self.eliminarRegion)

    def eliminarRegion(self):
        qm = QMessageBox
        ret = qm.question(self,'', "¿Estas seguro de eliminar esta region? Esta accion no se puede revetir", qm.Yes | qm.No)
        if ret == qm.Yes:
            indexRegion = self.comboRegion.currentIndex()
            self.comboRegion.removeItem(indexRegion)
            self.TicketAux.eliminarRegionByIndex(indexRegion)
            numRegiones= self.comboRegion.count()
            if (numRegiones==0):
                self.imagen_region.hide()
            elif (numRegiones>=1):
                coords = self.TicketAux.getCoordsRegionbyIndex(0)
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
                self.comboRegion.setCurrentIndex(0)
                self.imagen_ticketlabel.setPixmap(imgRegion)

    def closeEvent(self,evnt):
        self.auxParent.listaTickets[self.auxParent.indice][self.auxParent.indiceTicket] = self.TicketAux

    def guardarTexto(self):
        textoUsuario = self.txtUsuario.toPlainText()
        if textoUsuario == "":
            msg = QMessageBox()
            msg.setText("El texto no debe estar vacio")
            msg.setInformativeText('Introduzca un texto')
            msg.setWindowTitle("Error")
            msg.exec_()
        else:
            indexRegion = self.comboRegion.currentIndex()
            textoOCR = self.txtOCR.toPlainText()
            self.TicketAux.setTextOCRRegion(textoOCR,indexRegion)
            self.TicketAux.setTextoUsuarioRegion(textoUsuario,indexRegion)
            msg = QMessageBox()
            msg.setText("El texto se guardo correctamente")
            #msg.setInformativeText('Seleccione un ticket para procesar')
            msg.setWindowTitle("Exito!")
            msg.exec_()

    def mostrarRegiones(self):
        auxImagen = self.imagenTicket.copy()
        arrayRegionesCoords = self.TicketAux.getCoordsRegiones()
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
        self.recorteRegionD.cortarImagenbtn.hide()
        self.recorteRegionD.guardarbtn.hide()
        self.recorteRegionD.comboNuevasRegiones.hide()
        self.recorteRegionD.labelRegionMsg.hide()
        self.recorteRegionD.recorteLabel.hide()
        self.recorteRegionD.textLabel.show()
        self.recorteRegionD.continuarbtn.show()
        ##
        self.recorteRegionD.nombreTicket=text
        self.recorteRegionD.imagen = self.imagenTicket.copy()
        self.recorteRegionD.setModal(True)
        self.recorteRegionD.show()
    
    def seleccionarRegion(self):
        indexRegion = self.comboRegion.currentIndex()
        coords = self.TicketAux.getCoordsRegionbyIndex(indexRegion)
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
