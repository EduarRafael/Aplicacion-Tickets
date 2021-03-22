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

class recorteTicket(QDialog):
    def __init__(self,parent):
        super(recorteTicket,self).__init__(parent)
        loadUi("msgRecorte.ui",self)
        self.imagen = None
        self.aux = None
        self.nombreImagen=""
        self.indiceImagen = 0
        user32 = ctypes.windll.user32
        user32.SetProcessDPIAware()
        self.anchowin, self.alturawin = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        self.anchoImg = round(85/100*self.anchowin)
        self.alturaImg = round(85/100*self.alturawin)
        self.recorteLabel.setMaximumWidth(self.anchoImg)
        self.recorteLabel.setMaximumHeight(self.alturaImg)
        self.cortarImagenbtn.hide()
        self.guardarbtn.hide()
        self.continuarbtn.clicked.connect(self.cortarImagen)
        self.cortarImagenbtn.clicked.connect(self.cortarImagen)
        self.guardarbtn.clicked.connect(partial(self.gurdar,parent))

    #Evento para cerrar/guardar la imagen cortada
    def gurdar(self,parent):
        imgW = round(37/100*self.anchowin)
        imgH = round(68/100*self.alturawin)
        self.imagenPixMap = self.imagenPixMap.scaled(imgW,imgH)
        parent.img_ticket.setPixmap(self.imagenPixMap)
        self.recorteLabel.hide()
        parent.img_ticket.show()
        self.textLabel.show()
        listaux = []
        countTickets = parent.comboTicket.count()
        cont=1
        for x in range(len(self.puntos)):
            nombreTicket = "Ticket_"+str(countTickets+cont)+"_"+self.nombreImagen
            listaux.append(Ticket(nombreTicket,self.puntos[x]))
            parent.comboTicket.addItem(nombreTicket)
            cont+=1
        parent.listaTickets[self.indiceImagen] = listaux
        #print(parent.listaTickets[self.indiceImagen])
        indice= countTickets + cont -2
        parent.comboTicket.setCurrentIndex(indice)
        self.close()

    #Evento para cortar la imagen

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
        self.recorteLabel.hide()
        self.continuarbtn.hide()
        self.puntos=[]
        listaPuntos = []
        self.aux = self.imagen.copy()
        cv2.namedWindow("Imagen",cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Imagen",self.anchoImg,self.alturaImg)
        ROIs = cv2.selectROIs("Imagen",self.aux)
        cv2.destroyWindow("Imagen")
        for rect in ROIs:#Añade todos los recortes a la variable puntos
            x1=rect[0]
            y1=rect[1]
            x2=rect[2]
            y2=rect[3]
            listaPuntos = [[x1,y1],[(x2+x1),y1],[x1,(y1+y2)],[(x1+x2),(y1+y2)]]
            self.puntos.append(listaPuntos)
        #        
        for i in range (len(ROIs)):
            self.comboNuevasRegiones.addItem("Region "+str(i+1))
        if len(self.puntos)>=1:
            self.dst = recortarImagen(self.aux,self.puntos[0])
            self.cortarImagenbtn.show()
            self.guardarbtn.show()
            self.comboNuevasRegiones.show()
            self.labelRegionMsg.show()
            self.imagenPixMap = formatoPixMap(self.dst)
            imgW = round(37/100*self.anchowin)
            imgH = round(68/100*self.alturawin)
            self.imagenPixMap = self.imagenPixMap.scaled(imgW,imgH)
            self.recorteLabel.setPixmap(self.imagenPixMap)
            self.recorteLabel.show()
            self.move(50,50)
            self.textLabel.hide()
        else:
            msg = QMessageBox()
            msg.setText("Las regiones no se guardaron correctamente, porfavor seguir las instrucciones mostradas en pantalla")
            msg.setWindowTitle("Error")
            msg.exec_()
            self.continuarbtn.show()
