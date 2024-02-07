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



def cargar_archivo_excel(request):
    if request.method == 'POST' and request.FILES['archivo_excel']:
        archivo = request.FILES['archivo_excel']
        df = pd.read_excel(archivo)
        # Trabajar con el DataFrame de Pandas
        # Procesa los datos como desees
        
        # Leer el archivo de Excel en un DataFrame
        #df = pd.read_excel('almacenamiento_jeans.xlsx')

        # Crear una nueva columna para el color extrayendo la subcadena "AZC" de la columna "Producto"
        df['Color'] = df['Producto'].str.extract(r'AZC/(\w+)')

        # Agrupar por tienda y color, y combinar las tallas en una sola entrada
        df_grouped = df.groupby(['Cod.Tienda', 'Color', 'Cod.Producto', 'UPC', 'Cod.Provee']).agg({'Producto': lambda x: ', '.join(x)})

        # Realizar cálculos para obtener el UPC final, la suma de cantidades y conservar las columnas requeridas
        df_result = df_grouped.reset_index()
        # Agrega el último UPC del producto
        df_result['UPC_final'] = df.groupby('Cod.Producto')['UPC'].last()
        # Suma de cantidades del conjunto de tallas
        df_result['Emp.Pendiente'] = df.groupby(['Cod.Tienda', 'Color', 'Cod.Producto', 'Cod.Provee'])['Emp.Pendiente'].sum()

        # Crear una nueva tabla con los resultados
        nueva_tabla = df_result[['Cod.Tienda', 'Cod.Producto', 'UPC_final', 'Producto', 'Cod.Provee', 'Emp.Pendiente', 'Color']]

        nueva_tabla.to_excel('nueva_tabla_jeans.xlsx', index=False)
        
        # Crear la respuesta HTTP con el archivo adjunto
        nombre_archivo = 'nueva_tabla_jeans.xlsx'  # Nombre del archivo de Excel
        response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'

        # Leer el archivo de Excel y escribir su contenido en la respuesta HTTP
        with open(nombre_archivo, 'rb') as excel_file:
            response.write(excel_file.read())

        return response 
    return HttpResponse('Error en la carga del archivo')


def resultadosJeansFinal(df):
   

    # Leer el archivo de Excel en un DataFrame
    df = pd.read_excel('almacenamiento_jeans.xlsx')

    # Crear una nueva columna para el color extrayendo la subcadena "AZC" de la columna "Producto"
    df['Color'] = df['Producto'].str.extract(r'AZC/(\w+)')

    # Agrupar por tienda y color, y combinar las tallas en una sola entrada
    df_grouped = df.groupby(['Cod.Tienda', 'Color', 'Cod.Producto', 'UPC', 'Cod.Provee']).agg({'Producto': lambda x: ', '.join(x)})

    # Realizar cálculos para obtener el UPC final, la suma de cantidades y conservar las columnas requeridas
    df_result = df_grouped.reset_index()
    # Agrega el último UPC del producto
    df_result['UPC_final'] = df.groupby('Cod.Producto')['UPC'].last()
    # Suma de cantidades del conjunto de tallas
    df_result['Emp.Pendiente'] = df.groupby(['Cod.Tienda', 'Color', 'Cod.Producto', 'Cod.Provee'])['Emp.Pendiente'].sum()

    # Crear una nueva tabla con los resultados
    nueva_tabla = df_result[['Cod.Tienda', 'Cod.Producto', 'UPC_final', 'Producto', 'Cod.Provee', 'Emp.Pendiente', 'Color']]

    nueva_tabla.to_excel('nueva_tabla_jeans.xlsx', index=False)
    
    # Crear la respuesta HTTP con el archivo adjunto
    nombre_archivo = 'nueva_tabla_jeans.xlsx'  # Nombre del archivo de Excel
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{nombre_archivo}"'

    # Leer el archivo de Excel y escribir su contenido en la respuesta HTTP
    with open(nombre_archivo, 'rb') as excel_file:
        response.write(excel_file.read())

    return response

def resumen(request):
    try:
        
        if request.method == 'POST' and request.FILES['archivo_excel']:
            archivo = request.FILES['archivo_excel']
            df = pd.read_excel(archivo)
            
            # Trabajar con el DataFrame de Pandas
            # Procesa los datos como desees
            
            #Eliminar filas que contengan la palabra "SubTotal"
            for x in df.index:
                if df.loc[x, "Cod.Tienda"] == "SubTotal":
                    df.drop(x, inplace = True)
            
            # Leer el archivo de Excel en un DataFrame
            #df = pd.read_excel('almacenamiento_jeans.xlsx')

            # Crear una nueva columna para el color extrayendo la subcadena del color de la columna "Producto"
            #df['Color'] = df['Producto'].str.split('/').str[3]
            
            # Crear un nuevo archivo Excel con el DataFrame modificado
            with NamedTemporaryFile() as temp:
                with pd.ExcelWriter(temp.name, engine='xlsxwriter') as writer:
                    df.to_excel(writer, index=False, sheet_name='Sheet1')

                temp.seek(0)

                # Crear una FileResponse con el archivo adjunto para descargar
                response = FileResponse(open(temp.name, 'rb'), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                response['Content-Disposition'] = 'attachment; filename=nuevo_resumen.xlsx'

                return response  # Devolver la FileResponse con el archivo adjunto para descargar
                

        
    except Exception as e:
        messages.error(request, f"Error: {e}")
    return HttpResponse('Error en la carga del archivo')
    
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
        df1['UPC'] = df1['UPC'].astype(int)
        
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
            
            dfOriginal['UPC'] = dfOriginal['UPC'].astype(int)
            dfOriginal['UPC'] = dfOriginal['UPC'].round(0)
            dfOriginal['UPC'] = dfOriginal['UPC'].astype(str)
            dfOriginal['UPC'] = dfOriginal['UPC'].str.lstrip('-')
            
            
            #Tabla Epir
            df1 = pd.read_excel(archivo)
            
            
            #Borrar los "SubTotal"
            for x in df1.index:
                    if df1.loc[x, "Cod.Tienda"] == "SubTotal":
                        df1.drop(x, inplace = True)
            
            
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

            # Aplicar la función para extraer el color y agregarlo como una nueva columna
            df1['Color'] = df1['Producto'].apply(extraer_color)
            # Ordenar el DataFrame por las columnas "Cod.Tienda" y "Color"
            df1 = df1.sort_values(by=['Cod.Tienda', 'Color'])
            
            # Restablecer el índice para evitar ambigüedad
            df1 = df1.reset_index()
            # Eliminar el nombre del índice
            df1.index.name = None
            # Agrupar por 'Cod.Tienda', 'Color' y asignar un número a cada grupo
            df1['Numero Caja'] = df1.groupby(['Cod.Tienda', 'Color']).ngroup() + int(conse)
            
            
            # Eliminar la columna temporal
            df1 = df1.drop(columns=['Color'])
            # Convertir la columna a formato de cadena
            
            df1['Numero Caja'] = df1['Numero Caja'].astype(str)  
            df1['Cod.Prod'] = df1['Cod.Prod'].astype(int)
            df1['Cod.Prod'] = df1['Cod.Prod'].astype(str)
            df1['Cod.Prod'] = df1['Cod.Prod'].str.lstrip('-')
            
            df1['UPC'] = df1['UPC'].astype(int)            
            df1['UPC'] = df1['UPC'].astype(str)
            df1['UPC'] = df1['UPC'].str.lstrip('-')
            
            
            
            #Tabla Distribuido
            
            #Borrar los "SubTotal"
            for x in df.index:
                    if df.loc[x, "Cod.Tienda"] == "SubTotal":
                        df.drop(x, inplace = True)
            
            
            
            
            
        
            
            #Eliminar columnas
            df.drop(['Cant.Distrib', 'Cant.Recibida', 'Cant.Pendiente'], axis=1, inplace=True)
            
           # Columnas para color y tallas
            
            df['Color'] = df['Producto'].str.split('/').str[3]
            
            df['Talla'] = df['Producto'].str.split('/').str[4]
            #print(df)
            
           
            #Ordenar por Color
            df.sort_values(by='Color', inplace=True)
            
            
             #Columna numero de caja
            consecutivo= str(consecutivo)
            conse= "1811045990" + consecutivo
            conse = int(conse)
            
                    
            #df['Numero Caja'] = df.groupby('Tienda').cumcount() + 18110459900000
            #df['Numero Caja'] = df.groupby('Color').ngroup() + int(conse)
            
            # Convertir la columna a formato de cadena
            
            
            df['Cod.Prod'] = df['Cod.Prod'].astype(int)
            df['Cod.Prod'] = df['Cod.Prod'].astype(str)
            # Borrar el guion ("-") si está en la primera posición para todos los datos de la columna 'Cod.Prod'
            df['Cod.Prod'] = df['Cod.Prod'].str.lstrip('-')
            df['UPC'] = df['UPC'].astype(int)
            df['UPC'] = df['UPC'].astype(str)
            df['UPC'] = df['UPC'].str.lstrip('-')
            
            
            
            
            # Crear una nueva tabla para hacer el resumen
            
            nuevo_df = df.groupby(['Cod.Tienda', 'Tienda', 'Color']).agg({'Cod.Tienda': 'first', 'Tienda': 'first', 'Cod.Prod': 'first',  'UPC': 'last', 'Talla': lambda x: ' - '.join(x), 'Cód.Provee': 'first', 'Emp. Pendiente': 'sum', 'Color': 'first', })
            
            nuevo_df.rename(columns={'Talla': 'Producto'}, inplace=True)
            
            # columnas Linea y Orden de compra
            nuevo_df['Linea'] = linea
            nuevo_df['Orden de Compra'] = ordenCompra
            
            
            #Numero de caja
            
            # Ordenar el DataFrame por la columna  "Color"
            #nuevo_df = nuevo_df.sort_values(by='Color')
            #Ordenar por Color
            
            nuevo_df['Color2'] = nuevo_df['Color']  # Create a copy of the "Color" column
            nuevo_df.sort_values(by='Color2', inplace=True)  # Sort the DataFrame by the "Color2" column
            nuevo_df.drop(columns=['Color2'], inplace=True)  # Drop the "Color2" column
            # Incrementar el consecutivo por cada fila
            nuevo_df['Numero Caja'] = range(conse, conse + len(nuevo_df))  # Usar la función range para generar una secuencia de valores consecutivos
            nuevo_df['Numero Caja'] = nuevo_df['Numero Caja'].astype(str)
            
            
            
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
            
            df['Talla'] = df['Producto'].str.split('/').str[4]
            
        
            linea = dfHoja3['Linea'].iloc[0]            
            ordenCompra = dfHoja3['Orden de Compra'].iloc[0]
            
           
            #Ordenar por Color
            df.sort_values(by='Color', inplace=True)
            
            
             #Columna numero de caja
            consecutivo = df['Numero Caja'].iloc[0]
            df.drop(columns='Numero Caja', inplace=True)
            
            consecutivo= int(consecutivo)
            
            
            # Convertir la columna a formato de cadena
            
            
            df['Cod.Prod'] = df['Cod.Prod'].astype(int)
            df['Cod.Prod'] = df['Cod.Prod'].astype(str)
            # Borrar el guion ("-") si está en la primera posición para todos los datos de la columna 'Cod.Prod'
            df['Cod.Prod'] = df['Cod.Prod'].str.lstrip('-')
            df['UPC'] = df['UPC'].astype(int)
            df['UPC'] = df['UPC'].astype(str)
            df['UPC'] = df['UPC'].str.lstrip('-')
            
            
            
            
            # Crear una nueva tabla para hacer el resumen
            
            nuevo_df = df.groupby(['Cod.Tienda', 'Tienda', 'Color']).agg({'Cod.Tienda': 'first', 'Tienda': 'first', 'Cod.Prod': 'first',  'UPC': 'last', 'Talla': lambda x: ' - '.join(x), 'Cód.Provee': 'first', 'Emp. Pendiente': 'sum', 'Color': 'first', })
            
            nuevo_df.rename(columns={'Talla': 'Producto'}, inplace=True)
            
            # columnas Linea y Orden de compra
            
            nuevo_df['Linea'] = linea
            nuevo_df['Orden de Compra'] = ordenCompra
            
            
            #Numero de caja
            
            # Ordenar el DataFrame por la columna  "Color"
            #nuevo_df = nuevo_df.sort_values(by='Color')
            #Ordenar por Color
            
            nuevo_df['Color2'] = nuevo_df['Color']  # Create a copy of the "Color" column
            nuevo_df.sort_values(by='Color2', inplace=True)  # Sort the DataFrame by the "Color2" column
            nuevo_df.drop(columns=['Color2'], inplace=True)  # Drop the "Color2" column
            # Incrementar el consecutivo por cada fila
            nuevo_df['Numero Caja'] = range(consecutivo, consecutivo + len(nuevo_df))  # Usar la función range para generar una secuencia de valores consecutivos
            nuevo_df['Numero Caja'] = nuevo_df['Numero Caja'].astype(str)
            
            
            excel_buffer = BytesIO()
            writer = pd.ExcelWriter(excel_buffer, engine='xlsxwriter')
            
            dfHoja1.to_excel(writer, sheet_name='Original', index=False)
            dfHoja2.to_excel(writer, sheet_name='EPIR', index=False)
            nuevo_df.to_excel(writer, sheet_name='Plano', index=False)
           
            # Guardar el archivo de Excel
            writer.close()
            # Asegurarse de que la posición del archivo esté al principio
            excel_buffer.seek(0)

            # Escribir cada DataFrame en una hoja de Excel
            
            # Devolver el archivo Excel al usuario
            # Crear la respuesta HTTP con el archivo Excel como contenido
            response = HttpResponse(excel_buffer, content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=Distribuido.xlsx'
            
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
            
            dfOriginal['UPC'] = dfOriginal['UPC'].astype(int)
            dfOriginal['UPC'] = dfOriginal['UPC'].round(0)
            dfOriginal['UPC'] = dfOriginal['UPC'].astype(str)
            dfOriginal['UPC'] = dfOriginal['UPC'].str.lstrip('-')
            
            
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
            # Incrementar el consecutivo por cada fila
            nueva_df['Numero Caja'] = range(conse, conse + len(nueva_df))  # Usar la función range para generar una secuencia de valores consecutivos
            
            # columnas Linea y Orden de compra
            nueva_df['Linea'] = linea
            nueva_df['Orden de Compra'] = ordenCompra
            
            #Convertir columnas a string para evitar el formato de excel
            nueva_df['Numero Caja'] = nueva_df['Numero Caja'].astype(str)
            nueva_df['UPC'] = nueva_df['UPC'].astype(str)
            # Eliminar los decimales
            nueva_df['UPC'] = nueva_df['UPC'].apply(lambda x: x.split('.')[0])
            nueva_df['Orden de Compra'] = nueva_df['Orden de Compra'].astype(str)
            nueva_df['Cod.Prod'] = nueva_df['Cod.Prod'].astype(str)
            # Eliminar los decimales
            nueva_df['Cod.Prod'] = nueva_df['Cod.Prod'].apply(lambda x: x.split('.')[0])
            
            
            
            
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
    words = cadena.split()  # Dividir la cadena en palabras
    if len(words) >= 4:
        color_index = 3  # El color está después del tercer espacio
        talla_index = -1  # El índice de la talla es el último elemento
        color = " ".join(words[color_index:talla_index])  # Unir las palabras para formar el color
        return color
    else:
        return None

