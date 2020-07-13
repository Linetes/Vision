# Proyecto Integrador 2
Proyecto para la materia de visión computacional
## Integrantes del equipo
Juan Pablo Ramos Sanabria, 
Diego Alberto Alvarez Rodríguez, 
César Francisco Barraza Aguilar, 
César Buenfil Vázquez y 
Lisset Botello Santiago.

## Uso

### Dependencias
Selenium\n
```pip install selenium```
urllib.request
```pip install pycopy-urllib.request```
CV2
```pip install opencv-python```
numpy
```pip install numpy```
random
```pip install random2```
concurrent.futures
```pip install futures```
multiprocessing
```pip install multiprocess```
Web Driver
https://selenium-python.readthedocs.io/installation.html#downloading-python-bindings-for-selenium

### Correr
```python main.py```
Programa preguntará, "What are you looking for?"
Responder con la palabra del objeto que desea.

## Planteamiento del problema 
Usar la técnica de web data scraping para recopilar imágenes de una base de datos en línea. 
La base de datos que usaremos es ImageNet: http://image-net.org/about-overview

 <p align="center">
  <img src="https://github.com/Linetes/Vision/blob/master/web.JPG">
</p>

El programa debe solicitar un término de búsqueda al usuario, una vez ingresado el programa accesa a ImageNet y efectúa una consulta por ese término. El programa descarga las imágenes que arrojó la base de datos, el 80% de las imágenes deben ser guardadas en una carpeta llamada ./train/<término_de_búsqueda>, el 20% restante deben ser guardadas en una carpeta ./test/<término_de_búsqueda>.

## Explicación del Código
Las librerías utilizadas para la solución de esta actividad fueron las siguientes:
```
from selenium import webdriver
import urllib.request
import cv2
import numpy as np
import random
import os
import concurrent.futures as threads
import multiprocessing
```

Definimos una función llamada **url_to_image()** la cual solo utiliza un argumento url como entrada. En este momento utilizamos la librería urllib para convertir la dirección url de la imagen proporcionada a una secuencia de bytes que después es convertida a un arreglo de Numpy. A partir de aquí trabajamos el arreglo para obtener una imagen utilizando el comando **cv2.imdecode**. En ocasiones se encontraron url vacíos que saboteaban el funcionamiento del sistema, por esto fue necesario utilizar un if para descartar todos los url vacíos. 
```
#Función para descargar imagen y convertir a bytes
def url_to_image(url):
  if url is None:
    return []

  try:
    resp = urllib.request.urlopen(url)
    image = np.asarray(bytearray(resp.read()), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)
  except:
    return []

  return image
```  
Generamos una función llamada **save_image_train()** la cual se encarga de guardar las imágenes encontradas en la página web dentro de una carpeta local llamada train utilizando la función de **cv2.imwrite()**. Le asignamos un número de identificación i a cada archivo recibio el cual es utilizado para nombrar el documento en la descarga. De igual manera fue necesario implementar un filtro que omitiera argumentos vacíos utilizando un if.  
```  
#Función para guardar imagen localmente en train
def save_image_train(args):
  i, url = args
  image = url_to_image(url)

  if image is None or len(image) == 0:
    return

  cv2.imwrite(f'./train/{search}/{i}.jpg', image)
```  
Realizamos el mismo procedimiento para descargar las imágenes en la carpeta local test. 
```
#Función para guardar imagen localmente en test
def save_image_test(args):
  i, url = args
  image = url_to_image(url)

  if image is None or len(image) == 0:
    return

  cv2.imwrite(f'./test/{search}/{i}.jpg', image)
```
Para poder navegar en la red y realizar el scrapper descargamos el Chromedriver para ser utilizado con la librería de Selenium. En esta parte del código le dimos el acceso al driver utilizando la función **webdriver.Chrome()**.
```
#Crear driver de Selenium
driver = webdriver.Chrome('C:\webdrivers\chromedriver.exe')  
```
Usamos la función de **input()** para preguntar al usuario el tema a buscar. Aquí el usuario puede responder con "dog" para buscar fotos de perros. 
```
#Obtener input del usuario
search = input("What are you looking for? ")
```
Con la función **driver.get()** le damos la dirección al driver seleccionado para ingresar a la página web de donde queremo obtener la información. 
```
#Navegar a página
driver.get(f'http://www.image-net.org/search?q={search}')
```
Navegar la página web es similar a buscar un libro dentro de una biblioteca. Para llegar a los elementos deseados es necesario buscarlos dentro de su área y utilizando su argumento de referencia. En esta ocasión las imágenes de esta página web vienen dadas dentro de un elemento <a> con una referencia _href_. Implementando la funcion **driver.find_elements_by_css_selector()** aprovechamos este atributo para identificar todos los elementos de interés. Una vez obtenidos los id de los elementos deseados tuvimos que separar este contenido en una lista y eliminar los repetidos, para esto utilizamos el argumento de la línea 76.
```
#Obtener ids de imágenes
ids = driver.find_elements_by_css_selector('a[href*="synset?wnid"]')
ids = [elem.get_attribute('href') for elem in ids]
ids = list(set([elem.split('wnid=')[1] for elem in ids]))
```
Ingresando al id de las imágenes utilizando la función **driver.get()**, obtuvimos un listado de url de imágenes del tema en cuestión. Para seleccionar estas direcciones no dirigimos a ellas utilizando la función **driver.find_elemnt_by_tag_name()** y generamos una lista con todo el contenido recibido. 
```
#Obtener urls de imágenes
urls = []
for id in ids:
  driver.get(f'http://www.image-net.org/api/text/imagenet.synset.geturls?wnid={id}')
  elem = driver.find_element_by_tag_name('pre')
  urls += elem.text.split('\n')
```
Una vez teniendo toda la información necesaria, el primer paso fue realizar un shuffle a la lista de urls para no generar tendencias de la búsqueda que puedan perjudicar el entrenamiento de nuestro sistema. También se dividió la lista urls en donde el 80% de su contenido fuera destinado al entrenamiento y el 20% a la evaluación. Esto lo hicimos utilizando un split del listado. 
```
#Partir en train y test
random.shuffle(urls)
length = len(urls)
train_urls = urls[:int(length * 0.8)]
test_urls = urls[int(length * 0.8):]
```
Teniendo ya los elementos separados conforme su utilización. Es necesario generar las carpetas donde serán guardados los elementos. Asignamos la dirección y implementamos el valor search que es el input del usuario para organizar el contenido. Si no se encuentra esta dirección utilizamos el comando **os.makedirs()** para crearlo.  
```
#Crear folders si no existen
path = f'./train/{search}'
if not os.path.isdir(path):
  os.makedirs(path)
  
path = f'./test/{search}'
if not os.path.isdir(path):
  os.makedirs(path)
```
Debido a que trabajamos con cantidades muy grandes de información, implementamos la función **multiprocessing.cpu_count()** para poder agilizar el proceso de descarga.  
 ```
#Obtener CPUs disponibles
num_cpus = multiprocessing.cpu_count()
```
El último paso es descargar los elementos obtenidos. Para esto utilizamos el la función **threads.ThreadPoolexecutor()** para poder ejecutar las descargas de manera concurrente y así poder realizarlo en menor tiempo.
```
#Descargar y guardar imágenes concurrentemente
with threads.ThreadPoolExecutor(max_workers=num_cpus) as executor:
  result = list(executor.map(save_image_train, enumerate(train_urls)))
  result = list(executor.map(save_image_test, enumerate(test_urls)))
```

## Resultados
Las siguientes imágenes muestran el resultado que obtuvimos realizando la búsqueda de _horse_:

 <p align="center">
  <img src="https://github.com/Linetes/Vision/blob/master/result1.jpg">
</p>

 <p align="center">
  <img src="https://github.com/Linetes/Vision/blob/master/result2.jpg">
</p>
