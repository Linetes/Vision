# Vision
Proyecto para la materia de visión computacional
## Integrantes del equipo
Juan Pablo Ramos Sanabria, 
Diego Alberto Alvarez Rodríguez, 
César Francisco Barraza Aguilar, 
César Buenfil Vázquez y 
Lisset Botello Santiago.

## Planteamiento del problema 
Usar la técnica de web data scraping para recopilar imágenes de una base de datos en línea. 
La base de datos que usaremos es: ImageNet:http://image-net.org/about-overview

El programa debe solicitar un término de búsqueda al usuario, una vez ingresado el programa accesa a ImageNet y efectúa una consulta por ese término. El programa descarga las imágenes que arrojó la base de datos, el 80% de las imágenes deben ser guardadas en una carpeta llamada ./train/<término_de_búsqueda>, el 20% restante deben ser guardadas en una carpeta ./test/<término_de_búsqueda>.

## Explicación del código
```