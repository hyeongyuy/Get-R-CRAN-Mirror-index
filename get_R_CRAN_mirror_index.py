# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 16:50:57 2020
@author: hyeongyuy
"""
from bs4 import BeautifulSoup
import requests
import json
import time

class recur_url(object):  
    def __init__(self, BASE_URL, sleep_time=1):
        self.BASE_URL = BASE_URL
        self.file_dict = {}
        self.skip_data_dict = {'file': [], 'others':[]}
        self.sleep_time=sleep_time
        self.start_time = time.time()
        
       
    def sep_dir_file(self, base_url, file= {}):
        skip_data = {'file': [], 'others':[]}
        
        source = BeautifulSoup(requests.get(base_url).text, 'html.parser')
        trs = source.find_all("table")[0].find_all('tr')
        folder = {}
        
        for i, tr in enumerate(trs):
            try:
                lib_name = tr.select('tr > td > a')[0].get('href')
                if tr.select('tr > td > img')[0].get('alt') =='[DIR]':
                    new_url = base_url+lib_name
                    folder[lib_name.replace('/', '')] = new_url
                elif'.tar.gz' in lib_name: #파일인 경우 아래와 같은 데이터로 저장
                    try:
                        date, size = [r.text.strip() for r in tr.select('tr > td') if 'right' in str(r)]
                        file[lib_name.replace('.tar.gz','')] ={'name':lib_name, 'date':date, 'size':size}
                    except ValueError:
                        #파일 형식이 다르게 저장 된 경우
                        skip_data['file'].append([r.text.strip() for r in tr.select('tr > td') if 'right' in str(r)])
                        continue
            except IndexError:
                pass
            skip_data['others'].extend(tr)
                
        return folder, file, skip_data

    def mk_hiera_dict(self,  l, value): 
        pre = value
        for i in l[::-1]:
            post = {i: pre}
            pre=post
        return post
    
    
    def rec_folder(self, url):
        time.sleep(self.sleep_time)
        subfd, subfl, skip_data = self.sep_dir_file(url)
        
        if len(subfd) ==  0:
            folderlist =[i for i in url.replace(self.BASE_URL, '').split('/') if i != '']
            if len(folderlist) == 0: 
                self.file_dict['default'] =  subfl
                self.skip_data_dict['file'].extend(skip_data['file'])
                self.skip_data_dict['others'].extend(skip_data['others'])
                self.rec_folder(url)
            else:
                folder_dict = self.mk_hiera_dict(folderlist, subfl)
                self.file_dict =  dict(self.file_dict, **folder_dict)
                self.skip_data_dict['file'].extend(skip_data['file'])
                self.skip_data_dict['others'].extend(skip_data['others'])
        else:
            for url in subfd.values():
                self.rec_folder(url)
                
                
    def get_result(self):
        try:
            self.rec_folder(self.BASE_URL)
        except Exception as ex: 
            print('Exception:\n{}'.format(ex))
            return self.file_dict, self.skip_data_dict
        print('time: {}'.format(time.time() - self.start_time))
        return self.file_dict, self.skip_data_dict
    
            
sleep_time = 0.7
BASE_URL = 'https://cran.biodisk.org/src/contrib/'

create_ist = recur_url(BASE_URL, sleep_time)
result, skip_data_check = create_ist.get_result()

with open('result_data.json', 'w') as f:
    json.dump(result, f)
    
with open('skip_data.json', 'w') as f:
    json.dump(skip_data_check, f)
