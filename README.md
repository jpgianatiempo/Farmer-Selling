# Farmer-Selling

Proyecto diseñado para visualizar la información de la evolución de las ventas del productor y de las DJVE.

Se compone de diversas carpetas:
- **Data**
    - *Base*: Data histórica de farmer selling.
- **Scripts**
    - *Add New Week*: Scrap y wrangling para agregar los datos de la última semana.
    - *Scrap Faltantes*: Scrap y wrangling para agregar si falta alguna semana.
    - *App*: dash que corre en local para ver los datos históricos.


## Proceso para actualizar el proyecto
Para correr el proyecto solamente se debería:
1. Correr el script de *./AddNewWeek.py*
2. Correr el script de *./App.py*
En caso de perder alguna semana entre updates:
3. Correr el script de *./ScrapFaltantes.py* y cambiar las url por las semanas que no actualizaron.


