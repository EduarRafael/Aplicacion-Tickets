#Importacion de numpy, opencv y otros
import sys
import cv2
import ctypes
import numpy as np
import subprocess
from sys import platform
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

class recorteRegion(QDialog):
    def __init__(self,parent):
        super(recorteRegion,self).__init__(parent)
        loadUi("msgRecorte.ui",self)
        self.imagen = None
        self.aux = None
        self.nombreTicket=""
        ##
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
        self.anchoImg = round(45/100*self.anchowin)
        self.alturaImg = round(45/100*self.alturawin)
        #
        self.recorteLabel.setMaximumWidth(self.anchoImg)
        self.recorteLabel.setMaximumHeight(self.alturaImg)
        self.continuarbtn.clicked.connect(self.cortarImagen)
        self.cortarImagenbtn.clicked.connect(self.cortarImagen)
        self.guardarbtn.clicked.connect(partial(self.gurdar,parent))
        self.comboNuevasRegiones.activated.connect(self.cambioRegion)

    #Evento para cerrar/guardar la imagen cortada
    def gurdar(self,parent):
        countRegiones = parent.comboRegion.count()
        cont=1
        for x in range(len(self.puntos)):
            nombreRegion = "Region_"+str(countRegiones+cont)+"_"+self.nombreTicket
            parent.TicketAux.nuevaRegion(nombreRegion,"","",self.puntos[x])
            parent.comboRegion.addItem(nombreRegion)
            cont+=1
        indice = countRegiones+cont-2
        parent.comboRegion.setCurrentIndex(indice)
        parent.nuevaRegion = True
        indexRegion = parent.comboRegion.currentIndex()
        coords = parent.TicketAux.getCoordsRegionbyIndex(indexRegion)
        auxImagen = parent.imagenTicket.copy()
        imgRegion = dibujarRegion(auxImagen,coords)
        imgRegionSola = recortarImagen(parent.imagenTicket,coords)
        texto = procesarTexto(parent.imagenTicket,coords)
        parent.txtOCR.setPlainText(texto)
        imgRegionSola = recortarImagen(parent.imagenTicket,coords)
        imgRegionSola = formatoPixMap(imgRegionSola)
        parent.imagen_region.setPixmap(imgRegionSola)
        imgRegion = formatoPixMap(imgRegion)
        imgW = round(37/100*parent.anchowin)
        imgH = round(78.7/100*parent.alturawin)
        imgRegion = imgRegion.scaled(imgW,imgH)
        parent.imagen_ticketlabel.setPixmap(imgRegion)
        self.close()     

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
            x1=int(rect[0])
            y1=int(rect[1])
            x2=int(rect[2])
            y2=int(rect[3])
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
            self.imagenPixMap = self.imagenPixMap.scaled(self.anchoImg,self.alturaImg)
            self.recorteLabel.setPixmap(self.imagenPixMap)
            self.recorteLabel.show()
            self.move(50,50)
            self.textLabel.hide()
        else:
            self.cortarImagenbtn.hide()
            self.guardarbtn.hide()
            self.comboNuevasRegiones.hide()
            self.labelRegionMsg.hide()
            self.textLabel.show()
            self.continuarbtn.show()
            msg = QMessageBox()
            msg.setText("Las regiones no se guardaron correctamente, porfavor seguir las instrucciones mostradas en pantalla")
            msg.setWindowTitle("Error")
            msg.exec_()