"""
Copyright 2023 Gerald Valverde Mc kenzie | McKode Development

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

from tkinter import *
from tkinter import messagebox
import tkinter.scrolledtext as scrolledtext
import os
from playsound import playsound
from threading import Thread
import time
from PIL import Image, ImageTk
import requests
from InteligenciaArtificial import *
from ESP32Imagen import ESP32Imagen
from ShapeDetector import ShapeDetector


class RobotController:
    def __init__(self,direccion_ip_esp32):
        self.__ventana=None
        self.__espImg_x=220
        self.__espImg_y=310
        self.__cv= None
        self.__API= f"http://{direccion_ip_esp32}"
        self.IA = InteligenciaArtificial()
        self.ShapeIA = ShapeDetector()
        self.esp32_imagen = ESP32Imagen(direccion_ip_esp32)
        self.image_label = None
        self.image_value= None


    #***************Cargar Imagenes***********************
    #Entrada: Nombre de la imagen
    #Restricciones: el nombre de la imagen debe ser formato str
    #Salida: Genera la imagen
    def __loadImage(self,filename):
        path = os.path.join('images',filename)
        img = Image.open(path)
        imagen = ImageTk.PhotoImage(img)
        return imagen
    
    def __loadImageESPDef(self,filename):
        path = os.path.join('images',filename)
        img = Image.open(path).resize((450, 450))
        img = ImageTk.PhotoImage(img)
        return img
    
    def __loadImageESP(self):
        #path = os.path.join('images',filename)
        self.esp32_imagen.capturar_imagen()
        time.sleep(3)
        imagen = self.esp32_imagen.obtener_imagen()
        #img = Image.open(path)
        imagen = imagen.resize((450, 450))
        #imagen = ImageTk.PhotoImage(imagen)
        return imagen

    def send_command(self,command):
        response = requests.get(self.__API+'/'+command)
        print(command+": "+str(response))

    #Funcion principal
    def main(self):

        def update_image_thread():
            img, isDog = self.IA.localize_objects(self.__loadImageESP())
            img.resize((450, 450))
            if(isDog):
                self.send_command("led") 
                print("isDog")
            self.image_value= ImageTk.PhotoImage(image=img)#self.__loadImage("x.jpg")
            self.__cv.itemconfigure(self.image_label, image=self.image_value)
            print("Updated")

        def update_shape_thread():
            img, shapes = self.ShapeIA.detect_shapes(self.__loadImageESP())
            img.resize((450, 450))
            for shape in shapes:
                print(shape)
            if("Cuadrado" in shapes):
                self.send_command("led") 
                print("isSquare")
            self.image_value= ImageTk.PhotoImage(image=img)#self.__loadImage("x.jpg")
            self.__cv.itemconfigure(self.image_label, image=self.image_value)
            print("Updated")
            

        def send_command(command):
            response = requests.get(self.__API+'/'+command)
            print(response.content)

        def th_update():
            th_time=Thread(target=update_image_thread, args=())
            th_time.start()
        
        def th_shape():
            th_sh=Thread(target=update_shape_thread, args=())
            th_sh.start()
        
        #def th_shape():
            #th_time=Thread(target=update_shape_thread, args=())
            #th_time.start()


        
        window = Tk()
        window.title("MicroBot")
        window.minsize(800,535)
        window.resizable(width=NO, height=NO)
        window.configure(background="white")  
        self.__ventana = window
        self.__cv= Canvas(window, width= 2000, height = 2000, bg="white")

        #*********************NUEVA BARRA SUPERIOR***************************

        top_frame = Frame(window, bg='black', width=800, height=80)
        top_frame.pack(side=TOP, fill=X)

        logo = self.__loadImage("logo.jpg")
        logo_label = Label(top_frame, image=logo, bg='black')
        logo_label.pack(side=LEFT, padx=20)

        title_label = Label(top_frame, text='MicroBot', font=('Calibri', 30), fg='white', bg='black')
        title_label.pack(side=LEFT, padx=150)
        
        self.__cv.place(x=0,y=0)
        bg= self.__loadImage("bg.png")
        self.image_value= self.__loadImageESPDef("fig.png")
        self.__cv.create_image(0,0, anchor =  "nw", image = bg)  
        self.image_label=self.__cv.create_image(self.__espImg_x,self.__espImg_y, image = self.image_value, tags = "imgESP")

        #botonSTART = Button(window, text="START", command=hilo, bg="#096654",fg="white",font=("Helvetica",15)).place(x=400,y=20)
        figBtn = self.__loadImage("btnFig.png") #boton aceptar
        objBtn = self.__loadImage("btnObj.png") #boton aceptar
        botonConnect = Button(window,image=objBtn , command=th_update, borderwidth=0).place(x=550,y=200)
        botonShape = Button(window,image=figBtn , command=th_shape, borderwidth=0).place(x=550,y=280)

        #Move player
        def up(e):
            self.send_command("move_forward")

        def down(e):
            self.send_command("move_backward")

        def left(e):
            self.send_command("move_left")

        def right(e):
            self.send_command("move_right")
        
        def led_on(e):
            self.send_command("led")

        window.bind("<Up>", up)
        window.bind("<Down>", down)
        window.bind("<Left>", left)
        window.bind("<Right>", right)
        window.bind("<l>", led_on)
        window.mainloop()
        