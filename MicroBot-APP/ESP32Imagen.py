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

from io import BytesIO
import time
import requests
from PIL import Image

class ESP32Imagen:
    def __init__(self, direccion_ip_esp32):
        self.url_esp32 = f"http://{direccion_ip_esp32}"

    def capturar_imagen(self):
        # Hacer la solicitud HTTP al ESP32
        print("Capturing...")
        response = requests.get(self.url_esp32 + '/capture')
            
    def obtener_imagen(self):
        # Hacer la solicitud HTTP al ESP32
        time.sleep(1)
        print("Getting...")
        response = requests.get(self.url_esp32 + '/picture')
        
        # Si la solicitud fue exitosa (código 200)
        if response.status_code == 200:
            # Obtener la imagen de la respuesta
            imagen_bytes = response.content
            # Cargar la imagen usando Pillow
            imagen = Image.open(BytesIO(imagen_bytes))
            
            return imagen
        else:
            print('Error al obtener la imagen:', response.status_code)
            return None
    
    def guardar_imagen(self, imagen, ruta_imagen):
        # Guardar la imagen en el disco
        imagen.save(ruta_imagen)

# Ejemplo de uso
"""
direccion_ip_esp32 = "192.168.100.2"
esp32_imagen = ESP32Imagen(direccion_ip_esp32)
esp32_imagen.capturar_imagen()
time.sleep(3)
imagen = esp32_imagen.obtener_imagen()
esp32_imagen.guardar_imagen(imagen, 'images/t.jpg')
"""