from os import getcwd
import pandas as pd
import numpy as np
import lxml
from pandas.core.tools import numeric

#FECHAS QUE SE PASARON SIN ACTUALIZAR
urls = ["https://www.magyp.gob.ar/sitio/areas/ss_mercados_agropecuarios/areas/granos/_archivos/000058_Estad%C3%ADsticas/_compras_historicos/2019/01_embarque_2019-11-06.php",
"https://www.magyp.gob.ar/sitio/areas/ss_mercados_agropecuarios/areas/granos/_archivos/000058_Estad%C3%ADsticas/_compras_historicos/2021/01_embarque_2021-06-09.php",
"https://www.magyp.gob.ar/sitio/areas/ss_mercados_agropecuarios/areas/granos/_archivos/000058_Estad%C3%ADsticas/_compras_historicos/2021/01_embarque_2021-06-16.php"
]

a = pd.DataFrame()
url1 = urls[0]
dff = pd.read_html(url1)[5]
converters = {c:lambda x: str(x) for c in dff.columns}

for url in urls:
  all_list = pd.read_html(url, converters=converters,thousands=None)

  trigo = all_list[1]
  trigo["Grano"] = "Trigo"
  fecha = trigo.columns[0].split("AL ")[1]
  trigo["Fecha"] = fecha
  trigo["Fecha"] = pd.to_datetime(trigo['Fecha'], dayfirst=True)
  trigo.rename(columns={ trigo.columns[0]: "Sector" }, inplace = True)

  maiz = all_list[2]
  maiz["Grano"] = "Maíz"
  maiz["Fecha"] = fecha
  maiz["Fecha"] = pd.to_datetime(maiz['Fecha'], dayfirst=True)
  maiz.rename(columns={ maiz.columns[0]: "Sector" }, inplace = True)

  sorgo = all_list[3]
  sorgo["Grano"] = "Sorgo"
  sorgo["Fecha"] = fecha
  sorgo["Fecha"] = pd.to_datetime(sorgo['Fecha'], dayfirst=True)
  sorgo.rename(columns={ sorgo.columns[0]: "Sector" }, inplace = True)

  cebcerv = all_list[4]
  cebcerv["Grano"] = "Cebada Cervecera"
  cebcerv["Fecha"] = fecha
  cebcerv["Fecha"] = pd.to_datetime(cebcerv['Fecha'], dayfirst=True)
  cebcerv.rename(columns={ cebcerv.columns[0]: "Sector" }, inplace = True)

  cebforr = all_list[5]
  cebforr["Grano"] = "Cebada Forrajera"
  cebforr["Fecha"] = fecha
  cebforr["Fecha"] = pd.to_datetime(cebforr['Fecha'], dayfirst=True)
  cebforr.rename(columns={ cebforr.columns[0]: "Sector" }, inplace = True)

  soja = all_list[6]
  soja["Grano"] = "Soja"
  soja["Fecha"] = fecha
  soja["Fecha"] = pd.to_datetime(soja['Fecha'], dayfirst=True)
  soja.rename(columns={ soja.columns[0]: "Sector" }, inplace = True)

  gira = all_list[7]
  gira["Grano"] = "Girasol"
  gira["Fecha"] = fecha
  gira["Fecha"] = pd.to_datetime(gira['Fecha'], dayfirst=True)
  gira.rename(columns={ gira.columns[0]: "Sector" }, inplace = True)

  #uno todos
  df = pd.concat([trigo,maiz,sorgo,cebcerv,cebforr,soja,gira])

  #agregar fecha al extraer de columna compras al...
  df = df.assign(Ano = df['Fecha'].dt.year,
               Mes = df['Fecha'].dt.month,
               Numero_Semana = df['Fecha'].dt.week)


  #Filtro para quedarme con las campañas actuales, no las que tienen ()
  df = df[~df["Semanal"].str.startswith('(')]
  df = df[~df["Total Comprado (1)"].str.startswith('(')]

  #Renombro columnas
  df.columns = ["Sector","Campaña","Semanal","Total_Comprado","Total_Precio_Hecho","Total_a_Fijar","Total_Fijado","Saldo_a_Fijar","DJVE_Acumuladas","Grano","Fecha","Ano","Mes","Numero_de_Semana"]

  #acomodo los sectores
  conditions = [
  df["Sector"].str.contains("Exportador"),
  df["Sector"].str.contains("Industria"),
  df["Sector"].str.contains("Total")
  ]
  choices = ["Sector Exportador", "Sector Industrial", "Total"]

  df["Sector"] = np.select(conditions, choices)

  #saco los puntos primero
  df = df.assign(Semanal = df["Semanal"].str.replace(".",""),
              Total_Comprado = df["Total_Comprado"].str.replace(".",""),
              Total_Precio_Hecho = df["Total_Precio_Hecho"].str.replace(".",""),
              Total_a_Fijar = df["Total_a_Fijar"].str.replace(".",""),
              Total_Fijado = df["Total_Fijado"].str.replace(".",""),
              Saldo_a_Fijar = df["Saldo_a_Fijar"].str.replace(".",""),
              DJVE_Acumuladas = df["DJVE_Acumuladas"].str.replace(".","")
                )

  #saco caracteres raros
  df = df.assign(Semanal = df["Semanal"].str.rstrip(" (*)"),
              Total_Comprado = df["Total_Comprado"].str.rstrip(" (*)"),
              Total_Precio_Hecho = df["Total_Precio_Hecho"].str.rstrip(" (*)"),
              Total_a_Fijar = df["Total_a_Fijar"].str.rstrip(" (*)/"),
              Total_Fijado = df["Total_Fijado"].str.rstrip(" (*)/"),
              Saldo_a_Fijar = df["Saldo_a_Fijar"].str.rstrip(" (*)/"),
              DJVE_Acumuladas = df["DJVE_Acumuladas"].str.rstrip(" (*)/")
                )

  #reemplazando comas por puntos
  df = df.assign(Semanal = df["Semanal"].str.replace(",","."),
              Total_Comprado = df["Total_Comprado"].str.replace(",","."),
              Total_Precio_Hecho = df["Total_Precio_Hecho"].str.replace(",","."),
              Total_a_Fijar = df["Total_a_Fijar"].str.replace(",","."),
              Total_Fijado = df["Total_Fijado"].str.replace(",","."),
              Saldo_a_Fijar = df["Saldo_a_Fijar"].str.replace(",","."),
              DJVE_Acumuladas = df["DJVE_Acumuladas"].str.replace(",",".")
                )

  #saco espacios
  df = df.assign(Semanal = df["Semanal"].str.replace(" ",""),
              Total_Comprado = df["Total_Comprado"].str.replace(" ",""),
              Total_Precio_Hecho = df["Total_Precio_Hecho"].str.replace(" ",""),
              Total_a_Fijar = df["Total_a_Fijar"].str.replace(" ",""),
              Total_Fijado = df["Total_Fijado"].str.replace(" ",""),
              Saldo_a_Fijar = df["Saldo_a_Fijar"].str.replace(" ",""),
              DJVE_Acumuladas = df["DJVE_Acumuladas"].str.replace(" ","")
                )
  #join con resto
  a = pd.concat([a,df])
  a = a.replace("#¡VALOR!",np.nan)
  a["Total_Comprado"] = a["Total_Comprado"].str.rstrip(" /")

#paso a número
a = a.astype({"Semanal": float,
               "Total_Comprado": float,
               "Total_Precio_Hecho": float,
               "Total_a_Fijar": float,
               "Total_Fijado": float,
               "Saldo_a_Fijar": float,
               "DJVE_Acumuladas": float
               })


# Genero nuevas variables para el rbind -----------------------------------

a = a.assign(Total_sin_Precio = a.Total_a_Fijar.fillna(0) - a.Total_Fijado.fillna(0),
              Total_con_Precio = lambda x: (x['Total_Comprado'].fillna(0) -  x['Total_sin_Precio'].fillna(0)),
              #df.Total_Comprado.fillna(0) - df.Total_sin_Precio.fillna(0),
              Ano_Campaña = a.Campaña.str.split("/").str[1].astype(int)+2000,
              Ano_Mes = a.Ano.astype(str)+a.Mes.astype(str),
              id = lambda x: (np.select([x["Ano"] < x["Ano_Campaña"], x["Ano"] == x["Ano_Campaña"]],[x["Numero_de_Semana"], x["Numero_de_Semana"] + 52], x["Numero_de_Semana"]+104))
)

#selecciono columnas deseadas
a = a.loc[:, ~a.columns.isin(["Semanal","Total_Precio_Hecho","Saldo_a_Fijar"])]




#cargo, omito primer columna y transformo a fecha la col Fecha
base = pd.read_csv("./Data/Base.csv", encoding = "latin").iloc[:, 1:].assign(Fecha = lambda x: (pd.to_datetime(x["Fecha"], format = '%Y-%m-%d')))


#chequear si existen esas semanas y en ese caso guardar
#for unique fecha
for n in a.Fecha.unique():
  if (~base.Fecha.isin([n])):
    print("Agregando data del ",n)
    base = base.append(pd.DataFrame(a[a["Fecha"]==n], ignore_index = True))
    base.to_csv("./Data/Base.csv", encoding='utf-8')
  else:
    print("La fecha ",n," ya estaba cargada.")
  print("La base debería estar lista para usar.")
