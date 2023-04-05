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

import io
import os
from google.cloud import vision
import cv2
from PIL import Image, ImageDraw, ImageFont

# Credenciales de conexión con Google Cloud
credential_path = "credentials.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

class InteligenciaArtificial:
    def __init__(self) -> None:
        self.isDog = False
    
    def recognize_objects(self,path):
        """Localize objects in the local image.
        Args:
        path: The path to the local file.
        Returns:
        An annotated PIL Image object.
        """
        client = vision.ImageAnnotatorClient()

        with open(path, 'rb') as image_file:
            content = image_file.read()
        image = vision.Image(content=content)

        objects = client.object_localization(
            image=image).localized_object_annotations

        # Abrir la imagen con OpenCV y obtener sus dimensiones
        img = cv2.imread(path)
        height, width, _ = img.shape

        # Dibujar las etiquetas de los objetos en la imagen
        pil_img = Image.fromarray(img)
        draw = ImageDraw.Draw(pil_img)
        font = ImageFont.truetype("arial.ttf", 20)
        for object_ in objects:
            name = object_.name
            score = object_.score
            x1 = int(object_.bounding_poly.normalized_vertices[0].x * width)
            y1 = int(object_.bounding_poly.normalized_vertices[0].y * height)
            x2 = int(object_.bounding_poly.normalized_vertices[2].x * width)
            y2 = int(object_.bounding_poly.normalized_vertices[2].y * height)
            draw.rectangle([x1, y1, x2, y2], outline='red', width=2)
            draw.text((x1, y1), f'{name} ({score:.2f})', font=font)

        # Devolver la imagen con las etiquetas
        return pil_img

    def localize_objects(self,image):
        """Localize objects in the PIL image.

        Args:
        image: The PIL Image object.

        Returns:
        An annotated PIL Image object.
        """
        client = vision.ImageAnnotatorClient()
        self.isDog = False
        # Convertir la imagen PIL a bytes
        with io.BytesIO() as output:
            image.save(output, format="JPEG")
            content = output.getvalue()

        # Crear un objeto vision.Image con los bytes de la imagen
        vision_image = vision.Image(content=content)

        objects = client.object_localization(
            image=vision_image).localized_object_annotations

        # Obtener las dimensiones de la imagen
        width, height = image.size

        # Dibujar las etiquetas de los objetos en la imagen
        draw = ImageDraw.Draw(image)
        font = ImageFont.truetype("arial.ttf", 20)
        for object_ in objects:
            name = object_.name
            score = object_.score
            x1 = int(object_.bounding_poly.normalized_vertices[0].x * width)
            y1 = int(object_.bounding_poly.normalized_vertices[0].y * height)
            x2 = int(object_.bounding_poly.normalized_vertices[2].x * width)
            y2 = int(object_.bounding_poly.normalized_vertices[2].y * height)
            draw.rectangle([x1, y1, x2, y2], outline='red', width=2)
            draw.text((x1, y1), f'{name} ({score:.2f})', font=font)
            if(object_.name=="Dog"):
                self.isDog = True

        # Devolver la imagen con las etiquetas
        self.saveImage(image,"images/x.jpg")
        return image, self.isDog

    
    def saveImage(self,image,output_path):
        image.save(output_path)