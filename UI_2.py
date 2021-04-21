import numpy as np
import pandas as pd
#from pandas import DataFrame
from csv import reader
from datetime import datetime, time, timedelta
import matplotlib.pyplot as plt
#from matplotlib.pyplot import gcf, title, tight_layout, show
from tkinter import Tk, Button
from tkinter.ttk import Combobox
from tkcalendar import DateEntry
import locale
from sqlalchemy import (MetaData, Table, Column, Integer, Numeric, String,
DateTime, ForeignKey, create_engine, select)

locale.setlocale(locale.LC_ALL, "fr_FR")

metadata = MetaData()

m000 = Table('m000', metadata,
    Column('courant_id', Integer(), primary_key=True, autoincrement=True),
    Column('courant_val', String(), nullable=False),
    Column('created_on', DateTime(), default=datetime.now),
)

m001 = Table('m001', metadata,
    Column('courant_id', Integer(), primary_key=True, autoincrement=True),
    Column('courant_val', String(), nullable=False),
    Column('created_on', DateTime(), default=datetime.now),
)

def request_gen(date_i, date_f, machine):
    table = "machine"
    if machine == "OX-000":
        table = "m000"
    if machine == "OX-001":
        table = "m001"
    return (f"SELECT * FROM {table} WHERE created_on BETWEEN \"{date_i}\" AND \"{date_f}\"")

def exe():

    #determination du shift
    if shift.get() == "Total":
        date_i = datetime.combine(date_p.get_date(), time(0, 0, 0, 0))
        date_f =  date_i + timedelta(hours=24)
    if shift.get() == "1":
        date_i = datetime.combine(date_p.get_date(), time(0, 0, 0, 0))
        date_f = date_i + timedelta(hours=8)
    if shift.get() == "2":
        date_i = datetime.combine(date_p.get_date(), time(8, 0, 0, 0))
        date_f = date_i + timedelta(hours=8)    
    if shift.get() == "3":
        date_i = datetime.combine(date_p.get_date(), time(16, 0, 0, 0))
        date_f = date_i + timedelta(hours=8) 

    #request
    request = request_gen(date_i, date_f, machine.get())
    print(request)

    #exe request
    engine = create_engine('sqlite:///test2.db')
    metadata.create_all(engine)
    with engine.connect() as conn:
        rp = conn.execute(request)
        results = rp.fetchall()

    #importation de donnee
    x = []
    y = []
    for row in results:
        x.append(datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S.%f'))
        y.append(float(row[1]))

    #plot
    if graph.get() == "courant":
        x_ = []
        y_ = []
        for j in range(len(x)):
            date = x[j]
            courant = y[j]
            if  date_i <= date  and date < date_f :
                x_.append(date.strftime("%H:%M"))
                y_.append(courant)            
        df = pd.DataFrame({"Courant (A)" : y_}, index=x_)
        df.plot()
        figure = plt.gcf()
        figure.set_size_inches(12, 6)
        date_tmp = date_i.strftime("%Y-%m-%d")
        plt.title(f"Date:{date_tmp} Shift:{shift.get()} Graph:{graph.get()}")
        plt.tight_layout(w_pad=30, h_pad=30)
        plt.show()        

    if graph.get() == "courant+":
        date_list = []
        t = timedelta(minutes=0)
        while date_i + t < date_f:
            date_list.append(date_i + t)
            t += timedelta(minutes=10)
        x_ = []
        y_ = []
        min = []
        moy = []
        max = []
        for i in range(len(date_list) - 1):
            for j in range(len(x)):
                date = x[j]
                courant = y[j]            
                if  date_list[i] <= date  and date < date_list[i+1] :
                    y_.append(courant)
            np_y = np.array(y_)
            if len(np_y) == 0:
                min.append(0)
                moy.append(0)
                max.append(0)
            else:
                min.append(np_y.min())
                moy.append(np_y.mean())
                max.append(np_y.max())
            x_.append(date_list[i].strftime("%H:%M"))
            y_ = []            
        df = pd.DataFrame({"I min (A)" : min, "I moy (A)" : moy, "I max (A)" : max}, index=x_)
        df.plot()
        figure = plt.gcf()
        figure.set_size_inches(12, 6)
        date_tmp = date_i.strftime("%Y-%m-%d")
        plt.title(f"Date:{date_tmp} Shift:{shift.get()} Graph:{graph.get()}")
        plt.tight_layout(w_pad=30, h_pad=30)
        plt.show()

    if graph.get() == "consommation":
        date_list = []
        if shift.get() == "Total":
            date_i = datetime.combine(date_p.get_date(), time(0, 0, 0, 0))
            nbr_h = 24
            for i in range(nbr_h +1):
                date_list.append(date_i + timedelta(hours=i))
        else:
            date_i = datetime.combine(date_p.get_date(), time((8 * (int(shift.get()) - 1)), 0, 0, 0))
            nbr_h = 8
            for i in range(nbr_h +1):
                date_list.append(date_i + timedelta(hours=i))
        x2d = [[] for _ in range(len(date_list) - 1)]
        y2d = [[] for _ in range(len(date_list) - 1)]
        for i in range(len(date_list) - 1):
            for j in range(len(x)):
                date = x[j]
                courant = y[j]            
                if  date_list[i] <= date  and date < date_list[i+1] :
                    x2d[i].append(date)
                    y2d[i].append(courant)

        cons = []
        for i in range(nbr_h ):
            integral = 0     
            for j in range(len(x2d[i]) - 1):
                integral += y2d[i][j] * (x2d[i][j+1] - x2d[i][j]).total_seconds()
            cons.append( integral )
            # !!! conv to KWh
        x_ = []
        for _ in date_list[:-1]:
            x_.append(_.strftime("%H:%M"))
        df = pd.DataFrame({"Energie (KWh)" : cons}, index=x_)
        df.plot.bar()
        figure = plt.gcf()
        figure.set_size_inches(12, 6)
        date_tmp = date_list[0].strftime("%Y-%m-%d")
        plt.title(f"Date:{date_tmp} Shift:{shift.get()} Graph:{graph.get()}")
        plt.tight_layout(w_pad=30, h_pad=30)
        plt.show()

    if graph.get() == "temps d'arret":
        date_list = []
        t = timedelta(minutes=0)
        while date_i + t < date_f:
            date_list.append(date_i + t)
            t += timedelta(minutes=5)
        x_ = []
        y_ = []
        t_ = []
        for i in range(len(date_list) - 1):
            for j in range(len(x)):
                date = x[j]
                courant = y[j]            
                if  date_list[i] <= date  and date < date_list[i+1] :
                    y_.append(courant)
            np_y = np.array(y_)
            if len(np_y) == 0:
                t_.append(0)
            else:
                if np_y.mean() < 1:
                    t_.append(0)
                else:
                    t_.append(1)
            x_.append(date_list[i].strftime("%H:%M"))
            y_ = []
        df = pd.DataFrame({"TA" : t_}, index=x_)
        df.plot()
        figure = plt.gcf()
        figure.set_size_inches(12, 6)
        date_tmp = date_i.strftime("%Y-%m-%d")
        plt.title(f"Date:{date_tmp} Shift:{shift.get()} Graph:{graph.get()}")
        plt.tight_layout(w_pad=30, h_pad=30)
        plt.show()            

root = Tk()

date_p = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2, year=2021)
date_p.pack(padx=10, pady=10)
shift = Combobox(root, values=["Total", "1", "2" , "3"])
shift.set("Total")
shift.pack(padx=10, pady=10)
machine = Combobox(root, values=["OX-000", "OX-001", "OX-002" , "OX-003"])
machine.set("OX-000")
machine.pack(padx=10, pady=10)
graph = Combobox(root, values=["courant", "courant+", "consommation" , "temps d'arret"])
graph.set("consommation")
graph.pack(padx=10, pady=10)

Button(root, text='envoyer', command=exe).pack(padx=10, pady=10)

root.mainloop()
