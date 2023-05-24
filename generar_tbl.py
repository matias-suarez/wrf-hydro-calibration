import os
import argparse
import pandas as pd

def editar_tbl(mann_list:list):
    
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


#    mann_list = ['1','2','3','4','5','6','7','88','89','2142']
    
    data = pd.read_csv("mann_streamorder.csv")
    for column in data.columns:
        mann_list = []
        for k in range(10):
            mann_list.append(str(data[column].iloc[k]))


    editar_tbl(mann_list)


if __name__ == "__main__":
    main()

