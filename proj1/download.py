#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import numpy as np
import zipfile

import os
import io
import requests
from bs4 import BeautifulSoup as bs
import zipfile
import csv
import gzip
import pickle


class DataDownloader:
    headers = ["p1", "p36", "p37", "p2a", "weekday(p2a)", "p2b", "p6", "p7", "p8", "p9", "p10", "p11", "p12", "p13a",
               "p13b", "p13c", "p14", "p15", "p16", "p17", "p18", "p19", "p20", "p21", "p22", "p23", "p24", "p27", "p28",
               "p34", "p35", "p39", "p44", "p45a", "p47", "p48a", "p49", "p50a", "p50b", "p51", "p52", "p53", "p55a",
               "p57", "p58", "a", "b", "d", "e", "f", "g", "h", "i", "j", "k", "l", "n", "o", "p", "q", "r", "s", "t", "p5a", "region"]

    headers_type = ["U", "i", "i", "M", "i", "i", "i", "i", "i", "i", "i", "i", "i", "i",
                    "i", "i", "i", "i", "i", "i", "i", "i", "i", "i", "i", "i", "i", "i", "i",
                    "i", "i", "i", "i", "i", "i", "i", "i", "i", "i", "i", "i", "i", "i",
                    "i", "i", "f", "f", "f", "f", "f", "f", "U", "U", "U", "U", "U", "U", "U", "U", "U", "i", "i", "U", "i", "U"]

    regions = {
        "PHA": "00",
        "STC": "01",
        "JHC": "02",
        "PLK": "03",
        "ULK": "04",
        "HKK": "05",
        "JHM": "06",
        "MSK": "07",
        "OLK": "14",
        "ZLK": "15",
        "VYS": "16",
        "PAK": "17",
        "LBK": "18",
        "KVK": "19",
    }

    def __init__(self, url="https://ehw.fit.vutbr.cz/izv/", folder="data", cache_filename="data_{}.pkl.gz"):
        self.url = url
        self.folder = folder
        self.cache_filename = cache_filename
        
        self.global_dict_of_regions = dict()


    def download_data(self):
        # make folder if not exists
        if not os.path.exists(self.folder) :
            os.makedirs(self.folder)

        page = requests.get(self.url)
        soup = bs(page.content, 'html.parser')
    
        table = soup.find('table')    
        tr = soup.find_all('tr')

        for i in tr :
            btn = i.find_all('button')[-1]
            file_name = btn.get('onclick').split('\'')[1]    # get address for download
            link = self.url + file_name

            with open(file_name, 'wb') as file :
                response = requests.get(link)
                file.write(response.content)
        

    def parse_region_data(self, region):
        # check if folder exist and is not empty
        if not os.path.exists(self.folder) or len(os.listdir(self.folder)) == 0 :
            self.download_data()

        # get name of file for region 
        region_file = self.regions.get(region) + '.csv'

        list_of_collumns = [[] for _ in range(65)]
        np_arrays = []

        id_set = set()
        dict_of_region = dict()
        cnt = 0

        # iterate through all ZIP file 
        for f in os.listdir(self.folder) :
            # check if file is ZIP file 
            if not f.endswith('.zip') :
                continue

            with zipfile.ZipFile('data/' + f) as zip_file :
                with zip_file.open(region_file, 'r') as region_csv :
                    reader_csv = csv.reader(io.TextIOWrapper(region_csv, encoding='cp1250'), delimiter=';')

                    # iterate through all rows in csv file 
                    for line in reader_csv :

                        # check of duplicates 
                        if not line[0] in id_set :
                            id_set.add(line[0])
                        else :
                            continue

                        # iterate through all items in on row 
                        for index in range(0, len(line)) :
                            if not line[index] in ['', "XX"] :

                                if self.headers_type[index] == 'f' :    
                                    line[index] = line[index].replace(",", ".") # if float change "," to "."
                                    try :
                                        float(line[index])
                                    except :
                                        line[index] = -1
                                        
                                list_of_collumns[index].append(line[index])

                            else :
                                list_of_collumns[index].append(-1)
                        
                        list_of_collumns[-1].append(region)       # at the and of array shorcut for region
         
        for index in range(0, len(list_of_collumns)) :
            np_arrays.append(np.array(list_of_collumns[index], dtype=self.headers_type[index]))
            
            dict_of_region[self.headers[index]] = np_arrays[index]

        return dict_of_region


    def get_dict(self, regions=None):
        regions_data = []
        result_dict = dict()
        
        # if list 'regions' is empty put there all regions
        if regions == None :
            regions = []
            for key in self.regions :
                regions.append(key)

        # iterate through list regions[]
        for region in regions :
            # get name of gzip file
            gzip_name = self.cache_filename.format(region)
            # get path to gzip file of region
            gzip_path = self.folder + '/' + gzip_name

            if region in self.global_dict_of_regions :
                regions_data.append(self.global_dict_of_regions[region])

            elif os.path.exists(gzip_path) :
                with gzip.open(gzip_path, "rb") as f :
                    regions_data.append(pickle.load(f))

            # if region is not save in cache or in memory
            else :
                self.global_dict_of_regions[region] = self.parse_region_data(region)
                
                regions_data.append(self.global_dict_of_regions[region])

                # make cache file
                with gzip.open(gzip_path, "wb") as f :
                    pickle.dump(self.global_dict_of_regions[region], f)


        # iterate through all rows
        for row in range(len(regions_data[0])) :
            key = self.headers[row]
            cols_value = []
            cols_value.append(np.array([], dtype=self.headers_type[row]))

            # iterate through all regions in one row 
            for reg in range(len(regions_data)) :
                cols_value[0] = np.append(cols_value[0], regions_data[reg][key])

            result_dict[key] = cols_value[0]
        
        return result_dict        

if __name__ == "__main__" :
    downloader = DataDownloader()
    
    data = downloader.get_dict(["JHC", "PLK", "PAK"])
    print("Download data from regions :" , *np.unique(data["region"]))
    print("Colums : ", *data.keys())
    print("Number of accident : ", len(data["p1"]))