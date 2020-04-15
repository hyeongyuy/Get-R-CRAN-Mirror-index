# -*- coding: utf-8 -*-
"""
Created on Tue Apr 14 16:50:57 2020
@author: hyeongyuy
"""
from bs4 import BeautifulSoup
import requests
import json
import time
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


session = requests.Session()



class recur_url(object):  
    def __init__(self, BASE_URL, sleep_time=1):
        self.BASE_URL = BASE_URL
        self.file_dict = {}
        self.skip_data_dict = {'skip_data':''}
        self.sleep_time=sleep_time
        self.start_time = time.time()
        
    def get_source(self, url):
        try:
            with requests.Session() as session:
                source = BeautifulSoup(requests.get(url).text, 'html.parser')
            
        except requests.exceptions.ConnectionError as e:
            print('ConnectionError :\n{}\n\nReconnection...'.format(e))
            time.sleep(self.sleep_time)
            with requests.Session() as session:
                retry = Retry(connect=3, backoff_factor=0.5)
                adapter = HTTPAdapter(max_retries=retry)
                session.mount('http://', adapter)
                session.mount('https://', adapter)
                source = BeautifulSoup(requests.get(url).text, 'html.parser')
        return source
            
    
    def sep_dir_file(self, base_url, file= {}):
        print('current url: {}'.format(base_url))
        skip_data = {'skip_data': ''}
        source = self.get_source(base_url)
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
                    except ValueError:
                        lib_name, date, size = [r.text.strip() for r in tr.select('tr > td') if 'right' in str(r)]
                    file[lib_name.replace('.tar.gz','')] ={'name':lib_name, 'date':date, 'size':size}
                    continue
                    
            except IndexError:
                pass
            skip_data['skip_data'] += str(tr) + '\n'
                
        return folder, file, skip_data


    def mk_hiera_dict(self,  l, value): 
        pre = value
        for i in l[::-1]:
            post = {i: pre}
            pre=post
        return post
    
    
    def rec_folder(self, url):
        subfd, subfl, skip_data = self.sep_dir_file(url)
        
        if len(subfd) ==  0:
            folderlist =[i for i in url.replace(self.BASE_URL, '').split('/') if i != '']
            if len(folderlist) == 0: 
                self.file_dict['default'] =  subfl
                self.skip_data_dict['skip_data'] +=  skip_data['skip_data']
                self.rec_folder(url)
            else:
                folder_dict = self.mk_hiera_dict(folderlist, subfl)
                self.file_dict =  dict(self.file_dict, **folder_dict)
                self.skip_data_dict['skip_data'] +=  skip_data['skip_data']
        else:
            for url in subfd.values():
                self.rec_folder(url)
                
                
    def get_result(self):
        try:
            self.rec_folder(self.BASE_URL)
        except Exception as ex: 
            print('Exception:\n{}'.format(ex))
            print('time: {} (s)'.format(time.time() - self.start_time))
            return self.file_dict, self.skip_data_dict
        print('time: {} (s)'.format(time.time() - self.start_time))
        return self.file_dict, self.skip_data_dict
    
            
connection_error_sleep_time = 3
BASE_URL = 'https://cran.biodisk.org/src/contrib/'

create_ist = recur_url(BASE_URL, connection_error_sleep_time)
result, skip_data_check = create_ist.get_result()

with open('result_data.json', 'w') as f:
    json.dump(result, f)
    
with open('skip_data.json', 'w') as f:
    json.dump(skip_data_check, f)
