# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 16:50:57 2020

@author: hyeongyu_yeo1

"""


from bs4 import BeautifulSoup
import requests
import json

BASE_URL = 'https://cran.biodisk.org/src/contrib/'


def sep_dir_file(base_url, file= {}):
    source = BeautifulSoup(requests.get(base_url).text, 'html.parser')
    trs = source.find_all("table")[0].find_all('tr')
    folder = {}
    for i, tr in enumerate(trs):
        try:
            lib_name = tr.select('tr > td > a')[0].get('href')
            if tr.select('tr > td > img')[0].get('alt') =='[DIR]':
                new_url = base_url+lib_name
                folder[lib_name.replace('/', '')] = new_url
            else:
                if '.tar.gz' in lib_name:
                    file[lib_name.replace('.tar.gz','')] ={'name':lib_name, 'date':date, 'size':size, 'type': 'file', 'sub_dir' : '-'}
        except IndexError:
            print(tr)
    return folder, file


class recur_url(object):  
    def __init__(self, BASE_URL):
        self.BASE_URL = BASE_URL
        self.file_dict = {}
        
    def mk_hiera_dict(self,  l, value): 
        temp = [value]
        for i in l[::-1]:
            temp.append({i: temp[-1]})
        return temp[-1]    
    
    def rec_folder(self, url):
        subfd, subfl = sep_dir_file(url)
        
        if len(subfd) ==  0:
            folderlist = url.replace(self.BASE_URL, '').split('/')[:-1]
            folder_dict = self.mk_hiera_dict(folderlist, subfl)
        
            self.file_dict =  dict(self.file_dict, **folder_dict)
            
        else:
            for url in subfd.values():
                self.rec_folder(url)
                
    def get_folder_dict(self):
        self.rec_folder(self.BASE_URL)
        return self.file_dict
    
create_ist = recur_url('https://cran.biodisk.org/src/contrib/')
result = create_ist.get_folder_dict()

with open('data.json', 'w') as f:
    json.dump(result, f)
    
    
    
    
