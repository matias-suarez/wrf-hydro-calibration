"""
Created on Mon Jun 12 16:12:45 2023

@author: msuarez
"""
####################################################################################################
####################################################################################################
####################### SE NECESITA IMPORTAR LAS SIGUIENTES LIBRERIAS ##############################
import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import glob
####################################################################################################
####################################################################################################
# Este script ejecuta el modelo WRF-Hydro Standalone con distintas configuraciones
# con el objetivo de calibrarlo. 
# Cuestiones a tener en cuenta:
# Verificar las siguientes variables:
#                                      1) path_chanparm
#                                      2) path_genparm
#                                      3) output_dir
# Verificar que esten los siguientes archivos:
#                                      1) mann_streamorder.csv
#                                      2) refdk_file.csv
#                                      3) refkdt_file.csv

# Para ejecutar, escribir en una terminal: python wrfhydro-calibration.py
####################################################################################################
####################################################################################################
# Algunas aclaraciones de cómo funciona este script

# Este codigo grafica los caudales simulados vs los observados
# Es necesario que el archivo frxst_pts_out.txt que contiene los caudales simulados
# y los archivos caudal_obs_*.xlsx con los observados esten en el mismo directorio que
# el codigo

# Ademas, la comparacion se hace en el orden en el que se incluyeron los puntos frxst
# en el preprocesamiento con los archivos observados
# Es decir que si cargamos tres puntos en el frxst por ejemplo p1, p2 y p3
# Los caudales simulados en los mismos seran comparados con los archivos
# caudal_obs_1.xlsx, caudal_obs_2.xlsx y caudal_obs_3.xlsx respectivamente

# Se sabe que el minimo de puntos en archivo frxst es 3, por lo tanto si solo nos
# interesa un punto debemos asegurarnos que este este en el primer punto del archivo.
# Es decir, al momento de configurar el preprocesamiento debemos colocar en p1 nuestro
# punto de interes y crear dos puntos "placebo" p2 y p3 que no seran utilizados
# Se debera agregar el archivo caudal_obs_1.xlsx y el mismo script detectara un solo
# archivo por lo que realizara una sola comparacion entre p1 y los datos osbervados del archivo
####################################################################################################
####################################################################################################

# Indicar directorio de salida. Ejemplo:
# output_dir = '/home/user/output/'
output_dir = '/home/msuarez/Documents/Sims_WRFHYDRO/'

######################################################################################################
######################################################################################################
###################################### DEFINICION DE FUNCIONES #######################################
######################################################################################################
######################################################################################################
def editar_chanparm(mann_list:list):
    '''
    Esta función edita el archivo CHANPARM.TBL

    Parámetros de entrada:
        - mann_list: Lista de 10 valores de Manning.
                     Cada elemento de la lista debe ser un string.
    Salida:
        - Archivo CHANPARM.TBL editado.
    '''
    
    path_chanparm = '/home/msuarez/wrf-hydro-calibration'

    # Se copia el archivo temporal
    os.system('cp -a '+path_chanparm+'/CHANPARM_Temp.TBL '+path_chanparm+'/CHANPARM.TBL')

    # Se reemplazan las variables en el namelist
    with open(path_chanparm+'/CHANPARM.TBL', 'r') as file :
        filedata = file.read()
    filedata = filedata.replace('MANN1', mann_list[0])
    filedata = filedata.replace('MANN2', mann_list[1])
    filedata = filedata.replace('MANN3', mann_list[2])
    filedata = filedata.replace('MANN4', mann_list[3])
    filedata = filedata.replace('MANN5', mann_list[4])
    filedata = filedata.replace('MANN6', mann_list[5])
    filedata = filedata.replace('MANN7', mann_list[6])
    filedata = filedata.replace('MANN8', mann_list[7])
    filedata = filedata.replace('MANN9', mann_list[8])
    filedata = filedata.replace('MANNu', mann_list[9])

    with open(path_chanparm+'/CHANPARM.TBL', 'w') as file:
        file.write(filedata)

def editar_genparm(refdk_value,refkdt_value):
    '''
    Esta función edita el archivo GENPARM.TBL

    Parámetros de entrada:
        - refdk_value: str con el valor de infiltración.
        - refkdt_value: str con el valor de tasa de infiltración del suelo.
    Salida:
        - Archivo GENPARM.TBL editado.
    '''
    
    path_genparm = '/home/msuarez/wrf-hydro-calibration'

    # Se copia el archivo temporal
    os.system('cp -a '+path_genparm+'/GENPARM_Temp.TBL '+path_genparm+'/GENPARM.TBL')

    # Se reemplazan las variables en el namelist
    with open(path_genparm+'/GENPARM.TBL', 'r') as file :
        filedata = file.read()
    filedata = filedata.replace('refdk' , refdk_value)
    filedata = filedata.replace('refkdt', refkdt_value)

    with open(path_genparm+'/GENPARM.TBL', 'w') as file:
        file.write(filedata)

######################################################################################################
######################################################################################################
#################################### FIN DEFINICION DE FUNCIONES #####################################
######################################################################################################
######################################################################################################
def main():
    
    # Se lee el archivo con los manning de los streamorder
    mann_data     = pd.read_csv("mann_streamorder.csv")
    refdk_values  = pd.read_csv("refdk_file.csv")
    refkdt_values = pd.read_csv("refkdt_file.csv")

    sim = 1

    # Aca se iran guardando las metricas estadisticas calculadas para todas las simulaciones posibles
    # Creo un dataframe vacio donde se van a ir guardando las metricas
    # de todas las simulaciones
    metricas_df = pd.DataFrame()

    # Itero sobre las columnas en el csv con los streamorder
    for column in mann_data.columns:

        mann_list = []
        # Leo los valores del archivo streamorder manning para llamar a la funcion que edita el archivo
        for k in range(10):
            mann_list.append(str(mann_data[column].iloc[k]))
        # mann_list sale del loop con lo valores necesarios para la edición

        # Edito el CHANPARM.TBL
        os.system("echo 'Se configura el archivo CHANPARM.TBL'")
        try:
            editar_chanparm(mann_list)
        except Exception as err:
            print('Ocurrio un error durante la edición del archivo CHANPARM.TBL')
            print(err)
        #os.system('cat CHANPARM.TBL')
        os.system("echo 'Archivo CHANPARM.TBL configurado'")

        # Itero sobre los valores de refdk
        for i in range(len(refdk_values.index)):
            refdk = str(refdk_values['refdk_value'].iloc[i])
            # Itero sobre los valores de refkdt
            for j in range(len(refkdt_values.index)):
                refkdt = str(refkdt_values['refkdt_value'].iloc[j])

                os.system("echo 'Se configura el archivo GENPARM.TBL'")
                try:
                    editar_genparm(refdk, refkdt)
                except Exception as err:
                    print('Ocurrio un error durante la edición del archivo GENPARM.TBL')
                    print(err)
                #os.system('cat GENPARM.TBL')
                os.system("echo 'Archivo GENPARM.TBL configurado'")

                os.system("echo 'Simulación '"+str(sim))
                os.system("echo 'Manning values: '"+str(mann_list))
                os.system("echo 'REFDK value: '"+refdk)
                os.system("echo 'REFKDT value: '"+refkdt)

                os.system("echo 'Se inicia ejecución de la simulación'")
                try:
                    os.system('mpirun -np 6 ./wrf_hydro.exe')
                except Exception as err:
                    print('Ocurrio un error durante la ejecución del modelo')
                    print(err)
                os.system("echo 'Simulación finalizada'")


                ######################################################################################################
                ######################################################################################################
                ####################### ACA COMIENZA EL ANALISIS DEL ARCHIVO FRXST_PTS_OUT.TXT #######################
                ######################################################################################################
                ######################################################################################################
                try:
                    # Se lee el archivo frxst_pts_out.txt
                    frxst_pts_out = pd.read_csv('frxst_pts_out.txt', sep=",", header=None)
                    # Se renombran las columnas
                    frxst_pts_out = frxst_pts_out.rename(columns={0: "seg", 1: "Fecha", 2:'id', 3:'Lon', 4:'Lat',
                                                                  5:'caudal[m3/s]', 6:'caudal[ft3/s]', 7:'nivel'})
                    # Se transforma la columna fecha de str a objeto datetime
                    frxst_pts_out['Fecha'] = pd.to_datetime(frxst_pts_out['Fecha'], format = '%Y-%m-%d %H:%M:%S')
                    # Paso de UTC a hora local
                    frxst_pts_out['Fecha'] = frxst_pts_out['Fecha'] - pd.Timedelta(hours=3)
                    # Se setea la columna fecha como indice
                    frxst_pts_out.index = frxst_pts_out['Fecha']
                    # Identifico los puntos del archivo frxst_pts_out
                    frxst_pts_out_dif_points = list(frxst_pts_out['id'].unique())
                except Exception as err:
                    print('Ocurrio un error durante la lectura del archivo frxst_pts_out.txt')
                    print(err)

                # CUIDADO: SE VA A COMPARAR EL PRIMER PUNTO DEL frxst_pts_out CON EL PRIMER
                # ARCHIVO CAUDAL OBSERVADO. EL SEGUNDO PUNTO CONTRA EL SEGUNDO CAUDAL OBSERVADO
                # Y ASI SUCESIVAMENTE!!!

                # RESPETAR EL ESTANDAR EN EL NOMBRE DEL ARCHIVO CON CAUDAL OBSERVADO:
                # DEBE SER caudal_obs_*.xlsx CON * UN NUMERO DE 1 A n
                # Creamos una variable lista con todos los archivos contenidos en la carpeta
                try:
                    Filelist = glob.glob('caudal_obs_*.xlsx')
                    Filelist.sort()
                except Exception as err:
                    print('Ocurrio un error durante el control de los archivos caudal_obs_*.xlsx')
                    print(err)
                # Se cargan en un diccionario los caudales simulados
                dict_df_sim = {}
                for i in range(len(Filelist)):
                    dict_df_sim[str(i)] = frxst_pts_out.loc[frxst_pts_out['id'] == frxst_pts_out_dif_points[i]]
                # En el diccionario dict_df_sim se encuentran los caudales simulados
                # Se extraen los primeros n caudales simulados en cada punto donde n es el nro de archivos observados

                ######################################################################################################
                # Se cargan en un diccionario los caudales observados
                dict_df_obs = {}
                try:
                    for i in range(len(Filelist)):
                        df_temp = pd.read_excel('caudal_obs_'+str(i+1)+'.xlsx')
                        df_temp['Fecha'] =  pd.to_datetime(df_temp['Fecha'], format='%Y-%m-%d %H:%M:%S')
                        df_temp.set_index('Fecha', inplace=True)
                        dict_df_obs[str(i)] = df_temp
                except Exception as err:
                    print('Ocurrio un error durante la lectura de los archivos caudal_obs_*.xlsx')
                    print(err)
                    
                ######################################################################################################
                # Se realizan los graficos
                # Parametros de configuracion de la figura
                fig_width = 10
                fig_height = 6

                xtick_fontsize = 10
                ytick_fontsize = 10
                xy_label_fontsize = 10
                rotation = 45
                hour_interval = 12
                myFmt = mdates.DateFormatter('%d/%m/%Y - %Hh')
                #########################################################################
                try:
                    for i in range(len(Filelist)):
                        
                        fig = plt.figure(figsize=[fig_width,fig_height])

                        ax = fig.add_subplot(111)

                        ax.plot(dict_df_sim[str(i)].index, 
                                dict_df_sim[str(i)]['caudal[m3/s]'],
                                label='Sim', marker='o')

                        ax.plot(dict_df_obs[str(i)].index, 
                                dict_df_obs[str(i)]['Caudal'],
                                 label='Obs', marker='o')

                        ax.set_ylabel('Caudal [$m^3/s$]', fontsize=xy_label_fontsize)
                        ax.set_xlabel('Fecha-Hora [ART]', fontsize=xy_label_fontsize)

                        ax.grid(alpha=.25)
                        ax.xaxis.set_major_formatter(myFmt)
                        ax.xaxis.set_major_locator(mdates.HourLocator(interval = hour_interval))

                        plt.xticks(fontsize=xtick_fontsize,rotation=rotation)
                        plt.yticks(fontsize=xtick_fontsize)

                        plt.legend()
                        plt.tight_layout()
                        plt.savefig(output_dir+'Sim1_p'+str(i)+'.png', dpi=250, facecolor='white')
                except Exception as err:
                    print('Ocurrio un error durante el plot de los caudales observados vs simulados')
                    print(err)

                try:
                    # Hago un loop sobre todos los archivos con caudales observados
                    for i in range(len(Filelist)):
                        # Creo un df temporal
                        df_temp = pd.DataFrame()
                        # Comienzo a iterar sobre el las filas del dataframe guardado en el diccionario dict_df_sim
                        for index, element in dict_df_sim[str(i)].iterrows():
                            # Intento localizar el indice en el dataframe observado
                            try:
                                a = dict_df_obs[str(i)].loc[index]
                            # Si no lo encuentro hago print del error y continuo con la siguiente vuelta
                            except KeyError as error:
                                print(f"Index Error: {error}")
                                continue
                            # Voy guardando los caudales simulados y observados en el dataframe df_temp
                            df_temp = df_temp.append({'Fecha': index,
                                                      'QSIM' :float(element[5]),
                                                      'QOBS' :float(a['Caudal'])},
                                                      ignore_index=True)
                        # Seteo el indice
                        df_temp.set_index('Fecha', inplace=True)
                        # Calculo el numero de datos que tengo
                        N = df_temp['QOBS'].count()
                        # Calculo el root mean square error
                        rmse = (( (df_temp['QOBS'] - df_temp['QSIM'])**2 ).sum()/N)**(.5)
                        # Calculo el sesgo o bias
                        bias = (df_temp['QOBS'] - df_temp['QSIM']).sum()/N
                        # Calculo el coef de correlacion de pearson
                        cc = df_temp.corr(method='pearson')['QOBS']['QSIM']
                        # Guardo las metricas en un diccionario llamado data
                        data = {'RMSE': [rmse], 'BIAS': [bias], 'CC': [cc]}
                        # Paso el diccionario anterior a un dataframe
                        temp_metricas_df = pd.DataFrame(data=data, index=['Sim'+str(i)])
                        # Concateno el resultado de cada vuelta de loop al dataframe metricas_df
                        metricas_df = pd.concat([metricas_df,temp_metricas_df])
                except Exception as err:
                    print('Ocurrio un error durante el calculo de las metricas estadisticas')
                    print(err)

                ######################################################################################################
                ######################################################################################################
                ####################### ACA FINALIZA EL ANALISIS DEL ARCHIVO FRXST_PTS_OUT.TXT #######################
                ######################################################################################################
                ######################################################################################################
                # Se copia el archivo frxst_pts_out.txt para guardarlo en el directorio de salida
                try:
                    os.system('mv frxst_pts_out.txt  '+output_dir+'frxst_pts_out_sim'+str(sim)+'.txt')
                except Exception as err:
                    print('Ocurrio un error durante la copia del archivo frxst_pts_out.txt')
                    print(err)

                sim = sim + 1

    metricas_df.to_csv(output_dir+'metricas_autocalibracion.csv')

    os.system("echo ' ******************************** '")
    os.system("echo ' ****** PROCESO FINALIZADO ****** '")
    os.system("echo ' ******************************** '")
    os.system("echo 'Se realizaron '"+str(sim-1)+" simulaciones")

if __name__ == "__main__":
    main()
