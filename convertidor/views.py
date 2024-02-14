from django.shortcuts import render, redirect
from .models import *
from django.contrib import messages
# pandas para procesar archivos excel
import pandas as pd
import numpy as np
from django.http import HttpResponse
#Para descargar el xlsx

import xlsxwriter
from io import BytesIO
import re
from django.http import FileResponse
from tempfile import NamedTemporaryFile

def homeView(request):
    """
    Renderiza la vista de inicio.

    Argumentos:
        solicitud (HttpRequest): el objeto de solicitud HTTP.
    
    Devoluciones:
        HttpResponse: la respuesta HTML representada.
    """
    return render(request,'index.html')






def res1(request):
    
    #EPIR
    
    #archivo = request.FILES['archivo_excel']
    #df = pd.read_excel('convertidor/assets/original.xlsx')
    #df = pd.read_excel('convertidor/assets/FALABELLA1.xlsm')
    
    if request.method == 'POST':
        archivo = request.FILES['archivo_excel']
        df1 = pd.read_excel(archivo)
        consecutivo = request.POST['consecutivo']
        
        
        #Borrar los "SubTotal"
        for x in df1.index:
                if df1.loc[x, "Cod.Tienda"] == "SubTotal":
                    df1.drop(x, inplace = True)
        
        
        #Ordenar por codigo de tienda
        df1.sort_values(by='Cod.Tienda', inplace=True)
        
        #Eliminar columnas
        df1.drop(['Cant.Distrib', 'Cant.Recibida', 'Cant.Pendiente'], axis=1, inplace=True)
        
        
        
        #Columna numero de caja
        consecutivo= str(consecutivo)
        conse= "1811045990" + consecutivo
        conse = int(conse)
        #df1['Numero Caja'] = df1.groupby('Tienda').cumcount() + 18110459900000
        df1['Numero Caja'] = df1.groupby('Cod.Tienda').ngroup() + int(conse)
        
        # Convertir la columna a formato de cadena
        
        df1['Numero Caja'] = df1['Numero Caja'].astype(str)  
        df1['Cod.Prod'] = df1['Cod.Prod'].astype(str)
        
        
        df1['UPC'] = df1['UPC'].astype(str)
        # Descargar el DataFrame como un archivo Excel
        
        # Crear el archivo Excel en memoria
        excel_buffer = io.BytesIO()
        df1.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)

        # Devolver el archivo Excel al usuario
        # Crear la respuesta HTTP con el archivo Excel como contenido
        response = HttpResponse(excel_buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = 'attachment; filename=datos.xlsx'

        
        return response

def res2 (request):
    #Nombre archivo Distribuido
    #Original, EPIR,  Plano
    
    if request.method == 'POST':
        try:
            archivo = request.FILES['archivo_excel']
            df = pd.read_excel(archivo)
            ordenCompra = request.POST['ordenCompra']
            linea = request.POST['linea']
            consecutivo = request.POST['consecutivo']
            
            #original
            dfOriginal = pd.read_excel(archivo)
            
            # Limpiar los valores no finitos
            dfOriginal['UPC'] = dfOriginal['UPC'].fillna(0)  # Rellenar los valores NaN con 0
            dfOriginal['UPC'] = dfOriginal['UPC'].replace([np.inf, -np.inf], 0)  # Reemplazar inf con 0
            
            # Eliminar los decimales          
            dfOriginal['UPC'] = dfOriginal['UPC'].astype(str)
            dfOriginal['UPC'] = dfOriginal['UPC'].apply(lambda x: x.split('.')[0])
            dfOriginal['UPC'] = dfOriginal['UPC'].str.lstrip('-')
            
           
            
            #Tabla Epir
            df1 = pd.read_excel(archivo)
            
            
            #Borrar los "SubTotal"
            for x in df1.index:
                    if df1.loc[x, "Cod.Tienda"] == "SubTotal":
                        df1.drop(x, inplace = True)
            
             # Eliminar los decimales
            df1['UPC'] = df1['UPC'].astype(str)
            df1['UPC'] = df1['UPC'].apply(lambda x: x.split('.')[0])
            df1['UPC'] = df1['UPC'].str.lstrip('-')
                       
            
            #Ordenar por codigo de tienda
            #df1.sort_values(by='Cod.Tienda', inplace=True)
            
            #Eliminar columnas
            df1.drop(['Cant.Distrib', 'Cant.Recibida', 'Cant.Pendiente'], axis=1, inplace=True)
            
            
            
            #Columna numero de caja
            consecutivo= str(consecutivo)
            conse= "1811045990" + consecutivo
            conse = int(conse)
            #df1['Numero Caja'] = df1.groupby('Tienda').cumcount() + 18110459900000
            #df1['Numero Caja'] = df1.groupby('Cod.Tienda').ngroup() + int(conse)
            
            # Función para extraer el color después del tercer "/"
            def extraer_color(cadena):
                partes = cadena.split('/')
                if len(partes) > 3:
                    return partes[3]
                else:
                    return ''

            def extraer_ref(cadena):
                partes = cadena.split('/')
                if len(partes) > 2:
                    return partes[2]
                else:
                    return ''


            # Aplicar la función para extraer el color y referencia y agregarlo como una nueva columna
            df1['Color'] = df1['Producto'].apply(extraer_color)
            df1['Ref'] = df1['Producto'].apply(extraer_ref)
            # Ordenar el DataFrame por las columnas "Cod.Tienda" y "Color"
            #df1 = df1.sort_values(by=['Ref', 'Color', 'Cod.Tienda'])
            
       
            df1.sort_values(by=['Ref', 'Color'], inplace=True)
            # Restablecer el índice para evitar ambigüedad
            df1 = df1.reset_index()
            # Eliminar el nombre del índice
            df1.index.name = None
            
            # Agrupar por 'Cod.Tienda', 'Color' y asignar un número a cada grupo
            df1['Numero Caja'] = df1.groupby(['Ref', 'Color', 'Cod.Tienda']).ngroup() + int(conse)
            
            #Si la tienda es 9903 asignarle un consecutivo individual a los elementos del grupo
            for index, (tienda, caja) in enumerate(zip(df1['Cod.Tienda'], df1['Numero Caja'])):
                if tienda == 9903:
                    start_index = index + 1
                    
                    index += 1
                    if df1.loc[index, 'Cod.Tienda'] == 9903:
                        df1.at[index, 'Numero Caja'] = caja
                    
                    if start_index < len(df1):
                        if df1.loc[index, 'Cod.Tienda'] == 9903:
                            df1.loc[start_index:, 'Numero Caja'] += 1
            
            print("EPIR")
            print(df1)       
               
            
            # Eliminar la columna temporal
            df1 = df1.drop(columns=['Color'])           
            df1 = df1.drop(columns=['Ref'])
            
            
            
            # Convertir la columna a formato de cadena
            
            df1['Numero Caja'] = df1['Numero Caja'].astype(str)  
            df1['Cod.Prod'] = df1['Cod.Prod'].astype(int)
            df1['Cod.Prod'] = df1['Cod.Prod'].astype(str)
            df1['Cod.Prod'] = df1['Cod.Prod'].str.lstrip('-')
            
            
            
            
            #Tabla Plano
            
            #Borrar los "SubTotal"
            for x in df.index:
                    if df.loc[x, "Cod.Tienda"] == "SubTotal":
                        df.drop(x, inplace = True)
            
            
            
            # Eliminar los decimales
            df['UPC'] = df['UPC'].astype(str)
            df['UPC'] = df['UPC'].apply(lambda x: x.split('.')[0])
            df['UPC'] = df['UPC'].str.lstrip('-')
                       
            
            
            #Eliminar columnas
            df.drop(['Cant.Distrib', 'Cant.Recibida', 'Cant.Pendiente'], axis=1, inplace=True)
            
           # Columnas para color y tallas
            
            df['Color'] = df['Producto'].str.split('/').str[3]
            
            df['Talla'] = df['Producto'].str.split('/').str[4]
            df['Ref'] = df['Producto'].str.split('/').str[2]
            
            
            
           
            #Ordenar por Color
            df.sort_values(by=['Ref','Color'], inplace=True)
            #df['Numero Caja copia'] = df1['Numero Caja']
            df = df.reset_index()
            # Eliminar el nombre del índice
            df.index.name = None
            
            
             #Columna numero de caja
            consecutivo= str(consecutivo)
            conse= "1811045990" + consecutivo
            conse = int(conse)
            
            # Agrupar por 'Cod.Tienda', 'Color' y asignar un número a cada grupo
            df['Numero Caja'] = df.groupby(['Ref', 'Color', 'Cod.Tienda']).ngroup() + int(conse)
             
             #Si la tienda es 9903 asignarle un consecutivo individual a los elementos del grupo
            for index, (tienda, caja) in enumerate(zip(df['Cod.Tienda'], df['Numero Caja'])):
                if tienda == 9903:
                    start_index = index + 1
                    
                    index += 1
                    if df.loc[index, 'Cod.Tienda'] == 9903:
                        df.at[index, 'Numero Caja'] = caja
                    
                    if start_index < len(df):
                        if df.loc[index, 'Cod.Tienda'] == 9903:
                            df.loc[start_index:, 'Numero Caja'] += 1       
                    
            print("Plano")
            print (df)
                    #Igual que el EPIR
                    
                    
            #df['Numero Caja'] = df.groupby('Tienda').cumcount() + 18110459900000
            
            
            #df['Numero Caja'] = df.groupby('Color').ngroup() + int(conse)
            
            # Convertir la columna a formato de cadena
            
            
            df['Cod.Prod'] = df['Cod.Prod'].astype(int)
            df['Cod.Prod'] = df['Cod.Prod'].astype(str)
            
            # Borrar el guion ("-") si está en la primera posición para todos los datos de la columna 'Cod.Prod'
            df['Cod.Prod'] = df['Cod.Prod'].str.lstrip('-')
           
            
            # Eliminar los decimales
            df['UPC'] = df['UPC'].astype(str)
            df['UPC'] = df['UPC'].apply(lambda x: x.split('.')[0])
            df['UPC'] = df['UPC'].str.lstrip('-')
            
            
            df['Numero Caja'] = df['Numero Caja'].astype(str)
            
            
            #nuevo_df = nuevo_df.merge(df1[['Cod.Tienda', 'Color', 'Numero Caja']], on=['Cod.Tienda', 'Color'], how='left')
            # Crear una nueva tabla para hacer el resumen
            
            #nuevo_df = df.groupby(['Cod.Tienda', 'Tienda', 'Color', 'Ref']).agg({'Cod.Tienda': 'first', 'Tienda': 'first', 'Cod.Prod': 'first', 'UPC': 'last', 'Talla': lambda x: ' - '.join(x), 'Cód.Provee': 'first', 'Emp. Pendiente': 'sum', 'Color': 'first', 'Ref': 'first','Numero Caja':'first'})
            
            nuevo_df = df.groupby(['Cod.Tienda', 'Tienda', 'Color', 'Ref', 'Numero Caja']).agg({'Cod.Tienda': 'first', 'Tienda': 'first', 'Cod.Prod': 'first', 'UPC': 'last', 'Talla': lambda x: ' - '.join(x), 'Cód.Provee': 'first', 'Emp. Pendiente': 'sum', 'Color': 'first', 'Ref': 'first','Numero Caja':'first'})
            
            #result_df = df[df['Cod.Tienda'] != 9903].groupby(['Cod.Tienda', 'Tienda', 'Color', 'Ref']).agg({'Cod.Tienda': 'first', 'Tienda': 'first', 'Cod.Prod': 'first', 'UPC': 'last', 'Talla': lambda x: ' - '.join(x), 'Cód.Provee': 'first', 'Emp. Pendiente': 'sum', 'Color': 'first', 'Ref': 'first','Numero Caja':'first'})
                        
            
            
            nuevo_df.rename(columns={'Talla': 'Producto'}, inplace=True)
            
            # columnas Linea y Orden de compra
            nuevo_df['Linea'] = linea
            nuevo_df['Orden de Compra'] = ordenCompra
            
            
            #Numero de caja
            
            # Ordenar el DataFrame por la columna  "Color"
            #nuevo_df = nuevo_df.sort_values(by='Color')
            #Ordenar por Color
            
            nuevo_df['Color2'] = nuevo_df['Color']  # Create a copy of the "Color" column
            nuevo_df['Referencia'] = nuevo_df['Ref']  # Create a copy of the "Ref" column
            nuevo_df.sort_values(by=['Referencia', 'Color2'], inplace=True)  # Sort the DataFrame by the "Color2" column
            nuevo_df.drop(columns=['Color2'], inplace=True)  # Drop the "Color2" column
            nuevo_df.drop(columns=['Referencia'], inplace=True)  # Drop the "Referencia" column
           
            
            
            # Crear el archivo Excel en memoria
            # Crear un escritor de Excel usando pandas
            excel_buffer = BytesIO()
            writer = pd.ExcelWriter(excel_buffer, engine='xlsxwriter')
            df1.drop('index', axis=1, inplace=True)
            dfOriginal.to_excel(writer, sheet_name='Original', index=False)
            df1.to_excel(writer, sheet_name='EPIR', index=False)
            nuevo_df.to_excel(writer, sheet_name='Plano', index=False)

            # Guardar el archivo de Excel
            writer.close()

            # Asegurarse de que la posición del archivo esté al principio
            excel_buffer.seek(0)

            # Crear la respuesta HTTP con el archivo Excel como contenido
            response = HttpResponse(excel_buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=Distribuido.xlsx'
            return response
        except Exception as e:
            messages.error(request, f"Error: {e}")
        return redirect('convertidor:home')
    
def res2suma(request):
    
    if request.method == 'POST':
        try:
            archivo = request.FILES['archivo_excel']
            
            xls = pd.ExcelFile(archivo)

            # Obtener los nombres de las hojas en el archivo de Excel
            nombreHojas = xls.sheet_names

            # Crear un DataFrame separado para cada hoja
            dfHoja1 = pd.read_excel(xls, nombreHojas[0])
            dfHoja2 = pd.read_excel(xls, nombreHojas[1])
            dfHoja3 = pd.read_excel(xls, nombreHojas[2])
            
            df=dfHoja2
            #Calcular el archivo plano nuevamente
            
            
                        #Tabla Distribuido       
            
            
           # Columnas para color y tallas
            
            df['Color'] = df['Producto'].str.split('/').str[3]
            df['Ref'] = df['Producto'].str.split('/').str[2]
            df['Talla'] = df['Producto'].str.split('/').str[4]
            
        
            linea = dfHoja3['Linea'].iloc[0]            
            ordenCompra = dfHoja3['Orden de Compra'].iloc[0]
            
           
            #Ordenar por Color
            df.sort_values(by=['Ref', 'Color'], inplace=True)
            
            
             #Columna numero de caja
            consecutivo = df['Numero Caja'].iloc[0]
            #df.drop(columns='Numero Caja', inplace=True)
            
            consecutivo= int(consecutivo)
            
            
            
            
            #df.dropna(columns=['Ref'], inplace=True)
            # Convertir la columna a formato de cadena
            
            
            df['Cod.Prod'] = df['Cod.Prod'].astype(int)
            df['Cod.Prod'] = df['Cod.Prod'].astype(str)
            # Borrar el guion ("-") si está en la primera posición para todos los datos de la columna 'Cod.Prod'
            df['Cod.Prod'] = df['Cod.Prod'].str.lstrip('-')
            
            # Eliminar los decimales
            df['UPC'] = df['UPC'].astype(str)
            df['UPC'] = df['UPC'].apply(lambda x: x.split('.')[0])
            df['UPC'] = df['UPC'].str.lstrip('-')
            
            
            
            df['Numero Caja'] = df['Numero Caja'].astype(str)
            
            
            # Crear una nueva tabla para hacer el resumen
            
            nuevo_df = df.groupby(['Cod.Tienda', 'Tienda', 'Color', 'Ref', 'Numero Caja']).agg({'Cod.Tienda': 'first', 'Tienda': 'first', 'Cod.Prod': 'first',  'UPC': 'last', 'Talla': lambda x: ' - '.join(x), 'Cód.Provee': 'first', 'Emp. Pendiente': 'sum', 'Color': 'first', 'Ref': 'first', 'Numero Caja': 'first'})
            
            nuevo_df.rename(columns={'Talla': 'Producto'}, inplace=True)
            
            # columnas Linea y Orden de compra
            
            nuevo_df['Linea'] = linea
            nuevo_df['Orden de Compra'] = ordenCompra
            
            
            #Numero de caja
            
            # Ordenar el DataFrame por la columna  "Color"
            #nuevo_df = nuevo_df.sort_values(by='Color')
            #Ordenar por Color
            
            nuevo_df['Color2'] = nuevo_df['Color']  # Create a copy of the "Color" column
            nuevo_df['Referencia']= nuevo_df['Ref']
            nuevo_df.sort_values(by=['Referencia', 'Color2'], inplace=True)  # Sort the DataFrame by the "Color2" column
            nuevo_df.drop(columns=['Color2', 'Referencia'], inplace=True)  # Drop the "Color2" column
            
            # Incrementar el consecutivo por cada fila
            #nuevo_df['Numero Caja'] = range(consecutivo, consecutivo + len(nuevo_df))  # Usar la función range para generar una secuencia de valores consecutivos
            #nuevo_df['Numero Caja'] = nuevo_df['Numero Caja'].astype(str)
            
            
             # Eliminar los decimales
            dfHoja1['UPC'] = dfHoja1['UPC'].astype(str)
            dfHoja1['UPC'] = dfHoja1['UPC'].apply(lambda x: x.split('.')[0])
            dfHoja1['UPC'] = dfHoja1['UPC'].str.lstrip('-')
            
            hojaDos= pd.read_excel(xls, nombreHojas[1])
            
            hojaDos['UPC'] = hojaDos['UPC'].astype(str)
            hojaDos['UPC'] = hojaDos['UPC'].apply(lambda x: x.split('.')[0])
            hojaDos['UPC'] = hojaDos['UPC'].str.lstrip('-')
            
            
            excel_buffer = BytesIO()
            writer = pd.ExcelWriter(excel_buffer, engine='xlsxwriter')
            
            
            hojaDos.reset_index(drop=True, inplace=True)
            hojaDos['Numero Caja'] = hojaDos['Numero Caja'].astype(str)
            #hojaDos.drop(columns=['Unnamed: 0', 'index'], inplace=True)
            
            dfHoja1.to_excel(writer, sheet_name='Original', index=False)
            hojaDos.to_excel(writer, sheet_name='EPIR', index=False)
            nuevo_df.to_excel(writer, sheet_name='Plano', index=False)
           
            # Guardar el archivo de Excel
            writer.close()
            # Asegurarse de que la posición del archivo esté al principio
            excel_buffer.seek(0)

            # Escribir cada DataFrame en una hoja de Excel
            
            # Devolver el archivo Excel al usuario
            # Crear la respuesta HTTP con el archivo Excel como contenido
            response = HttpResponse(excel_buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=DistribuidoR.xlsx'
            
            return response
            
            
        except Exception as e:
            messages.error(request, f"Error: {e}")
        return redirect('convertidor:home')


    return redirect('convertidor:home')

def res3 (request):
    #Almacenado
    #Original Almacenado
    if request.method == 'POST':
        try:
            archivo = request.FILES['archivo_excel']
            df = pd.read_excel(archivo)
            ordenCompra = request.POST['ordenCompra']
            linea = request.POST['linea']
            consecutivo = request.POST['consecutivo']
            uniCaja = request.POST['uniCaja']
            
            #DF original
            dfOriginal = pd.read_excel(archivo)
            
                        # Limpiar los valores no finitos
            dfOriginal['UPC'] = dfOriginal['UPC'].fillna(0)  # Rellenar los valores NaN con 0
            dfOriginal['UPC'] = dfOriginal['UPC'].replace([np.inf, -np.inf], 0)  # Reemplazar inf con 0
            
            #dfOriginal['UPC'] = dfOriginal['UPC'].astype(int)
            #dfOriginal['UPC'] = dfOriginal['UPC'].round(0)
            # Eliminar los decimales
            
            dfOriginal['UPC'] = dfOriginal['UPC'].astype(str)
            dfOriginal['UPC'] = dfOriginal['UPC'].apply(lambda x: x.split('.')[0])
            dfOriginal['UPC'] = dfOriginal['UPC'].str.lstrip('-')
            
            #print(dfOriginal)
            #Almacenado
            
            
            #Borrar los "SubTotal"
            for x in df.index:
                    if df.loc[x, "Cod.Tienda"] == "SubTotal":
                        df.drop(x, inplace = True)
            
            
            # Crear las nuevas columnas 'Talla' y 'Color'
            #df['Producto '] = df['Producto'].apply(extract_talla)
            
            df.insert(6, 'Producto ', df['Producto'].apply(extract_talla))
            df['Color'] = df['Producto'].apply(extract_color)

            
            #Eliminar columnas
            df.drop(['Producto'], axis=1, inplace=True)
            
            # Crear una nueva tabla con los registros separados por cuántas cajas se pueden empacar
            nueva_tabla = []

            for index, row in df.iterrows():
                unidades = row['Emp. Pendiente']
                capacidad_caja = int(uniCaja)  # Capacidad de la caja (reemplaza con el valor real)
                
                while unidades > 0:
                    if unidades >= capacidad_caja:
                        nueva_fila = row.copy()
                        nueva_fila['Emp. Pendiente'] = capacidad_caja
                        nueva_tabla.append(nueva_fila)
                        unidades -= capacidad_caja
                    else:
                        nueva_fila = row.copy()
                        nueva_fila['Emp. Pendiente'] = unidades
                        nueva_tabla.append(nueva_fila)
                        break

            nueva_df = pd.DataFrame(nueva_tabla)
            
             #Numero de caja
            consecutivo= str(consecutivo)
            conse= "1811045990" + consecutivo
            conse = int(conse)
            
            # columnas Linea y Orden de compra
            nueva_df['Linea'] = linea
            nueva_df['Orden de Compra'] = ordenCompra
            
            nueva_df = nueva_df.sort_values(by=['Color', 'Producto '])
            # Incrementar el consecutivo por cada fila
            nueva_df['Numero Caja'] = range(conse, conse + len(nueva_df))  # Usar la función range para generar una secuencia de valores consecutivos
            
            #Convertir columnas a string para evitar el formato de excel
            nueva_df['Numero Caja'] = nueva_df['Numero Caja'].astype(str)
            nueva_df['UPC'] = nueva_df['UPC'].astype(str)
            # Eliminar los decimales
            nueva_df['UPC'] = nueva_df['UPC'].apply(lambda x: x.split('.')[0])
            nueva_df['Orden de Compra'] = nueva_df['Orden de Compra'].astype(str)
            nueva_df['Cod.Prod'] = nueva_df['Cod.Prod'].astype(str)
            # Eliminar los decimales
            nueva_df['Cod.Prod'] = nueva_df['Cod.Prod'].apply(lambda x: x.split('.')[0])
            
            nueva_df= nueva_df.drop(['Cant.Recibida','Cant.Pendiente','Cant.Distrib'], axis=1, errors = 'ignore')
            
            
            
            
            # Crear el archivo Excel en memoria
            # Crear un escritor de Excel usando pandas
            excel_buffer = BytesIO()
            writer = pd.ExcelWriter(excel_buffer, engine='xlsxwriter')
            
            dfOriginal.to_excel(writer, sheet_name='Original', index=False)
            nueva_df.to_excel(writer, sheet_name='Almacenado', index=False)
           
            # Guardar el archivo de Excel
            writer.close()
            # Asegurarse de que la posición del archivo esté al principio
            excel_buffer.seek(0)

            # Escribir cada DataFrame en una hoja de Excel
            
            # Devolver el archivo Excel al usuario
            # Crear la respuesta HTTP con el archivo Excel como contenido
            response = HttpResponse(excel_buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=Almacenado.xlsx'
            return response
    
        except Exception as e:
            messages.error(request, f"Error: {e}")
        
    return redirect('convertidor:home')
    
    
    


# Definir una función para extraer la talla y el color
def extract_talla(cadena):
    matches = re.findall(r'\b(\d+)\b', cadena)  # Buscar el último número como la talla
    if matches:
        return matches[-1]
    else:
        return None

def extract_color(cadena):
    
    for char in cadena:
        if char == '/':
            
            words = cadena.split('/')  # Dividir la cadena en palabras usando '/'
            color = words[3]  # El color es el 4 elemento después de dividir
            return color
        
        elif char == ' ':
           
            words = cadena.split()  # Dividir la cadena en palabras
            if len(words) >= 4:
                color_index = 3  # El color está después del tercer espacio
                talla_index = -1  # El índice de la talla es el último elemento
                color = " ".join(words[color_index:talla_index])  # Unir las palabras para formar el color
                return color
            
            else:
                return None

