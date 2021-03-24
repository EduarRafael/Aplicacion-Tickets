import cv2
import numpy as np
import math
import os
import pytesseract
import json
from ClasesTicket import * 
from PyQt5 import QtGui
from PyQt5.QtGui import QImage
from cv2 import boundingRect, countNonZero, cvtColor, drawContours, findContours, getStructuringElement, imread, morphologyEx, pyrDown, rectangle, threshold
pytesseract.pytesseract.tesseract_cmd = r'D:\Program Files\Tesseract-OCR\tesseract'

def calcularDistancias(puntos=[]):
    cuadrado1= (puntos[1][0]-puntos[0][0])**2
    cuadrado2= (puntos[1][1]-puntos[0][1])**2
    d1 = math.sqrt(cuadrado1+cuadrado2)
    cuadrado1= (puntos[3][0]-puntos[2][0])**2
    cuadrado2= (puntos[3][1]-puntos[2][1])**2
    d2 = math.sqrt(cuadrado1+cuadrado2)
    if(d1>d2):
        ancho = round(d1)
    elif(d2>d1):
        ancho = round(d2)
    elif(d1==d2):
        ancho = round(d2)
    cuadrado1= (puntos[2][0]-puntos[0][0])**2
    cuadrado2= (puntos[2][1]-puntos[0][1])**2
    d3 = math.sqrt(cuadrado1+cuadrado2)
    cuadrado1= (puntos[3][0]-puntos[1][0])**2
    cuadrado2= (puntos[3][1]-puntos[1][1])**2
    d4 = math.sqrt(cuadrado1+cuadrado2)
    if(d3>d4):
        alto = round(d3)
    elif(d4>d3):
        alto = round(d4)
    elif(d3==d4):
        alto = round(d4)
    #print(ancho,alto)
    return ancho,alto

def recortarImagen(imagen,puntos=[]):
    #print(puntos)
    sizeimg = calcularDistancias(puntos)
    pts1= np.float32([puntos])
    pts2 = np.float32([[0,0],[sizeimg[0],0],[0,sizeimg[1]],[sizeimg[0],sizeimg[1]]])
    #pts2 = np.float32([[0,0],[480,0],[0,300],[480,300]])
    M = cv2.getPerspectiveTransform(pts1,pts2)
    imgRecortada = cv2.warpPerspective(imagen,M,(sizeimg[0],sizeimg[1]))
    #imgRecortada = cv2.warpPerspective(imagen,M,(480,300))
    return imgRecortada

def formatoPixMap(imagen):
    size = imagen.shape
    step = imagen.size /size[0]
    qformat = QImage.Format_Indexed8
    if len(size) == 3:
        if size[2] == 4:
            qformat = QImage.Format_RGBA8888
        else:
            qformat = QImage.Format_RGB888
    imgPixMap = QImage(imagen,size[1], size[0], step, qformat)
    imgPixMap = imgPixMap.rgbSwapped()
    imgPixMap = QtGui.QPixmap(imgPixMap)
    return imgPixMap

def takeY(elem):
    return elem[0][1]

def cortarRegiones(imagen):
    large = imagen
    rgb = cv2.pyrDown(large)

    small = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)

    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    grad = cv2.morphologyEx(small, cv2.MORPH_GRADIENT, kernel)

    _, bw = cv2.threshold(grad, 0.0, 255.0, cv2.THRESH_BINARY | cv2.THRESH_OTSU)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (9, 1))
    connected = cv2.morphologyEx(bw, cv2.MORPH_CLOSE, kernel)
    # using RETR_EXTERNAL instead of RETR_CCOMP
    contours, hierarchy = cv2.findContours(connected.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    #For opencv 3+ comment the previous line and uncomment the following line
    #_, contours, hierarchy = cv2.findContours(connected.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    mask = np.zeros(bw.shape, dtype=np.uint8)

    arrayaux= []
    arrayRegionesCoord=[]
    for idx in range(len(contours)):
        #print(contours)
        x, y, w, h = cv2.boundingRect(contours[idx])
        mask[y:y+h, x:x+w] = 0
        cv2.drawContours(mask, contours, idx, (255, 255, 255), -1)
        r = float(cv2.countNonZero(mask[y:y+h, x:x+w])) / (w * h)
        if r > 0.45 and w > 8 and h > 8:
            #cv2.rectangle(large, (x*2, y*2), ((x+w-1)*2, (y+h-1)*2), (0, 255, 0), 2)
            cv2.rectangle(rgb, (x, y), ((x+w-1), (y+h-1)), (0, 255, 0), 2)
            aux = [[x*2, y*2],[(x+w-1)*2,y*2],[x*2,(y+h-1)*2],[(x+w-1)*2,(y+h-1)*2]]
            arrayaux.append(aux)
    arrayRegionesCoord.append(arrayaux)
    arrayRegionesCoord[0].sort(key=takeY)
    return arrayRegionesCoord, rgb#Retorna un array con las coordenadas de las regiones econtradas
    #y una imagen con las regiones dibujadas

def procesarTexto(imagen,coords=[]):
    img = recortarImagen(imagen,coords)
    img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    img = cv2.threshold(img,0,255,cv2.THRESH_BINARY+ cv2.THRESH_OTSU)[1]
    img = cv2.medianBlur(img, 5)
    texto = pytesseract.image_to_string(img)
    return texto

def dibujarRegion(img,coords=[]):
    cv2.rectangle(img,(coords[0][0],coords[0][1]),(coords[3][0],coords[3][1]),(0,255,0),2)
    return img

def dibujarRegiones(img,coords=[]):
    for x in range(len(coords)):
        cv2.rectangle(img,(coords[x][0][0],coords[x][0][1]),(coords[x][3][0],coords[x][3][1]),(0,255,0),2)
    return img

def guardarJson(listaTickets,dicImagenes):
    for x in range(len(listaTickets)):
        if len(listaTickets[x])==0:
            pass
        else:
            dicTicket = {}
            dicTicket["Ticket"] = []#Se crea un diccionario que contega la lista de ticketes y sus regiones(En dado caso de tenerlas)
            aux = len(listaTickets[x])#La longitud de este array nos dice si existe más de 1 ticket en la imagen/En caso de fallar, se sabe que solo se recorto un ticket en
            #la imagen
            for j in range(aux):
                nombreticket = listaTickets[x][j].getNomTicket()#Se toma el nombre y coordenadas del ticket
                coordsTicket = listaTickets[x][j].getCoords()
                regiones = listaTickets[x][j].getRegiones()#Se llama la funcion getRegiones para saber si este ticket tiene regiones identificadas por la aplicacion o no
                if len(regiones)==0:#En dado caso de no tener regiones pasa al siguiente ticket
                    dicTicket["Ticket"].append({"Nomticket":nombreticket,"CoordsTicket":coordsTicket})
                elif len(regiones)>=1:#En dado caso de tener regiones se agregan los nombres y coorenadas de la region correspondiente
                    dicregion = []#Se crea una lista para las regiones
                    arrayRegionesCoords = listaTickets[x][j].getCoordsRegiones()
                    arrayNombresRegiones = listaTickets[x][j].getNombresRegiones()
                    for i in range(len(arrayNombresRegiones)):
                        dicregion.append({"NomRegion":arrayNombresRegiones[i],"CoordsRegion":arrayRegionesCoords[i]})
                    dicTicket["Ticket"].append({"Nomticket":nombreticket,"CoordsTicket":coordsTicket,"Regiones":dicregion})#Se agregan las regiones al ticket
            #print(dicTicket)
            dicImagenes["Imagenes"]["Imagen_"+str(x)].append(dicTicket)#Se agrega el ticket y sus correspondientes regiones a la imagen correspondiente
    #print(dicImagenes)
    with open('data.json', 'w') as file:#El archivo se guarda con el nombre data.json
        json.dump(dicImagenes, file, indent=2)#Se le pasa el diccionario con las imagenes, con sus correspondientes ticketes y las correspondientes regiones por ticket

def cargarArchivo():
    with open("data.json") as contenido:
        jdata = json.load(contenido)
        carpeta = jdata["Dir"]["NomCarpeta"]
        if os.path.isdir(carpeta):
            dicImagenes = {}
            dicImagenes["Dir"]={"NomCarpeta":carpeta}
            dicImagenes["Imagenes"]=[]
            dicImagen = {}
            listaTickets = [[]] * len(jdata["Imagenes"])
            for x in range (len(jdata["Imagenes"])):
                imgNom = jdata["Imagenes"]["Imagen_"+str(x)][0]["NombreImagen"]
                if os.path.isfile(carpeta+"/"+imgNom):
                    dicImagen["Imagen_"+str(x)]=[]
                    dicImagen["Imagen_"+str(x)].append({"NombreImagen":imgNom})
                    #print("Existe")
                else:
                    print("No existe la imagen ",imgNom)

                if len(jdata["Imagenes"]["Imagen_"+str(x)])>1:#Sí entra a este if significa que la imagen tiene tickets recortados
                    #print(len(jdata["Imagenes"]["Imagen_"+str(x)]))
                    for i in range (1,len(jdata["Imagenes"]["Imagen_"+str(x)])):
                        listaux = []
                        for j in range (len(jdata["Imagenes"]["Imagen_"+str(x)][i]["Ticket"])):
                            nomTicket = jdata["Imagenes"]["Imagen_"+str(x)][i]["Ticket"][j]["Nomticket"]
                            coordsTicket = jdata["Imagenes"]["Imagen_"+str(x)][i]["Ticket"][j]["CoordsTicket"]
                            ticket = Ticket(nomTicket,coordsTicket)
                            if len(jdata["Imagenes"]["Imagen_"+str(x)][i]["Ticket"][j])>2:#Sí entra a este if significa que el ticket tiene regiones encontradas
                                for k in range(len(jdata["Imagenes"]["Imagen_"+str(x)][i]["Ticket"][j]["Regiones"])):
                                    nomRegion= jdata["Imagenes"]["Imagen_"+str(x)][i]["Ticket"][j]["Regiones"][k]["NomRegion"]
                                    coordsRegionRegion= jdata["Imagenes"]["Imagen_"+str(x)][i]["Ticket"][j]["Regiones"][k]["CoordsRegion"]
                                    ticket.nuevaRegion(nomRegion,coordsRegionRegion)
                            else:
                                pass
                            listaux.append(ticket)#Se añade el ticket a la listaaux
                        listaTickets[x] = listaux#Se asigna la lista de tickets a la imagen correspondiente
            dicImagenes["Imagenes"] = dicImagen#Se añanden las imagenes encontradas al dicImagenes para que se cargen en la vistaP
            return dicImagenes, listaTickets
        else:
            return False   
        