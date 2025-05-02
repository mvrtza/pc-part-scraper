import undetected_chromedriver as uc
from selenium import webdriver
import numpy as np
import json
import csv


from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from pkg_resources._vendor.more_itertools.more import sliced
import time
from selenium.webdriver.support.select import Select
import pandas as pd
import urllib.parse
import os
from tqdm import tqdm


def split(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))
def motherboard():
    driver = webdriver.Firefox()
    driver.implicitly_wait(20)
    driver.get("https://motherboarddb.com/motherboards/?dt=list")
    delay = 100
    final_array = []
    i = 0
    try:
        while True:
            
            myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'page-link')))
            myElem = driver.find_element(By.ID,"table-wrapper")
            
            data = myElem.text
            data = data.split("\n")
            if(i==0):
                sliced_arr = np.array(data)[17:237]
                if("SATA" not in sliced_arr[-1]):
                    sliced_arr = np.array(data)[18:238]
                    if("SATA" not in sliced_arr[-1]):
                        sliced_arr = np.array(data)[20:240]
            else:
                sliced_arr = np.array(data)[18:238]
                if("SATA" not in sliced_arr[-1]):
                    sliced_arr = np.array(data)[17:237]
                    if("SATA" not in sliced_arr[-1]):
                        sliced_arr = np.array(data)[20:240]
                    
            sliced_arr = sliced_arr.tolist()
            
            chunks = split(sliced_arr,20)
            for item in chunks:
                
                final_array.append( {
                    'Model': item[0], 
                    'Sockets': item[1].split("Socket(s): ")[1],
                    'Ram': item[4].split("RAM: ")[1],
                })
        

            with open('data.json', 'w') as fp:
                json.dump(final_array, fp)
            time.sleep(2)
            driver.find_elements(By.CLASS_NAME,"page-link")[-1].click()
        
            i = i+1
            
        
    except TimeoutException:
        print ("Loading took too much time!")
    driver.quit()

def cpu():
    driver = webdriver.Firefox()
    driver.implicitly_wait(20)
    driver.get("https://www.videocardbenchmark.net/GPU_mega_page.html")
    delay = 100 
    final_array = []
    i = 0
    try:
        
            
            select = Select(driver.find_element(By.CLASS_NAME, "input-sm"))
            select.select_by_value('-1')
            table = driver.find_element(By.ID,"cputable")
            with open('eggs_gpu.csv', 'w', newline='') as csvfile:
                wr = csv.writer(csvfile)
                for row in table.find_elements(By.CSS_SELECTOR,'tr'):
                    wr.writerow([d.text for d in row.find_elements(By.CSS_SELECTOR,'td')])
        
    except TimeoutException:
        print ("Loading took too much time!")

    driver.quit()

arr = []
def fixdata():
    dic_temp = {}
    f = open("data/bad-data-2.csv", "r")
    i = 0
    for item in f.read().split(','):
        match i:
            case 0:
                dic_temp["Name"] = item
            case 1:
                dic_temp["Core"] = item
            case 2:
                dic_temp["Socket"] = item
            case 3:
                dic_temp["Type"] = item
                arr.append(dic_temp)
                dic_temp={}
                i = -1
        i = 1+i
    with open('data-new-2.json', 'w') as f:
        json.dump(arr, f)
    print(arr)

def motherboard_fulldata():
    with open('data/all.json') as f:
        data = json.load(f)
    driver = webdriver.Firefox()
    driver.implicitly_wait(20)
    delay = 100 # seconds
    if(not os.path.isfile("sample-1.json") or os.stat("sample-1.json").st_size == 0):
        file = open("sample-1.json","w") 
        file.write("[]") 
        file.close()
    with open('sample-1.json', 'r') as openfile:

        json_object = json.load(openfile)



    start_point = 0

    updated_arr = []
    if(json_object!=None):
        if(len(json_object)>1):
            updated_arr=json_object
            start_point = len(json_object)
        else:
            updated_arr=[]

    for i in tqdm(range(start_point,len(data["Motherboard"]["Row"]))):
        item = data["Motherboard"]["Row"][i]
        driver.get("https://motherboarddb.com/motherboards/?search="+urllib.parse.quote(item["Model"]))
        try:
            imagebase64 = ""
            network = ""
            amdcross = ""
            sli  = ""
            ddr = ""
            ram_max  = ""
            ram_channel = ""
            m2 = ""
            manifacture  = ""
            formfactor  = ""
            sata = ""
            pcie = ""
            myElem = WebDriverWait(driver, delay).until(EC.presence_of_element_located((By.CLASS_NAME, 'page-link')))
            myElem = driver.find_element(By.ID,"table-wrapper")
            elem = myElem.find_elements(By.TAG_NAME,"a")[5]
            links = elem.get_attribute('href')
            clone_item = item
            if(links!=None):
                driver.get(links)
                if(driver.find_element(By.TAG_NAME,"HTML").text!='Server Error (500)' and  "Showing 0-0 of 0" not in driver.find_element(By.CLASS_NAME,"main-content").text):
                    imagebase64 =  driver.find_elements(By.CLASS_NAME,"img-fluid")[0].screenshot_as_base64
                    for item in driver.find_elements(By.CLASS_NAME,"table-sm"):
                        if ("Mbit" in item.text):
                            network = item.text.split('\n')[1]
                        if ('Crossfire' in item.text):
                            amdcross = item.text.split('\n')[0]
                        if('SLI' in item.text):
                            sli = item.text.split('\n')[1]
                        if('Slot Protocol' in item.text):
                            ddr = item.text.split('\n')[0].split('Slot Protocol')[1]
                        if('Maximum Capacity ' in item.text):
                            ram_max = item.text.split('\n')[3].split('Maximum Capacity ')[1]
                        if('Maximum Channels ' in item.text):
                            ram_channel =  item.text.split('\n')[4].split('Maximum Channels ')[1]
                        if ('x M-Key' in item.text):
                            m2 =  item.text.split('\n')[1].split('x M-Key')[0] 
                    for item in driver.find_elements(By.CLASS_NAME,"table"):
                        if('Manufacturer ' in item.text):
                            manifacture  = item.text.split('\n')[0].split('Manufacturer ')[1]
                        if('Form Factor ' in item.text):
                            formfactor = item.text.split('\n')[3].split('Form Factor ')[1]
                    for item in driver.find_elements(By.TAG_NAME,"ul"):
                        if("SATA" in item.text):
                            sata = item.text.split('\n')
                        if("PCI-E" in item.text):
                            pcie=  item.text.split('\n')
                

                    clone_item["data"] = {
                        "Image": imagebase64,
                        "Network": network,
                        "AMD Cross": amdcross,
                        "Nvidia SLI": sli,
                        "Ram Type":ddr,
                        "Maximum Ram": ram_max,
                        "Ram Channels":ram_channel,
                        "M.2":m2,
                        "Creator":manifacture,
                        "Form Factor":formfactor,
                        "Sata":sata,
                        "PCI e":pcie
                    }
                    updated_arr.append(clone_item)
                    json_object = json.dumps(updated_arr)                
                    with open("sample-1.json", "w") as outfile:
                        outfile.write(json_object)

        except TimeoutException:
            print("MX")
with open('sample-1.json') as f:
        data = json.load(f)
arr = []
for item in data:
    clone_item = item
    clone_item["data"]["Image"] = ""
    arr.append(clone_item)
with open("sample-3.json", "w") as outfile:
    outfile.write(json.dumps(arr))
