#%%
from os import getcwd
import pandas as pd
import requests
from bs4 import BeautifulSoup
from lxml import html
import numpy as np

#url del último publicado
url = 'https://www.magyp.gob.ar/sitio/areas/ss_mercados_agropecuarios/areas/granos/_archivos/000058_Estad%C3%ADsticas/000020_Compras%20y%20DJVE%20de%20Granos.php'
df = pd.read_html(url)[5]

converters = {c:lambda x: str(x) for c in df.columns}

all_list = pd.read_html(url, converters=converters,thousands=None)

trigo = all_list[4]
trigo["Grano"] = "Trigo"
fecha = trigo.columns[0].split("AL ")[1]
trigo["Fecha"] = fecha
trigo["Fecha"] = pd.to_datetime(trigo['Fecha'], dayfirst=True)
trigo.rename(columns={ trigo.columns[0]: "Sector" }, inplace = True)


maiz = all_list[5]
maiz["Grano"] = "Maíz"
maiz["Fecha"] = fecha
maiz["Fecha"] = pd.to_datetime(maiz['Fecha'], dayfirst=True)
maiz.rename(columns={ maiz.columns[0]: "Sector" }, inplace = True)

sorgo = all_list[6]
sorgo["Grano"] = "Sorgo"
sorgo["Fecha"] = fecha
sorgo["Fecha"] = pd.to_datetime(sorgo['Fecha'], dayfirst=True)
sorgo.rename(columns={ sorgo.columns[0]: "Sector" }, inplace = True)


cebcerv = all_list[7]
cebcerv["Grano"] = "Cebada Cervecera"
cebcerv["Fecha"] = fecha
cebcerv["Fecha"] = pd.to_datetime(cebcerv['Fecha'], dayfirst=True)
cebcerv.rename(columns={ cebcerv.columns[0]: "Sector" }, inplace = True)


cebforr = all_list[8]
cebforr["Grano"] = "Cebada Forrajera"
cebforr["Fecha"] = fecha
cebforr["Fecha"] = pd.to_datetime(cebforr['Fecha'], dayfirst=True)
cebforr.rename(columns={ cebforr.columns[0]: "Sector" }, inplace = True)


soja = all_list[9]
soja["Grano"] = "Soja"
soja["Fecha"] = fecha
soja["Fecha"] = pd.to_datetime(soja['Fecha'], dayfirst=True)
soja.rename(columns={ soja.columns[0]: "Sector" }, inplace = True)


gira = all_list[10]
gira["Grano"] = "Girasol"
gira["Fecha"] = fecha
gira["Fecha"] = pd.to_datetime(gira['Fecha'], dayfirst=True)
gira.rename(columns={ gira.columns[0]: "Sector" }, inplace = True)


#uno todos
del(df)
df = pd.concat([trigo,maiz,sorgo,cebcerv,cebforr,soja,gira])
del(trigo,maiz,sorgo,cebcerv,cebforr,soja,gira)
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
              Total_a_Fijar = df["Total_a_Fijar"].str.rstrip(" (*)"),
              Total_Fijado = df["Total_Fijado"].str.rstrip(" (*)"),
              Saldo_a_Fijar = df["Saldo_a_Fijar"].str.rstrip(" (*)"),
              DJVE_Acumuladas = df["DJVE_Acumuladas"].str.rstrip(" (*)")
                )

#pasar a número, sacando reemplazando comas por puntos
df = df.assign(Semanal = df["Semanal"].str.replace(",","."),
              Total_Comprado = df["Total_Comprado"].str.replace(",","."),
              Total_Precio_Hecho = df["Total_Precio_Hecho"].str.replace(",","."),
              Total_a_Fijar = df["Total_a_Fijar"].str.replace(",","."),
              Total_Fijado = df["Total_Fijado"].str.replace(",","."),
              Saldo_a_Fijar = df["Saldo_a_Fijar"].str.replace(",","."),
              DJVE_Acumuladas = df["DJVE_Acumuladas"].str.replace(",",".")
                )

df = df.astype({"Semanal": float,
               "Total_Comprado": float,
               "Total_Precio_Hecho": float,
               "Total_a_Fijar": float,
               "Total_Fijado": float,
               "Saldo_a_Fijar": float,
               "DJVE_Acumuladas": float
               })


# Genero nuevas variables para el rbind -----------------------------------

df = df.assign(Total_sin_Precio = df.Total_a_Fijar.fillna(0) - df.Total_Fijado.fillna(0),
              Total_con_Precio = lambda x: (x['Total_Comprado'].fillna(0) -  x['Total_sin_Precio'].fillna(0)),
              #df.Total_Comprado.fillna(0) - df.Total_sin_Precio.fillna(0),
              Ano_Campaña = df.Campaña.str.split("/").str[1].astype(int)+2000,
              Ano_Mes = df.Ano.astype(str)+df.Mes.astype(str),
              id = lambda x: (np.select([x["Ano"] < x["Ano_Campaña"], x["Ano"] == x["Ano_Campaña"]],[x["Numero_de_Semana"], x["Numero_de_Semana"] + 52], x["Numero_de_Semana"]+104))
)

#selecciono columnas deseadas
df = df.loc[:, ~df.columns.isin(["Semanal","Total_Precio_Hecho","Saldo_a_Fijar"])]


# Cargo data --------------------------------------------------------------

#cargo, omito primer columna y transformo a fecha la col Fecha
base = pd.read_csv("./Data/Base.csv", encoding = "latin").iloc[:, 1:].assign(Fecha = lambda x: (pd.to_datetime(x["Fecha"], format = '%Y-%m-%d')))

#Check for update
if (max(base.Fecha) < max(df.Fecha)):
  print("Actualizando la base ...")
  a = base.append(pd.DataFrame(data = df), ignore_index=True)
  a.to_csv("./Data/Base.csv", encoding='utf-8')
  print("Base actualizada al ",max(a.Fecha))
else:
  print("La base ya esta actualizada al ",max(base.Fecha))

