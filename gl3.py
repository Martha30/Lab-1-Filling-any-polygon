#Universidad del Valle de Guatemala
#Laurelinda Gómez 19501
#Ejercicio 1
#26/07/2021

import struct
from collections import namedtuple


V2 = namedtuple('Vertex2', ['x', 'y'])
#V3 = namedtuple('Vertex3', ['x', 'y', 'z'])


def char(c):
    # 1 byte
    return struct.pack('=c', c.encode('ascii'))

def word(w):
    #2 bytes
    return struct.pack('=h', w)

def dword(d):
    # 4 bytes
    return struct.pack('=l', d)

# Guarda color
def color(r, g, b):
    # Acepta valores de 0 a 1
    return bytes([b, g, r])

# Variables globales

#BLACK = color(0,0,0)
#WHITE = color(1,1,1)


class Renderer(object):
    #Constructor
    def __init__(self, width, height):
        
        self.height = height
        self.width = width
        self.framebuffer = []
        self.clear_color = color(255, 255, 255)
        self.vertex_color = color(0, 0, 0)
        self.glClear()

    def glCreateWindow(self, width, height):
        self.width = width
        self.height = height
        self.glClear()
        self.glViewport(0,0, width, height)

    # Crea el viewport
    def glViewport(self, x, y, width, height):
        self.viewportX = int(x)
        self.viewportY = int(y)
        self.viewportWidth = int(width)
        self.viewportHeight = int(height)

    # color fondo
    def glClearColor(self, r, g, b):
        self.clear_color = color(r, g, b)

    def glClear(self):
        self.framebuffer = [
            [self.clear_color for x in range(self.width)]
            for y in range(self.height)
        ]

    
    # Color 
    def glColor(self, r, g, b):
        self.curr_color = color(r,g,b)

    # Dibujar un punto
    def glPoint(self, x, y, color ): 
        x = int(round((x+1) * self.width / 2))
        y = int(round((y+1) * self.height / 2))
        try:
                self.framebuffer[y][x] = color
        except IndexError:
                print("\nerror\n")

            
    def glPoint2(self, x, y, color = None): 
        x = int( (x + 1) * (self.viewportWidth / 2) + self.viewportX )
        y = int( (y + 1) * (self.viewportHeight / 2) + self.viewportY)
        if x < self.viewportX or x >= self.viewportX + self.viewportWidth or y < self.viewportY or y >= self.viewportY + self.viewportHeight:
            return
        if (0 <= x < self.width) and (0 <= y < self.height):
            self.framebuffer[int(x)][int(y)] = color or self.curr_color

#Basado en lo que se realizó en clase
    def glLine(self, v0, v1, color = None):
        x0 = v0.x
        x1 = v1.x
        y0 = v0.y
        y1 = v1.y
        if x0 == x1 and y0 == y1:
            self.glPoint(x0,y1,color)
            return

        # Pendiente
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)
        steep = dy > dx 
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0
        dx = abs(x1 - x0)
        dy = abs(y1 - y0)

        offset = 0
        limit = 0.5

        m = dy/dx
        y = y0
        
        for x in range(x0, x1 + 1):
            if steep:
                self.glPoint(y, x, color)
            else:
                self.glPoint(x, y, color)

            
            offset += m
            if offset >= limit:
                
                y += 1 if y0 < y1 else -1
                limit += 1

    


    #Se tomo de ejemplo lo realizado en clase
    def glLoadModel(self, filename, translate = V2(0.0,0.0), scale = V2(1.0,1.0)):
        
        model = Obj(filename)

        for face in model.faces:
            
            vertCount = len(face)

            for v in range(vertCount):
                
                index0 = face[v][0] - 1 
                index1 = face[(v + 1) % vertCount][0] - 1

                vert0 = model.vertices[index0]
                vert1 = model.vertices[index1]

                x0 = round(vert0[0] * scale.x + translate.x)
                y0 = round(vert0[1] * scale.y + translate.y)
                x1 = round(vert1[0] * scale.x + translate.x)
                y1 = round(vert1[1] * scale.y + translate.y)

                self.glLine(V2(x0,y0), V2(x1, y1))

    

    # Creación del Bitmap
    def glFinish(self, filename):
        # archivo BMP 
        with open(filename, "wb") as file:
            # Header
            file.write(bytes('B'.encode('ascii')))
            file.write(bytes('M'.encode('ascii')))
            # Por cada pixel se tienen 3 Bytes
            file.write(dword(14 + 40 + (self.width * self.height * 3)))
            file.write(dword(0))
            file.write(dword(14 + 40))

            # InfoHeader
            file.write(dword(40))
            file.write(dword(self.width))
            file.write(dword(self.height))
            file.write(word(1))
            file.write(word(24))
            file.write(dword(0))
            file.write(dword(self.width * self.height * 3))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))

            # Color Table
            for y in range(self.height):
                for x in range(self.width):
                    file.write(self.framebuffer[y][x])
    
    #Relleno de los polígonos
    def glFill(self, polygon):
        for y in range(self.height):
            for x in range(self.width):
                i = 0
                j = len(polygon) - 1
                d = False
                
                for i in range(len(polygon)):
                    if (polygon[i][1] < y and polygon[j][1] >= y) or (polygon[j][1] < y and polygon[i][1] >= y):
                        if polygon[i][0] + (y - polygon[i][1]) / (polygon[j][1] - polygon[i][1]) * (polygon[j][0] - polygon[i][0]) < x:
                            d = not d
                    j = i
                if d:
                    self.glPoint((float(x)/(float(self.width)/2))-1,(float(y)/(float(self.height)/2))-1,self.vertex_color)


# Dimensiones
width = 800
height = 740

# Instancia del renderer
r = Renderer(width, height)


#polígonos 1,2,3,45,5
polygono1= ((165, 380), (185, 360), (180, 330), (207, 345), (233, 330), (230, 360), (250, 380), (220, 385), (205, 410), (193, 383))
r.glFill(polygono1)

polygono2 = ((321, 335), (288, 286) ,(339, 251), (374, 302))
r.glFill(polygono2)

polygono3 = ((377, 249) ,(411, 197) ,(436, 249))
r.glFill(polygono3)

polygono4 = ((413, 177) ,(448, 159), (502, 88), (553, 53) ,(535, 36) ,(676, 37) ,(660, 52),(750, 145) ,(761, 179) ,(672, 192) ,(659, 214) ,(615, 214), (632, 230), (580, 230),(597, 215) ,(552, 214) ,(517, 144) ,(466, 180))
r.glFill(polygono4)

polygono5 = ((682, 175), (708, 120), (735, 148) ,(739, 170))
r.glFill(polygono5)

r.glFinish("polygon.bmp")




                    