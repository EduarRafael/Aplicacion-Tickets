#Clase de objeto RegionTicket
class RegionTicket:
    #Inicializacion de la clase
    def __init__(self,nom,t1,t2,coords=[]):
        self.nombreRegion = nom
        self.puntos = coords
        self.textoUsuario = t1
        self.textoOcr = t2
    
    #Retorna el nombre de la region
    def getNombre(self):
        return self.nombreRegion

    #Retorna la lista con las coordenadas dentro del ticket
    def getPuntos(self):
        return self.puntos

    #Retorna el texto de la region del ticket
    def getTextoOCR(self):
        return self.textoOcr

    #Define el texto por el usuario 
    def setTextOCR(self,t):
        self.textoOcr = t

    def getTextoUsuario(self):
        return self.textoUsuario

    def setTextoUsuario(self,t):
        self.textoUsuario = t

#Clase de objeto ticket    
class Ticket:    
    #Inicializacion de la clase
    def __init__(self,nom,coords=[]):
        self.nombreTicket = nom
        self.fecha=""
        self.establecimiento = ""
        self.regiones = []
        self.puntos = coords

    #Define la fecha del ticket
    def setFecha(self,fecha):
        self.fecha= fecha
    
    #Define el nombre del establecimiento del ticket
    def setEstablecimiento(self,estab):
        self.establecimiento= estab

    #Define el texto del OCR
    def setTextOCRRegion(self,t,indice):
        self.regiones[indice].setTextOCR(t)

    #Define el texto por el usuario 
    def setTextoUsuarioRegion(self,t,indice):
        self.regiones[indice].setTextoUsuario(t)

    def eliminarRegionByIndex(self,indice):
        self.regiones.pop(indice)
        
    #Ingresa una nueva region en la lista de regiones del ticket
    def nuevaRegion(self,nom,t1,t2,coords=[]):
        regionN = RegionTicket(nom,t1,t2,coords)
        self.regiones.append(regionN)

    def getNomTicket(self):
        return self.nombreTicket
    
    #Retorna la fecha del ticket
    def getFecha(self):
        return self.fecha

    #Retorna el nombre del establecimiento del ticket
    def getEstablecimiento(self):
        return self.establecimiento
    
    #Retorna las coordenadas del ticket recortado en la imagen original
    def getCoords(self):
        return self.puntos

    def getTextRegion(self,index):
        return self.regiones[index].getTextoUsuario()
    
    def getTextRegionOCR(self,index):
        return self.regiones[index].getTextoOCR()

    #Retorna una region(Nombre de region y sus coordenadas) del ticket por id
    def getRegionbyIndex(self,index):
        return self.regiones[index].getNombre(), self.regiones[index].getPuntos()

    def getCoordsRegionbyIndex(self,index):
        return self.regiones[index].getPuntos()

    #Retorna las regiones en una lista(Para manipular las regiones de forma individual sin acceder al ticket)
    def getRegiones(self):
        listregiones = []
        for r in range(len(self.regiones)):
            listregiones.append(self.regiones[r])
        return listregiones

    #Retorna una lista con los nombres de las regiones de los tickets
    def getNombresRegiones(self):
        listnom = []
        for r in range(len(self.regiones)):
            listnom.append(self.regiones[r].getNombre())
        return listnom

    #Retorna una lista con las coordenadas de las regiones de los tickets
    def getCoordsRegiones(self):
        listcoords = []
        for r in range(len(self.regiones)):
            listcoords.append(self.regiones[r].getPuntos())
        return listcoords