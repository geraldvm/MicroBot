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

from PIL import Image
import cv2
import numpy as np

class ShapeDetector:
    def __init__(self):
        pass
    
    def detect_shapes(self, pil_image):
        # Convertir la imagen PIL en una imagen numpy
        np_image = np.array(pil_image)

        # Convertir BGR a escala de grises
        gray = cv2.cvtColor(np_image, cv2.COLOR_BGR2GRAY)

        # Aplicar Canny
        canny = cv2.Canny(gray, 10, 150)

        # Dilatar y erosionar la imagen
        canny = cv2.dilate(canny, None, iterations=1)
        canny = cv2.erode(canny, None, iterations=1)

        # Encontrar los contornos
        cnts, _ = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Inicializar la lista de formas encontradas
        shapes = []

        # Procesar cada contorno
        for c in cnts:
            # Aproximar el contorno a un polígono
            epsilon = 0.01 * cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, epsilon, True)

            # Obtener las dimensiones del rectángulo que encierra la forma
            x, y, w, h = cv2.boundingRect(approx)
            shape_type = ''
            # Verificar el número de vértices para determinar la forma
            if len(approx) == 3:
                shape_type = 'Triangulo'
            elif len(approx) == 4:
                aspect_ratio = float(w) / h
                if aspect_ratio == 1:
                    shape_type = 'Cuadrado'
                else:
                    shape_type = 'Rectangulo'
            elif len(approx) == 5:
                shape_type = 'Pentagono'
            """
            elif len(approx) == 6:
                shape_type = 'Hexagono'
            else:
                shape_type = 'Circulo'
            """
            # Dibujar el contorno y etiquetar la forma
            cv2.drawContours(np_image, [approx], 0, (0, 255, 0), 2)
            cv2.putText(np_image, shape_type, (x, y - 5), 1, 1.5, (0, 255, 0), 2)

            # Agregar la forma a la lista de formas encontradas
            #shapes.append((shape_type, x, y, w, h))
            shapes.append(shape_type)

        # Convertir la imagen numpy a PIL
        pil_image_result = Image.fromarray(np_image)

        # Retornar las formas encontradas y la imagen PIL
        return pil_image_result, shapes 


# Ejemplo
"""
# Cargar la imagen
pil_image = Image.open('a.jpg')

# Crear una instancia de ShapeDetector
sd = ShapeDetector()

# Detectar las formas en la imagen
pil_image_result, shapes = sd.detect_shapes(pil_image)

# Mostrar la imagen resultante
pil_image_result.show()

# Imprimir las formas encontradas
for shape in shapes:
    print(shape)
"""