'''
The MIT License (MIT)

Copyright (c) 2016 kagklis

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


# -*- coding: utf-8 -*-
from __future__ import division, print_function
import Tkinter as tk
from Tkinter import *
from tkMessageBox import *
from tkFileDialog import askdirectory
from tkSimpleDialog import askstring
from tkFileDialog import asksaveasfilename
import pyparsing
import LoadTimeseries
import Summarize
import Summarize4Clustering
import Summarize4Prediction
import Clustering
import Prediction

import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2TkAgg
# implement the default mpl key bindings
from matplotlib.backend_bases import key_press_handler
import matplotlib.pyplot as plt
import pandas as pd

global flag
flag = False

def display_error(code):
    if code == 1:
        errmsg="Please select the dataset directory!"
        showerror('Selection Error',errmsg)
    elif code == 2:
        errmsg="Please select a task!"
        showerror('Selection Error',errmsg)
    elif code == 3:
        errmsg="Length of timeseries is a required field for the Summarize task!"
        showerror('Data Field Required Error',errmsg)
    elif code == 4:
        errmsg="Length must be an integer!"
        showerror('Data Field Required Error',errmsg)
    elif code == 5:
        errmsg="Length of timeseries must be an integer greater than 0!"
        showerror('Data Field Required Error',errmsg)
    elif code == 6:
        errmsg="Please select a stock"
        showerror('Selection Error',errmsg)
    elif code == 7:
        errmsg="Number of timeseries is a required field for the Clustering task!"
        showerror('Data Field Required Error',errmsg)
    elif code == 8:
        errmsg="Number of timeseries must be an integer!"
        showerror('Data Field Violation',errmsg)
    elif code == 9:
        errmsg="Number of timeseries must be an integer greater than 0!"
        showerror('Data Field Violation',errmsg)
    elif code == 10:
        errmsg="Length of timeseries is a required field for the Clustering task!"
        showerror('Data Field Required Error',errmsg)
    elif code == 11:
        errmsg="Length of timeseries must be an integer!"
        showerror('Data Field Violation',errmsg)
    elif code == 12:
        errmsg="Length of timeseries must be an integer greater than 0!"
        showerror('Data Field Violation',errmsg)
    elif code == 13:
        errmsg="Step of prediction is a required field for the Prediction task!"
        showerror('Data Field Required Error',errmsg)
    elif code == 14:
        errmsg="Step of prediction must be an integer!"
        showerror('Data Field Violation',errmsg)
    elif code == 15:
        errmsg="Step of prediction must be an integer greater than 0!"
        showerror('Data Field Violation',errmsg)
    elif code == 16:
        errmsg="len(timeseries) + (# steps) > "+str(num_days)+"! This sum must be less or equal than the length of the timeserie for evaluation reasons"
        showerror('Data Field Violation',errmsg)
      

def display_first(_text):
    global text
    text.insert('1.0', _text)
    #text.get('1.0', END+'-1c')

def display_text(_file):
    global text
    text.delete('1.0', END)
    text_ = open(_file, 'r').read()
    text.insert('1.0',text_)

def get_dataset_path():
    global data_path;global flag
    flag = True
    data_path = askdirectory()
    label2.config(text=data_path)
    opt1.configure(state=NORMAL)

def update(option):
    global flag; global stock_list; global len_stock_list; global num_days
    if option!="Clustering":
        opt2.configure(state=NORMAL)
        num.configure(state=DISABLED)
        length.configure(state=NORMAL)
        if flag:
            stock_list, len_stock_list, num_days = LoadTimeseries.simple_scan(data_path)
            opt2['menu'].delete(0, 'end')
            for choice in stock_list:
                opt2['menu'].add_command(label=choice, command=tk._setit(stock, choice))
            label42.config(text='Length of timeseries (1 - '+str(num_days)+'):')
            
            flag = False
        
        label4.config(text='Number of timeseries:')
        if option == "Prediction":
            label4.config(text='Number of timeseries:')
            steps.configure(state=NORMAL)
        else:
            steps.configure(state=DISABLED)
 
    else:
        opt2.configure(state=DISABLED)
        num.configure(state=NORMAL)
        length.configure(state=NORMAL)
        
        stock_list, len_stock_list, num_days = LoadTimeseries.simple_scan(data_path)
        label4.config(text='Number of timeseries (1 - '+str(len_stock_list)+'):')
        label42.config(text='Length of timeseries (1 - '+str(num_days)+'):')
        steps.configure(state=DISABLED)


def onSave():
    filename = asksaveasfilename()
    if filename:
        alltext =text.get('1.0', END+'-1c')
        open(filename, 'w').write(alltext)
    
def destr():
    global canvas
    plt.clf()
    canvas.show()
    flag = False
    data_path=None
    label2.config(text='')
    label4.config(text='Number of timeseries:')
    label42.config(text = 'Length of timeseries:')
    task.set(None)
    opt1.configure(state=DISABLED)
    opt2.configure(state=DISABLED)
    stock.set(None)
    num.configure(state=NORMAL)
    num.delete(0,END)
    num.configure(state=DISABLED)
    length.configure(state=NORMAL)
    length.delete(0,END)
    length.configure(state=DISABLED)
    steps.configure(state=NORMAL)
    steps.delete(0,END)
    steps.configure(state=DISABLED)
    
    
def _Go():
    global flag;global num_days;global length;global steps;
    global num_days;global f;global sa;global plots;global curr_pos

    sel_task = task.get()
   
    if (data_path == None):
        display_error(1)
    elif (sel_task == 'None'):
        display_error(2)
    elif (sel_task == 'Summarize'):
        curr_pos = 0
        plots = []
        name = str(stock.get())
        if name != "None":
            lot = length.get()
            if lot=="":
                display_error(3)
            else:
                lot = int(lot)
                if type(lot) != int:
                    display_error(4)
                elif lot <= 0:
                    display_error(5)
                    
            if lot != "" and type(int(lot)) == int and int(lot) > 0:
                data = LoadTimeseries.read_p_timeseries(data_path, name, lot)
                original, summarized = Summarize.summarize(data)
                plt.clf()

                #yearsFmt = mdates.DateFormatter('%b %Y')
                f = plt.figure(figsize=(6,6), dpi=100, facecolor='white')
                plt.subplot(411)
                plt.title("Initial Timeserie")
                original[name].ix[original[name].index].plot(style='b')
                
##                print(summarized[name]["extremas-x"])
##                tps = []
##                tps_ind = []
##                for i in range(len(original[name])):
##                    if i in summarized[name]["extremas-x"]:
##                        tps.append(original[name][i])
##                        tps_ind.append(original[name].index[i])
##                print(tps_ind)
##                print(tps)
##                f = Series(tps, index=tps_ind).ix[tps_ind].plot(style='r',marker='o', linestyle="", markersize=7)

                plt.subplot(412)
                plt.title("Overall Timeserie Trend")
                plt.plot(summarized[name]["trend"]["x"],summarized[name]["trend"]["r"],'g')
                plt.xlim([0,lot])
                
                plt.subplot(413)
                plt.title("Turning Points")
                plt.plot(summarized[name]["extremas-x"], summarized[name]["extremas"], 'o', mfc='none', markersize=7)
                plt.xlim([0,lot])
                
                plt.subplot(414)
                plt.title("Seasonality and Cycle")
                plt.plot(summarized[name]["Ds-x"], summarized[name]["Ds"], 'r')
                plt.xlim([0,lot])
                plt.tight_layout()
                canvas.figure = f
                canvas.draw()
                
        else:
            display_error(6)
        
        
    elif sel_task == 'Clustering':
        n = num.get()
        lot = length.get()
        
        if n == "":
            display_error(7)
        else:
            n = int(n)
            if type(n) != int:
                display_error(8)
            elif n <= 0:
                display_error(9)

        if lot == "":
            display_error(10)
        else:
            lot = int(lot)
            if type(lot) != int:
                display_error(11)
            elif lot <= 0:
                display_error(12)
            
        if type(lot) == int and type(n) == int and lot > 0 and n > 0:
            curr_pos = 0
            plots = []        
            data, aDates = LoadTimeseries.read_c_timeseries(data_path, n, lot)
            original, summarized = Summarize4Clustering.summarize(data, aDates, lot)
            plt.clf()
            curr_pos = 0
            plots = Clustering.cluster(original, summarized, n)
            canvas.figure = plots[0]
            canvas.draw()
       
    elif sel_task == 'Prediction':
        curr_pos = 0
        plots = []
        name = str(stock.get())
        if name != "None":
            lot = length.get()
            sp = steps.get()
            if sp == "":
                display_error(13)
            else:
                sp = int(sp)
                if type(sp) != int:
                    display_error(14)
                elif sp <= 0:
                    display_error(15)
                
            if lot != "":
                lot = int(lot)
                if type(lot) != int:
                    display_error(11)
                elif lot <= 0:
                    display_error(12)
                
            if lot+sp > num_days:
                display_error(16)

            if type(lot) == int and lot > 0 and type(sp) == int and sp > 0 and lot+sp<=num_days:
                data = LoadTimeseries.read_p_timeseries(data_path, name, lot+sp)
                original, summarized = Summarize4Prediction.summarize(data,sp)
                orig_pre, orig_r_pre, sum_pre = Prediction.predict(original, summarized[name]["Ds"], summarized[name]["AL"], sp)
                plt.clf()
               # print(original)
                f = plt.figure(figsize=(6,6), dpi=100, facecolor='white')
                original[name].ix[original[name].index[0]:].plot(style='b', label="Actual")
                orig_pre.ix[orig_pre.index[0]:].plot(style='r',label="ARMA")
                orig_r_pre.ix[orig_r_pre.index[0]:].plot(style='purple',label="r-ARMA")
                sum_pre.ix[orig_pre.index[0]:].plot(style='g', label="Summarized")
                plt.legend(loc=2,prop={'size':10})
                canvas.figure = f
                canvas.draw()
        else:
            display_error(3)
        
root=Tk()
root.geometry('1000x700')
root.title('CAPS (developed by Vasileios Kagklis)')
root.config(bg='navy')

global plots
plots = []

########-------left side---------############
frame_1=Frame(root)
frame_1.pack(side=LEFT)
frame_1.config(bg='navy')
sub_frame_1=Frame(frame_1)
sub_frame_1.pack(side=LEFT,expand=YES,fill=X,padx=10)
sub_frame_1.config(bg='lightblue')
labelfont=('times',10,'bold')

label1=Label(sub_frame_1,text='Give dataset path:')
label1.config(bg='lightblue',font=labelfont)
label1.pack(pady=5)

data_path=None

Button(sub_frame_1,
       text='Select directory',
       command=lambda:get_dataset_path()
       ).pack()

label2=Label(sub_frame_1, text=data_path )
label2.config(bg='lightblue')
label2.pack(pady=10)

label22=Label(sub_frame_1, text = "Select stock:")
label22.config(bg='lightblue',font=labelfont)
label22.pack(pady=5)

stock =StringVar()
stock.set(None)
global opt2
opt2 = OptionMenu(sub_frame_1, stock, "")
opt2.configure(state=DISABLED)
opt2.pack()

label3=Label(sub_frame_1, text = "Select Task:")
label3.config(bg='lightblue',font=labelfont)
label3.pack(pady=5)

task =StringVar()
task.set(None)
global opt1
opt1 = OptionMenu(sub_frame_1, task, 'Summarize','Clustering', 'Prediction', command=update)
opt1.configure(state=DISABLED)
opt1.pack()

global label4
label4=Label(sub_frame_1, text = "Number of timeseries:")
label4.config(bg='lightblue',font=labelfont)
label4.pack(pady=5)

global num
num=IntVar()
num=Entry(sub_frame_1)
num.config(bg='#ffffcc')
num.configure(state=DISABLED)
num.pack()

global label42
label42=Label(sub_frame_1, text = "Length of timeseries:")
label42.config(bg='lightblue',font=labelfont)
label42.pack(pady=5)

global length
length=IntVar()
length=Entry(sub_frame_1)
length.config(bg='#ffffcc')
length.configure(state=DISABLED)
length.pack()

label5=Label(sub_frame_1, text = "Enter number of prediction steps:")
label5.config(bg='lightblue',font=labelfont)
label5.pack(pady=5)

global steps
steps=IntVar()
steps=Entry(sub_frame_1)
steps.config(bg='#ffffcc')
steps.configure(state=DISABLED)
steps.pack()

go=Button(sub_frame_1, text = "GO", command = _Go)
go.pack(padx=20,pady=10)
go.config(fg='blue',font=('arial',14,'bold'))

clear=Button(sub_frame_1, text = "RESET", command =destr)
clear.pack(padx=20,pady=10)
clear.config(fg='red',font=('arial',12,'bold'))


########---------- right side (canvas area)---------#########

frame_3=Frame(root)
frame_3.pack(side=RIGHT,expand=YES,fill=X,padx=20)
frame_3.config(bg='navy')
sub_frame_4=Frame(frame_3)
sub_frame_4.pack(side=TOP)
global f
f = plt.figure(figsize=(7,6), dpi=100, facecolor='white')
global canvas
canvas = FigureCanvasTkAgg(f, master=sub_frame_4)
f.canvas.show()
canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=1)

global curr_pos
curr_pos = 0
def on_backward_event(event):
    global curr_pos;global plots
    #print("Back: ",curr_pos)
    if len(plots) > 0:            
        if curr_pos == 0:
            curr_pos = len(plots)-1
        else:
            curr_pos -= 1
        canvas.figure = plots[curr_pos]
        canvas.draw()
    #key_press_handler(event, canvas, toolbar)

def on_forward_event(event):
    global curr_pos;global plots
    #print("Forward: ",curr_pos)
    if len(plots) > 0:            
        if curr_pos == len(plots)-1:
            curr_pos = 0
        else:
            curr_pos += 1
        
        canvas.figure = plots[curr_pos]
        canvas.draw()
    #key_press_handler(event, canvas, toolbar)


#forward = NavigationToolbar2TkAgg.forward
#backward = NavigationToolbar2TkAgg.back 

def new_backward(self, *args, **kwargs):
    s = 'backward_event'
    event = Event()
    event.foo = 100
    canvas.callbacks.process(s, event)
    #backward(self, *args, **kwargs)

def new_forward(self, *args, **kwargs):
    s = 'forward_event'
    event = Event()
    canvas.callbacks.process(s, event)
    #forward (self, *args, **kwargs)

NavigationToolbar2TkAgg.forward = new_forward
NavigationToolbar2TkAgg.back = new_backward
toolbar = NavigationToolbar2TkAgg( canvas, sub_frame_4)
toolbar.update()
canvas._tkcanvas.pack(fill=BOTH, expand=YES)
canvas.mpl_connect('forward_event', on_forward_event)
canvas.mpl_connect('backward_event', on_backward_event)

##canvas = Canvas(sub_frame_4,width=800, height=600, bg='white')
##
##canvas.pack(expand=YES, fill=BOTH)
##canvas.config(bg='#ffffcc')
##
##canvas.config(scrollregion=(0, 0, 1100, 10000))
##
##init_label=Label(canvas,text='Results shall be plotted here...')
##init_label.config(fg='blue',bg='#ffffcc',font=('times',10,'bold'))
##canvas.create_window(85,20,window=init_label)

root.mainloop()
