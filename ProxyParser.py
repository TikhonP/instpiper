#!/Users/tikhon/anaconda3/bin/python
# coding: utf-8

# In[9]:


from selenium import webdriver
from bs4 import BeautifulSoup
import csv

def proxy_parser():
    driver = webdriver.Chrome()
    driver.get('https://advanced.name/ru/freeproxy')

    soup = BeautifulSoup(driver.page_source)
    with open('proxies.csv', 'w', newline='') as csvfile:
                fieldnames = ['proxy', 'port','type']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                for proxies in soup.find_all('table'):
                    for proxy in proxies.find_all('tr'):
                        ip = proxy.text.split('\n')[2]
                        port = proxy.text.split('\n')[3]
                        tip = proxy.text.split('\n')[5]
                        writer.writerow({'proxy': ip, 'port': port,'type':tip})


if __name__=="__main__":
    proxy_parser()
