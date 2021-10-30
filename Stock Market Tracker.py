'''
scrape stock prices from online OK
store data onto database by date NOPE
present data on GUI OK
graph data OK
scrape data at a certain time every day? NOPE
My favourite stocks: shows selected stocks OK
https://finance.yahoo.com/quote
'''

from bs4 import BeautifulSoup
import requests
import sqlite3
import time
import datetime
from tkinter import *
from tkinter import ttk
import textwrap
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import numpy as np
from matplotlib.ticker import (MultipleLocator, FormatStrFormatter,
                               AutoMinorLocator)

# Main window
root = Tk()
root.title('Stock Market Tracker')
root.geometry('800x800')
root.config(background='#0ca1cf')

# New Screen


def new_screen(base):
    global frame

    frame = Frame(base, width=800, height=800, bg='#0ca1cf')
    frame.pack(fill=BOTH)

    quit_frame_button = Button(frame, text='quit', command=root.destroy)
    quit_frame_button.place(relx=0, rely=0)

    back_button = Button(frame, text='back', command=frame.destroy)
    back_button.place(relx=0.95, rely=0)


# Global Indices


def world_indices(base):
    global frame
    new_screen(base)

    time = datetime.datetime.today()
    time = time.strftime('%Y-%m-%d %H:%M')

    label = Label(frame, text='Global Indices', bg='#0ca1cf', fg='black', font=('times', 24, 'bold'))
    label.place(relx=0.4, rely=0.1)

    global_indices = ttk.Treeview(frame, height=30)
    global_indices['columns'] = ('one', 'two', 'three', 'four')

    global_indices.column('#0', width=0)
    global_indices.column('one', width=250)
    global_indices.column('two', width=150)
    global_indices.column('three', width=150)
    global_indices.column('four', width=150)

    global_indices.heading('one', text='Name', anchor='w')
    global_indices.heading('two', text='Price', anchor='w')
    global_indices.heading('three', text='Change', anchor='w')
    global_indices.heading('four', text='Percentage Change', anchor='w')

    url = 'https://finance.yahoo.com/world-indices'
    source = requests.get(url).text
    soup = BeautifulSoup(source, 'lxml')

    conn = sqlite3.connect('Stock Market Tracker.db')
    c = conn.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS Global_Indices (
                                                Date BLOB, 
                                                Name BLOB, 
                                                Price_in_USD REAL, 
                                                Change REAL, 
                                                Percentage_Change REAL)''')
    conn.commit()

    row = soup.find('tbody')
    for item in row.findAll('tr'):
        name = item.find('td', {'class': 'data-col1 Ta(start) Pend(10px)'}).text
        price = item.find('td', {'class': 'data-col2 Ta(end) Pstart(20px)'}).text
        change = item.find('td', {'class': 'data-col3 Ta(end) Pstart(20px)'}).text
        percentage_change = item.find('td', {'class': 'data-col4 Ta(end) Pstart(20px)'}).text

        c.execute('''INSERT INTO Global_Indices (Date, Name, Price_in_USD, Change, Percentage_Change) VALUES 
                        (:date, :name, :price, :change, :percentage_change)''', {'date': time, 'name': name,
                                                                                 'price': price, 'change': change,
                                                                                 'percentage_change': percentage_change})
        conn.commit()

        data = [name, price, change, percentage_change]
        global_indices.insert('', 'end', text='', values=data)

    global_indices.place(relx=0.05, rely=0.2)

    conn.close()

# Search Stocks


def search_stocks_screen(base):
    global frame
    new_screen(base)

    search_stocks_label = Label(frame, text = 'Search for Stocks by Code or Name', bg='#0ca1cf', font=('times', 24, 'bold'))
    search_stocks_label.place(relx=0.28, rely=0.1)

    code_label = Label(frame, text = 'Stock Code: ', bg='#0ca1cf')
    code_label.place(relx=0.05, rely=0.25)

    code_entry = Entry(frame, bg='#0ca1cf')
    code_entry.place(relx=0.18, rely=0.245)

    name_label = Label(frame, text='Stock Name: ', bg='#0ca1cf')
    name_label.place(relx=0.55, rely=0.25)

    name_entry = Entry(frame, bg='#0ca1cf')
    name_entry.place(relx=0.68, rely=0.245)

    search_submit = Button(frame, text = 'Search', bg='#0ca1cf', command=lambda: search_stocks())
    search_submit.place(relx=0.44, rely=0.32)

    search_result = ttk.Treeview(frame, height=22)
    search_result['columns'] = ('one', 'two', 'three', 'four')

    search_result.column('#0', width=0)
    search_result.column('one', width=100)
    search_result.column('two', width=100)
    search_result.column('three', width=125)
    search_result.column('four', width=370)

    search_result.heading('one', text='Price', anchor='w')
    search_result.heading('two', text='Change', anchor='w')
    search_result.heading('three', text='Percentage Change', anchor='w')
    search_result.heading('four', text='Description', anchor='w')

    def search_stocks():
        conn = sqlite3.connect('Stock Market Tracker.db')
        c = conn.cursor()

        code = code_entry.get()
        name = name_entry.get()

        code_entry.delete(0, END)
        name_entry.delete(0, END)

        for row in search_result.get_children():
            search_result.delete(row)

        def wrap(string, length=45):
            return '\n'.join(textwrap.wrap(string, length))

        if len(name) > 0:
            c.execute("SELECT * FROM All_Stocks_Table WHERE Name = ?", (name,))
            conn.commit()
            code = c.fetchone()[0]

        count = str(code)
        filler = ''
        filler = (4 - len(count)) * str(0)

        url1 = 'https://finance.yahoo.com/quote/' + str(filler) + str(code) + '.hk/'
        source1 = requests.get(url1).text
        soup1 = BeautifulSoup(source1, 'lxml')

        price = soup1.findAll('div', class_='My(6px) Pos(r) smartphone_Mt(6px)')[0].find('span').text
        c.execute("SELECT * FROM All_Stocks_Table WHERE Code = ?", (code,))
        name = c.fetchone()[1]
        all_change = soup1.findAll('div', class_='My(6px) Pos(r) smartphone_Mt(6px)')[0].findAll('span')[1].text
        change = all_change.split('(')[0]
        percentage_change = all_change.split('(')[1].split(')')[0]

        url2 = url1 + 'profile?p=' + str(filler) + str(code) + '.HK'
        source2 = requests.get(url2).text
        soup2 = BeautifulSoup(source2, 'lxml')

        description = soup2.findAll('section', class_='quote-sub-section Mt(30px)')[0].find('p').text
        description = ' '.join(str(description).split())[:1000] + '...'

        data = [price, change, percentage_change, wrap(description)]
        search_result.insert('', 'end', text='', values=data)
        search_result.place(relx=0.05, rely=0.45)

        show_stocks_label = Label(frame)
        show_stocks_label.forget()
        show_stocks_label = Label(frame, text='%s' % (name), bg='#0ca1cf',
                                  font=('times', 18, 'bold'))
        show_stocks_label.place(relx=0.05, rely=0.38)

        conn.close()


# Modify Favourites


def modify_favorites(base):
    global frame, home_screen
    new_screen(base)

    conn = sqlite3.connect('Stock Market Tracker.db')
    c = conn.cursor()

    modify_favorites_label = Label(frame, text='Modify Favorites by Code or Name', bg='#0ca1cf',
                                font=('times', 24, 'bold'))
    modify_favorites_label.place(relx=0.28, rely=0.1)

    code_label = Label(frame, text='Stock Code: ', bg='#0ca1cf')
    code_label.place(relx=0.05, rely=0.25)

    code_entry = Entry(frame, bg='#0ca1cf')
    code_entry.place(relx=0.18, rely=0.245)

    name_label = Label(frame, text='Stock Name: ', bg='#0ca1cf')
    name_label.place(relx=0.55, rely=0.25)

    name_entry = Entry(frame, bg='#0ca1cf')
    name_entry.place(relx=0.68, rely=0.245)

    add = Button(frame, text='Add', bg='#0ca1cf', command=lambda: modify('add'))
    add.place(relx=0.26, rely=0.35)

    delete = Button(frame, text='Delete', bg='#0ca1cf', command=lambda: modify('delete'))
    delete.place(relx=0.77, rely=0.35)

    my_favorites_show = ttk.Treeview(frame, height=20)
    my_favorites_show['columns'] = ('one', 'two')

    my_favorites_show.column('#0', width=0)
    my_favorites_show.column('one', width=100)
    my_favorites_show.column('two', width=400)

    my_favorites_show.heading('one', text='Code', anchor='w')
    my_favorites_show.heading('two', text='Name', anchor='w')

    c.execute("SELECT * FROM My_Favorites")
    conn.commit()
    result = c.fetchall()
    conn.commit()

    for item in result:
        my_favorites_show.insert('', 'end', text='', values=item)

    my_favorites_show.place(relx=0.2, rely=0.5)

    my_favorites_label = Label(frame, text='My Favorites', bg='#0ca1cf',
                              font=('times', 18, 'bold'))
    my_favorites_label.place(relx=0.45, rely=0.45)

    def modify(option):
        c.execute('''CREATE TABLE IF NOT EXISTS My_Favorites (
                                                Code NUMBER, 
                                                Name BLOB) ''')
        conn.commit()

        code = code_entry.get()
        name = name_entry.get()

        code_entry.delete(0, END)
        name_entry.delete(0, END)

        if len(name) > 0:
            c.execute("SELECT * FROM All_Stocks_Table WHERE Name = ?", (name,))
            conn.commit()
            code = c.fetchone()[0]
        elif len(code) > 0:
            c.execute("SELECT * FROM All_Stocks_Table WHERE code = ?", (code,))
            conn.commit()
            name = c.fetchone()[1]

        if option == 'add':
            c.execute("SELECT * FROM My_Favorites WHERE Code = ?", (code,))
            conn.commit()
            test = c.fetchone()

            if test:
                pass
            else:
                c.execute("INSERT INTO My_Favorites (Code, Name) VALUES (?, ?)", (code, name,))
                conn.commit()
                value = code, name
                my_favorites_show.insert('', 'end', text='', values=value)

        elif option == 'delete':
            c.execute("DELETE FROM My_Favorites WHERE Code = ?", (code,))
            conn.commit()

        for row in my_favorites_show.get_children():
            my_favorites_show.delete(row)

        c.execute("SELECT * FROM My_Favorites")
        conn.commit()
        result = c.fetchall()
        conn.commit()

        for item in result:
            my_favorites_show.insert('', 'end', text='', values=item)


# Home Screen Buttons


def create_home_screen():

    home_screen = Frame(root, bg='#0ca1cf', width=800, height=800)
    home_screen.pack(fill=BOTH)

    modify_favourites = Button(home_screen, text = '''Modify
Favourites''', bg='black', fg='black', width=15, height=2, command=lambda: modify_favorites(home_screen))
    modify_favourites.place(relx=0.1, rely=0.25)

    see_all = Button(home_screen, text = '''Search
Stocks''', bg='black', fg='black', width=15, height=2, command=lambda: search_stocks_screen(home_screen))
    see_all.place(relx=0.42, rely=0.25)

    global_index = Button(home_screen, text = '''World 
Indices''', bg='black', fg='black', width=15, height=2, command=lambda: world_indices(home_screen))
    global_index.place(relx=0.72, rely=0.25)

    quit_button = Button(root, text='quit', command = lambda: root.destroy())
    quit_button.place(relx=0, rely=0)

    home_screen_label = Label(home_screen, text = 'Stock Market Tracker', bg='#0ca1cf', font = ('times', 30, 'bold'))
    home_screen_label.place(relx=0.33, rely=0.1)

    refresh_button = Button(home_screen, text = 'Refresh', command = lambda: my_favorites(home_screen))
    refresh_button.place(relx=0, rely=0.405)

    my_favorites(home_screen)

# My favorites show


def my_favorites(base):

    conn = sqlite3.connect('Stock Market Tracker.db')
    c = conn.cursor()

    c.execute("SELECT * FROM My_Favorites")
    conn.commit()
    my_favorites_list = c.fetchall()

    my_favorites_notebook_main = ttk.Notebook(base, height=400, width=745)

    for i in range(len(my_favorites_list)):

        maintabi = Frame(my_favorites_notebook_main)
        maintabi.pack()

        word_limit = int(60 / len(my_favorites_list))

        my_favorites_notebook_main.add(maintabi, text= str(my_favorites_list[i][0]) + ' ' +
                                                       ' '.join(str(my_favorites_list[i][1]).split())[:word_limit])

        my_favorites_notebook_subi = ttk.Notebook(maintabi, height=375, width=691)

        # Overview

        overviewi = Frame(my_favorites_notebook_subi)
        overviewi.pack()

        codei = my_favorites_list[i][0]
        counti = str(codei)
        filleri = (4 - len(counti)) * str(0)

        url1i = 'https://finance.yahoo.com/quote/' + str(filleri) + str(codei) + '.hk/'
        source1i = requests.get(url1i).text
        soup1i = BeautifulSoup(source1i, 'lxml')

        pricei = soup1i.findAll('div', class_='My(6px) Pos(r) smartphone_Mt(6px)')[0].find('span').text
        c.execute("SELECT * FROM All_Stocks_Table WHERE Code = ?", (codei,))
        namei = c.fetchone()[1]
        all_changei = soup1i.findAll('div', class_='My(6px) Pos(r) smartphone_Mt(6px)')[0].findAll('span')[1].text
        changei = all_changei.split('(')[0]
        percentage_changei = all_changei.split('(')[1].split(')')[0]
        volumei = soup1i.findAll('tr')[6].findAll('td')[1].find('span').text
        dividendi = soup1i.findAll('tr')[13].findAll('td')[1].text

        stock_name = Label(overviewi, text='%s - %s' % (my_favorites_list[i][1], my_favorites_list[i][0]),
                           font=('times', 16))
        stock_name.place(relx=0, rely=0)

        stock_price = Label(overviewi, text='Current Price is: %s' % pricei, font=('times', 14))
        stock_price.place(relx=0, rely=0.1)

        stock_change = Label(overviewi, text='Price Change is: %s' % changei, font=('times', 14))
        stock_change.place(relx=0, rely=0.2)

        stock_percentage_change = Label(overviewi, text='Percentage Price Change is: %s' % percentage_changei,
                                        font=('times', 14))
        stock_percentage_change.place(relx=0, rely=0.3)

        stock_volume = Label(overviewi, text='Volume is: %s' % volumei,
                                        font=('times', 14))
        stock_volume.place(relx=0, rely=0.4)

        stock_dividend = Label(overviewi, text='Dividend is: %s' % dividendi,
                             font=('times', 14))
        stock_dividend.place(relx=0, rely=0.5)

        #  Monthly trend

        month_trendi = Frame(my_favorites_notebook_subi)
        month_trendi.pack()

        url3i = url1i + 'history?p=' + str(filleri) + str(codei) + '.HK'
        source3i = requests.get(url3i).text
        soup3i = BeautifulSoup(source3i, 'lxml')

        month_pricei = []
        month_daysi = []
        a = 0

        for item in soup3i.findAll('tr', {'class': 'BdT Bdc($seperatorColor) Ta(end) Fz(s) Whs(nw)'}):
            data = item.findAll('td', {'class': 'Py(10px) Pstart(10px)'})
            if len(month_pricei) <= 30 and len(data) == 6:
                if data[0].text == '-':
                    pass
                else:
                    month_pricei.append(float(data[0].text))
                    a += 1
                    month_daysi.append(a)

                if data[4].text == '-':
                    pass
                else:
                    month_pricei.append(float(data[4].text))
                    a += 1
                    month_daysi.append(a)

        month_pricei.reverse()

        scale = sum(month_pricei) / a / 60

        month_pricei = np.array(month_pricei)
        month_daysi = np.array(month_daysi)

        fig = Figure(figsize=(8, 3))
        month_graph = fig.add_subplot(111)
        month_graph.scatter(month_daysi, month_pricei, color='red')
        month_graph.plot(month_daysi, month_pricei, color='blue')

        month_graph.set_ylabel("Price", fontsize=12)
        month_graph.set_xlabel("Days", fontsize=12)
        month_graph.yaxis.set_major_locator(MultipleLocator(scale))

        canvas = FigureCanvasTkAgg(fig, month_trendi)
        canvas.get_tk_widget().pack(fill=BOTH)
        canvas.draw()

        #  Yearly trend

        year_trendi = Frame(my_favorites_notebook_subi)
        year_trendi.pack()

        year_pricei = []
        year_daysi = []
        a = 0

        for item in soup3i.findAll('tr', {'class': 'BdT Bdc($seperatorColor) Ta(end) Fz(s) Whs(nw)'}):
            data = item.findAll('td', {'class': 'Py(10px) Pstart(10px)'})

            if len(data) == 6:
                if data[0].text == '-':
                    pass
                else:
                    year_pricei.append(float(data[0].text))
                    a += 1
                    year_daysi.append(a)

                if data[4].text == '-':
                    pass
                else:
                    year_pricei.append(float(data[4].text))
                    a += 1
                    year_daysi.append(a)

        year_pricei.reverse()

        scale = sum(year_pricei) / a / 70

        year_pricei = np.array(year_pricei)
        year_daysi = np.array(year_daysi)

        fig = Figure(figsize=(8, 3))
        year_graph = fig.add_subplot(111)
        year_graph.scatter(year_daysi, year_pricei, color='red')
        year_graph.plot(year_daysi, year_pricei, color='blue')

        year_graph.set_ylabel("Price", fontsize=12)
        year_graph.set_xlabel("Days", fontsize=12)
        year_graph.yaxis.set_major_locator(MultipleLocator(scale))

        canvas = FigureCanvasTkAgg(fig, year_trendi)
        canvas.get_tk_widget().pack(fill=BOTH)
        canvas.draw()

        # Bigger Notebook

        my_favorites_notebook_subi.add(overviewi, text='Overview')
        my_favorites_notebook_subi.add(month_trendi, text='Monthly Trend')
        my_favorites_notebook_subi.add(year_trendi, text='Yearly Trend')

        my_favorites_notebook_subi.pack()

    my_favorites_notebook_main.place(relx=0, rely=0.43)
    conn.close()

# Welcome Screen


def create_welcome():
    welcome_screen = Frame(root, bg = '#0ca1cf', width = 800, height = 800)
    welcome_screen.place(relx = 0.5, rely = 0.5, anchor = 'center')

    welcome_sign = Label(welcome_screen, text = 'Welcome ', bg = '#0ca1cf', font = ('Times', 48, 'bold'))
    welcome_sign.place(relx = 0.5, rely = 0.3, anchor = 'center')

    marco_sign = Label(welcome_screen, text = 'Marco ', bg = '#0ca1cf', font = ('Times', 48, 'bold'))
    marco_sign.place(relx = 0.5, rely = 0.6, anchor = 'center')

    def destroy_welcome(event):
        time1 = time.time()

        create_home_screen()
        welcome_screen.destroy()

        time2 = time.time()

        print('That took: ' + str(round((time2 - time1), 1)), 'seconds')

    welcome_screen.bind('<Button-1>', destroy_welcome)
    welcome_sign.bind('<Button-1>', destroy_welcome)
    marco_sign.bind('<Button-1>', destroy_welcome)


create_welcome()

root.mainloop()
