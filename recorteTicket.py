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
        self.nombreTicket=""
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
        if len(parent.listaTickets[self.indiceImagen])==0:
            listaux.append(Ticket(self.nombreTicket,self.puntos))
            parent.listaTickets[self.indiceImagen] = listaux
            #print(parent.listaTickets[self.indiceImagen])
        else:
            listaux = parent.listaTickets[self.indiceImagen]
            listaux.append(Ticket(self.nombreTicket,self.puntos))
            parent.listaTickets[self.indiceImagen] = listaux
            #print(parent.listaTickets[self.indiceImagen])
        parent.comboTicket.addItem(self.nombreTicket)
        parent.comboTicket.setCurrentIndex(parent.contImg-1)
        self.close()

    #Evento para cortar la imagen
    def cortarImagen(self):
        self.continuarbtn.hide()
        self.puntos=[]
        self.aux = self.imagen.copy()
        cv2.namedWindow("Imagen",cv2.WINDOW_NORMAL)
        cv2.setMouseCallback("Imagen",self.clics)
        cv2.resizeWindow("Imagen",self.anchoImg,self.alturaImg)
        cv2.imshow("Imagen",self.aux)
    

    #Evento de mouse de opencv para cortar la imagen
    def clics(self,event,x,y,falgs,param):
        if event == cv2.EVENT_LBUTTONDOWN:
            cv2.circle(self.aux,(x,y),25,(0,255,0),8)
            self.puntos.append([x,y])
            cv2.imshow("Imagen",self.aux) 
        if len(self.puntos) ==4:
            self.dst = recortarImagen(self.imagen,self.puntos)
            cv2.destroyWindow("Imagen")
            self.cortarImagenbtn.show()
            self.guardarbtn.show()
            self.imagenPixMap = formatoPixMap(self.dst)
            self.imagenPixMap = self.imagenPixMap.scaled(self.anchoImg,self.alturaImg)
            self.recorteLabel.setPixmap(self.imagenPixMap)
            self.recorteLabel.show()
            self.move(50,50)
            self.textLabel.hide()
