#Importacion de numpy, opencv y otros
import sys
import cv2
import numpy as np
import os
import ctypes
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
#Importacion de vistas
from recorteTicket import *
from vistaTicket import *


class  mainWindow(QDialog):
    def __init__(self,parent=None):
        super(mainWindow,self).__init__(parent)
        loadUi("vistaPrincipal.ui",self)#Craga del UI
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
        self.anchoImg = round(85/100*self.anchowin)
        self.alturaImg = round(85/100*self.alturawin)
        self.contRegiones=0
        self.imagenSeleccionada = False
        #Declaracion de objetos de las vistas
        self.recorteTicketD = recorteTicket(self)#Objeto para dialogo del recorte del ticket  
        self.vistaTicketD = vistaTicket(self)
        #Declaracion de eventos de los botones/widgets
        self.botonAbrir.clicked.connect(self.abirRepo)#Evento para el botonAbrir
        self.listImagenes.clicked.connect(self.selectImg)#Evento para listWidget
        self.listImagenes.activated.connect(self.selectImg)#Evento para listWidget
        self.recortarTicket.clicked.connect(self.recortarTDialog)
        self.btnvistaTicket.clicked.connect(self.vistaTicketDialog)
        self.btnEliminarTicket.clicked.connect(self.eliminarTicket)
        self.comboTicket.activated.connect(self.cambioTicket)
        
    
    #Funcion para cuando el usuario quiera salir del programa    
    def closeEvent(self, event):
        #Se tiene comentado el autoguardado por pruebas y cambios en el codigo relacionados a la lista que se utlizaba para los objetos
        pass
        #print(self.dicImagenes)
        #print("  ")
        #print(self.listaTickets)
        #guardarJson(self.listaTickets,self.dicImagenes)
        #Agregar la parte para guardar el archivo
    
    #Funcion para abir el repositorio 
    def abirRepo(self):
        self.directorio = str(QFileDialog.getExistingDirectory(self,"Select Directory"))#Abre el explorador de archivos solo mostrando carpetas y toma la ruta de la carpeta
        if self.directorio == "":#If para verificar que selecciona una carpeta
            #Inicializa y muestra el mensaje de error
            msg = QMessageBox()
            #msg.setIcon(QMessageBox.Critical)
            msg.setText("Error al abrir carpeta")
            msg.setInformativeText('Seleccione una carpeta')
            msg.setWindowTitle("Error")
            msg.exec_()
            self.listImagenes.clear()
        else:#En dado caso de abrir la carpeta se ejecuta el siguiente codigo
            self.listImagenes.clear()#Limpa el widgetList para los objetos entrantes
            archivos = os.listdir(self.directorio)#Hace una lista de los archivos dentro de la ruta que se tomo anteriormente
            self.dicImagenes = {}
            self.dicImagenes["Imagenes"]=[]
            self.dicImagen = {}
            self.listaTickets = [[]] * len(archivos)
            #print(len(self.listaTickets))
            cont=0
            for i in range (len(archivos)):#Ciclo para revisar todos los archivos de la carpeta abierta
                if archivos[i].endswith(".png") or archivos[i].endswith(".jpg") or archivos[i].endswith(".jpeg"):
                    self.listImagenes.addItem(str(archivos[i]))#Enlista solo los archivos que sean tipo imagen(Terminaciones png, jpg, jpeg)
                    self.dicImagen["Imagen_"+str(cont)]=[]
                    self.dicImagen["Imagen_"+str(cont)].append({"NombreImagen":archivos[i]})
                    cont=cont+1
            self.dicImagenes["Imagenes"]=self.dicImagen
            self.dicImagenes["Dir"]={"NomCarpeta":self.directorio}
            #print(self.dicImagenes)
            #with open('data.json', 'w') as file:
                #json.dump(self.dicImagenes, file, indent=2)
            #print(self.dicImagenes)
    
    #Funcion del listWidget para seleccionar la imagen
    def selectImg(self):
        self.nombreImagen = self.listImagenes.currentItem().text()#Toma el texto del item seleccionado
        ruta =self.directorio+"/"+self.nombreImagen
        #Se abre la imagen seleccionada mediante cv2
        self.imagencv2 = cv2.imread(ruta)
        self.indice = self.listImagenes.currentRow()
        self.imagenSeleccionada = True
        #print(len(self.listaTickets[self.indice]))
        if(len(self.listaTickets[self.indice])==0):
            self.img_ticket.hide()
            self.comboTicket.clear()            
        else:
            self.comboTicket.clear()
            i = len(self.listaTickets[self.indice])
            for x in range(i):
                self.comboTicket.addItem(self.listaTickets[self.indice][x].getNomTicket())
            self.comboTicket.setCurrentIndex(0)
            img = recortarImagen(self.imagencv2,self.listaTickets[self.indice][0].getCoords())
            img = formatoPixMap(img)
            imgW = round(37/100*self.anchowin)
            imgH = round(68/100*self.alturawin)
            img = img.scaled(imgW,imgH)
            self.img_ticket.show()
            self.img_ticket.setPixmap(img)
        imagen = QtGui.QPixmap(ruta)#Se abre la imagen en un objeto QPixmap
        imgW = round(42/100*self.anchowin)
        imgH = round(80/100*self.alturawin)
        imagen = imagen.scaled(imgW,imgH)#Se escala la imagen al tamaño predeterminado del label
        self.imagen_1.setPixmap(imagen)#Se añade la imagen al label

    def cambioTicket(self):
        self.indiceTicket = self.comboTicket.currentIndex()
        img = recortarImagen(self.imagencv2,self.listaTickets[self.indice][self.indiceTicket].getCoords())
        img = formatoPixMap(img)
        imgW = round(37/100*self.anchowin)
        imgH = round(67.59/100*self.alturawin)
        img = img.scaled(imgW,imgH)
        self.img_ticket.setPixmap(img)

    def eliminarTicket(self):
        numTickets= self.comboTicket.count()
        if(numTickets>=1):
            qm = QMessageBox
            ret = qm.question(self,'', "¿Estas seguro de eliminar este ticket? Esta accion no se puede revertir", qm.Yes | qm.No)
            if ret == qm.Yes:
                self.indiceTicket = self.comboTicket.currentIndex()
                self.comboTicket.removeItem(self.indiceTicket)
                self.listaTickets[self.indice].pop(self.indiceTicket)
                numTickets= self.comboTicket.count()
                if (numTickets==0):
                    self.img_ticket.hide()
                elif (numTickets>=1):
                    img = recortarImagen(self.imagencv2,self.listaTickets[self.indice][0].getCoords())
                    img = formatoPixMap(img)
                    imgW = round(37/100*self.anchowin)
                    imgH = round(67.59/100*self.alturawin)
                    img = img.scaled(imgW,imgH)
                    self.comboTicket.setCurrentIndex(0)
                    self.img_ticket.setPixmap(img)
        elif(numTickets==0):
            msg = QMessageBox()
            #msg.setIcon(QMessageBox.Critical)
            msg.setText("Error al eliminar ticket")
            msg.setInformativeText('Seleccione un ticket para eliminar')
            msg.setWindowTitle("Error")
            msg.exec_() 

    def recortarTDialog(self):
        if(self.imagenSeleccionada == False):
            msg = QMessageBox()
            #msg.setIcon(QMessageBox.Critical)
            msg.setText("Error, seleccione una imagen")
            #msg.setInformativeText('Seleccione un imagen')
            msg.setWindowTitle("Error")
            msg.exec_() 
        elif(self.imagenSeleccionada == True):
            self.recorteTicketD.cortarImagenbtn.hide()
            self.recorteTicketD.guardarbtn.hide()
            self.recorteTicketD.comboNuevasRegiones.hide()
            self.recorteTicketD.labelRegionMsg.hide()
            self.recorteTicketD.continuarbtn.show()
            #
            imgW = round(39/100*self.anchowin)
            imgH = round(32/100*self.alturawin)
            self.recorteTicketD.resize(imgW,imgH)
            self.recorteTicketD.move(round(self.anchowin/3),round(self.alturawin/3))
            self.recorteTicketD.setModal(True)
            #
            self.recorteTicketD.imagen = self.imagencv2
            self.recorteTicketD.indiceImagen= self.indice
            self.recorteTicketD.nombreImagen= self.nombreImagen
            #
            self.recorteTicketD.show()


    def vistaTicketDialog(self):
        numTickets= self.comboTicket.count()
        if(numTickets>=1):
            self.indiceTicket = self.comboTicket.currentIndex()
            self.vistaTicketD.comboRegion.clear()
            #print(self.listaTickets[self.indice][indiceTicket].getCoords())
            imgTicket = recortarImagen(self.imagencv2,self.listaTickets[self.indice][self.indiceTicket].getCoords())
            imgTicketAux = imgTicket.copy()
            regiones = self.listaTickets[self.indice][self.indiceTicket].getRegiones()
            if len(regiones)==0:
                arrayRegionesCoords, imgTicketRegiones = cortarRegiones(imgTicket)#Se procesa el ticket para encontrar las posibles regiones con texto
                nomticket = self.listaTickets[self.indice][self.indiceTicket].getNomTicket()#Se toma el nombre del ticket seleccionado
                for x in range(len(arrayRegionesCoords[0])):
                    nombreRegion = "Region_"+str(x+1)+"_"+nomticket#Nombre del ticket
                    #Se crean las regiones en base a las coordenadas calculadas
                    self.listaTickets[self.indice][self.indiceTicket].nuevaRegion(nombreRegion,arrayRegionesCoords[0][x])
                    #Se añade el nombre de las regiones al comboBox
                    self.vistaTicketD.comboRegion.addItem(nombreRegion)  
            elif len(regiones)>1:
                arrayRegionesCoords = self.listaTickets[self.indice][self.indiceTicket].getCoordsRegiones()#Obtiene las coordenadas de las regiones
                arrayNombresRegiones = self.listaTickets[self.indice][self.indiceTicket].getNombresRegiones()#Obtiene los nombres de las regiones
                imgTicketRegiones = dibujarRegiones(imgTicketAux,arrayRegionesCoords)
                for x in range(len(arrayNombresRegiones)):
                    self.vistaTicketD.comboRegion.addItem(arrayNombresRegiones[x])
            self.vistaTicketD.setModal(True)
            self.vistaTicketD.imagenTicket = imgTicket
            imgLabel = formatoPixMap(imgTicketRegiones)
            imgW = round(37/100*self.anchowin)
            imgH = round(78.7/100*self.alturawin)
            imgLabel = imgLabel.scaled(imgW,imgH)
            self.vistaTicketD.imagen_ticketlabel.setPixmap(imgLabel)
            self.vistaTicketD.TicketAux = self.listaTickets[self.indice][self.indiceTicket]
            self.vistaTicketD.show()
        elif(numTickets==0):
            msg = QMessageBox()
            #msg.setIcon(QMessageBox.Critical)
            msg.setText("Error al abrir ticket")
            msg.setInformativeText('Seleccione un ticket para procesar')
            msg.setWindowTitle("Error")
            msg.exec_()       
        

app=QApplication(sys.argv)
mainwindow=mainWindow()
#widget=QtWidgets.QStackedWidget()
#widget.addWidget(mainwindow)
mainwindow.showMaximized()
mainwindow.show()
sys.exit(app.exec_())