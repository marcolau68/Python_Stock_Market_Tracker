# All Stocks List file

import sqlite3
from bs4 import BeautifulSoup
import requests

conn = sqlite3.connect('Stock Market Tracker.db')
c = conn.cursor()

c.execute('''CREATE TABLE IF NOT EXISTS All_Stocks_Table (
                                                Code NUMBER,
                                                Name BLOB)''')
conn.commit()

# url = 'https://en.wikipedia.org/wiki/List_of_companies_listed_on_the_Hong_Kong_Stock_Exchange#Hong_Kong_Depositary_Receipts'
# source = requests.get(url).text
# soup = BeautifulSoup(source, 'lxml')
#
# for row in soup.findAll('tbody'):
#
#     for term in row.findAll('tr'):
#         raw_code = term.find('a', {'class', 'external text'})
#         code = str(raw_code).split('>')
#         list_name = term.findAll('a')
#         name = ''
#
#         if len(list_name) != 3:
#             pass
#         else:
#             #name = list_name[2].get('title')
#             name = list_name[2].text
#
#         if 1 < len(code) <= 3:
#             code = code[1].split('<')
#             code = code[0]
#             # print(code, name)
#             c.execute("INSERT INTO All_Stocks_Table (Code, Name) VALUES (:code, :name)", {'code': code, 'name': name})
#             conn.commit()
#         else:
#             pass

c.execute("SELECT * FROM All_Stocks_Table")
conn.commit()
all_stocks = c.fetchall()
conn.commit()
for i in range(len(all_stocks)):
    print(all_stocks[i])

# c.execute("DELETE FROM All_Stocks_Table")
# conn.commit()

# url = 'https://finance.yahoo.com/quote/0066.hk/'
# source = requests.get(url).text
# soup = BeautifulSoup(source, 'lxml')
#
# test = soup.findAll('div', class_='My(6px) Pos(r) smartphone_Mt(6px)')[0].find('span').text
# print(test)

# conn.close()








