import requests
from bs4 import BeautifulSoup
import csv
url='put website link'
response=requests.get(url)
html_text=response.text
soup=BeautifulSoup(html_text,'html.parser')
class mum:
    def _init_(self, titile,link):
        self.title=title
        self.link=link
    def to_csv(self):
        return[self.title,self.link]
    @staticmethod
    def csv_title(self):
        return['title','link']

# get lists
items=soup.findAll('span',{'class':'lbx'})
mum=[]
for item in items:
  title=item.find_all('a').text #title
  link=item.find_all('a').get('href') #link
  m=mum(title,link)
  mums.append(m)
file_name=guizhou.csv
with open(file_name.'w',newline='') as f:
    pen=csv.writer(f)
    pen.writerow(mun.csv_title())
    for m in mums:
        pen.writerow(v.to_csv())
