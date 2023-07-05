from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
import re
import pandas as pd
from selenium.webdriver.chrome.options import Options




options = Options()
options.add_argument('--headless')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
options.add_argument('--disable-extensions')



URL = 'https://r.gnavi.co.jp/area/jp/kods00143/rs/?sc_lid=cp_home_kods00143'

browser = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver',options=options)




data = []


def grunavi(URL):
    browser = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver',options=options)
    browser.get(URL)
    article = browser.find_elements(By.TAG_NAME,"article")
    for ob_article in article:
        if len(data)<50:
            browser = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver',options=options)
            browser.implicitly_wait(3)
            article_href = ob_article.find_element(By.CLASS_NAME,"style_titleLink__oiHVJ").get_attribute('href')
            browser.get(article_href)
            ## 各サイトの情報を取得する
            name = browser.find_element(By.ID,"info-name").text
            print(name)##処理が長すぎて、動いているかわからないため、確認用
            number = browser.find_element(By.CLASS_NAME,"number").text
            region = browser.find_element(By.CLASS_NAME,"region").text

            pattern = '''(...??[都道府県])((?:旭川|伊達|石狩|盛岡|奥州|田村|南相馬|那須塩原|東村山|武蔵村山|羽村|十日町|上越|
            富山|野々市|大町|蒲郡|四日市|姫路|大和郡山|廿日市|下松|岩国|田川|大村|宮古|富良野|別府|佐伯|黒部|小諸|塩尻|玉野|
            周南)市|(?:余市|高市|[^市]{2,3}?)郡(?:玉村|大町|.{1,5}?)[町村]|(?:.{1,4}市)?[^町]{1,4}?区|.{1,7}?[市町村])(.+)'''

            result = re.match(pattern, region)
            prefecture = result.group(1) #都道 
            municipality = result.group(2) #市区町村
            addres = result.group(3) #番地
            ## lenで建物情報の有無を確認
            if len(browser.find_elements(By.CLASS_NAME,"locality"))== 0:
                build = None
            else:
                build = browser.find_element(By.CLASS_NAME,"locality").text

            #店舗のホームページを記載してある店とそうでない店の区別
            #もしあれば、そのホームページがSSLかどうかを判断

            if len(browser.find_elements(By.CLASS_NAME,"sv-of"))== 0:
                page = None
                SSL = 'False'
            else:
                page = browser.find_element(By.CLASS_NAME,"sv-of").get_attribute('href')
                if page.startswith('https'):
                    SSL = 'True'
                else:
                    SSL = 'False'
        else:
            break


        data.append([name, number, prefecture, municipality, addres, build, page, SSL])

while len(data)<50:
    grunavi(URL)
    browser.get(URL)
    next = browser.find_element(By.CLASS_NAME,"style_pages__Y9bbR").find_elements(By.TAG_NAME,"li")[9].find_element(By.TAG_NAME,"a").get_attribute('href')
    URL = next
    
pd.DataFrame(data,columns =['店舗名', '電話番号', '都道府県', '区市町村', '番地', '建物名', 'URL', 'SSL'])

df = pd.DataFrame(data,columns =['店舗名', '電話番号', '都道府県', '区市町村', '番地', '建物名', 'URL', 'SSL'])

from sqlalchemy import create_engine, text
import sys
from sqlalchemy import *
from sqlalchemy.orm import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Float, DateTime

DATABASE = 'mysql://%s:%s@%s/%s?charset=utf8mb4' % (
    "root",  #ユーザー
    "mysql",  #パスワード    
    "mysql3",  #MySQLサーバ(http:\/\/127.0.0.1:3306)に接続し
    #dockerの場合、IPはコンテナ名
    "SCHOOL", 
)

ENGINE = create_engine(
    DATABASE,
    echo=True  #SQLをログに吐き出すフラグ
)

session = scoped_session(
    sessionmaker(
        autocommit = False,
        autoflush = False,
        bind = ENGINE
    )
)




df.to_sql('datas', ENGINE, index=False,  
           method = "multi",chunksize = 10000 ,if_exists='replace')