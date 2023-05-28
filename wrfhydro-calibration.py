import os
import argparse
import pandas as pd


# Este script ejecuta el modelo WRF-Hydro Standalone con distintas configuraciones
# con el objetivo de calibrarlo. 
# Cuestiones a tener en cuenta:


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


def main():

    #parser = argparse.ArgumentParser(prog="Generar Archivos TBL,\
    #                                       generar_tbl.py")

    #parser.add_argument("mann1",
    #                    help="Numero de Manning 1: ej 0.02")
    #parser.add_argument("mann2")
    #parser.add_argument("mann3")
    #parser.add_argument("mann4")
    #parser.add_argument("mann5")
    #parser.add_argument("mann6")
    #parser.add_argument("mann7")
    #parser.add_argument("mann8")
    #parser.add_argument("mann9")
    #parser.add_argument("mann10")

    #args = parser.parse_args()



    
    # Se lee el archivo con los manning de los streamorder
    mann_data     = pd.read_csv("mann_streamorder.csv")
    refdk_values  = pd.read_csv("refdk_file.csv")
    refkdt_values = pd.read_csv("refkdt_file.csv")

    sim = 1

    # Itero sobre las columnas en el csv con los streamorder
    for column in mann_data.columns:

        mann_list = []
        # Leo los valores del archivo streamorder manning para llamar a la funcion que edita el archivo
        for k in range(10):
            mann_list.append(str(mann_data[column].iloc[k]))
        # mann_list sale del loop con lo valores necesarios para la edición

        # Edito el CHANPARM.TBL
        os.system("echo 'Se configura el archivo CHANPARM.TBL'")
        editar_chanparm(mann_list)
        #os.system('cat CHANPARM.TBL')
        os.system("echo 'Archivo CHANPARM.TBL configurado'")

        # Itero sobre los valores de refdk
        for i in range(len(refdk_values.index)):
            refdk = str(refdk_values['refdk_value'].iloc[i])
            # Itero sobre los valores de refkdt
            for j in range(len(refkdt_values.index)):
                refkdt = str(refkdt_values['refkdt_value'].iloc[j])

                os.system("echo 'Se configura el archivo GENPARM.TBL'")
                editar_genparm(refdk, refkdt)
                #os.system('cat GENPARM.TBL')
                os.system("echo 'Archivo GENPARM.TBL configurado'")

                os.system("echo 'Simulación '"+str(sim))
                os.system("echo 'Manning values: '"+str(mann_list))
                os.system("echo 'REFDK value: '"+refdk)
                os.system("echo 'REFKDT value: '"+refkdt)

                os.system("echo 'Se inicia ejecución de la simulación'")
                os.system('mpirun -np 6 ./wrf_hydro.exe')
                os.system("echo 'Simulación finalizada'")
                sim = sim + 1

    os.system("echo ' ******************************** '")
    os.system("echo ' ****** PROCESO FINALIZADO ****** '")
    os.system("echo ' ******************************** '")
    os.system("echo 'Se realizaron '"+str(sim-1)+" simulaciones")

if __name__ == "__main__":
    main()
