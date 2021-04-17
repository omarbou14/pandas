import numpy as np
import pandas as pd
from csv import reader
from datetime import datetime, time, timedelta
import matplotlib.pyplot as plt
from tkinter import Tk, Button
from tkinter.ttk import Combobox
from tkcalendar import DateEntry

def png():
    #importation de donnee
    x = []
    y = []
    with open("data.csv", newline='') as csvfile:
        spamreader = reader(csvfile, delimiter=',')

        for row in spamreader:
            x.append(datetime.strptime(row[2], '%Y-%m-%d %H:%M:%S'))
            y.append(float(row[1]))

    #determination du shift
    date_i = datetime.combine(date_p.get_date(), time(0, 0, 0, 0))
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
    print(date_i)
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
        np_y = np.array(y2d[i])
        cons.append(np_y.sum()*220/3600000)
    print(cons)
    x_ = []
    for _ in date_list[:-1]:
        x_.append(_.strftime("%H:%M"))
    df3 = pd.DataFrame({"Energie (KWh)" : cons}, index=x_)
    df3.plot.bar()
    figure = plt.gcf()
    figure.set_size_inches(12, 6)
    date_tmp = date_list[0].strftime("%Y-%m-%d")
    plt.title(f"Date:{date_tmp} Shift:{shift.get()}")
    plt.tight_layout(w_pad=30, h_pad=30)
    plt.show()

root = Tk()

date_p = DateEntry(root, width=12, background='darkblue', foreground='white', borderwidth=2, year=2021)
date_p.pack(padx=10, pady=10)
shift = Combobox(root, values=["Total", 1, 2 , 3])
shift.set("Total")
shift.pack(padx=10, pady=10)

Button(root, text='export png', command=png).pack(padx=10, pady=10)


root.mainloop()
