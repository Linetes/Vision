from selenium import webdriver
import urllib.request
import cv2
import numpy as np
import random
import os
import concurrent.futures as threads
import multiprocessing

## Función para descargar imagen y convertir a bytes
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

## Función para guardar imagen localmente en train
def save_image_train(args):
  i, url = args
  image = url_to_image(url)

  if image is None or len(image) == 0:
    return

  cv2.imwrite(f'./train/{search}/{i}.jpg', image)

## Función para guardar imagen localmente en test
def save_image_test(args):
  i, url = args
  image = url_to_image(url)

  if image is None or len(image) == 0:
    return

  cv2.imwrite(f'./test/{search}/{i}.jpg', image)

# Crear driver de Selenium
driver = webdriver.Chrome('C:\webdrivers\chromedriver.exe')

# Obtener input del usuario
search = input("What are you looking for? ")

# Navegar a página
driver.get(f'http://www.image-net.org/search?q={search}')

# Obtener ids de imágenes
ids = driver.find_elements_by_css_selector('a[href*="synset?wnid"]')
ids = [elem.get_attribute('href') for elem in ids]
ids = list(set([elem.split('wnid=')[1] for elem in ids]))

# Obtener urls de imágenes
urls = []
for id in ids:
  driver.get(f'http://www.image-net.org/api/text/imagenet.synset.geturls?wnid={id}')
  elem = driver.find_element_by_tag_name('pre')
  urls += elem.text.split('\n')

# Partir en train y test
random.shuffle(urls)
length = len(urls)
train_urls = urls[:int(length * 0.8)]
test_urls = urls[int(length * 0.8):]

# Crear folders si no existen
path = f'./train/{search}'
if not os.path.isdir(path):
  os.makedirs(path)

path = f'./test/{search}'
if not os.path.isdir(path):
  os.makedirs(path)

# Obtener CPUs disponibles
num_cpus = multiprocessing.cpu_count()

# Descargar y guardar imágenes concurrentemente
with threads.ThreadPoolExecutor(max_workers=num_cpus) as executor:
  result = list(executor.map(save_image_train, enumerate(train_urls)))
  result = list(executor.map(save_image_test, enumerate(test_urls)))
