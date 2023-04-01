from selenium import webdriver
from time import sleep
from selenium.webdriver.common.by import By
import re
import pandas as pd
from selenium.webdriver.chrome.options import Options










URL = 'https://r.gnavi.co.jp/area/jp/kods00143/rs/?sc_lid=cp_home_kods00143'






data = []


def grunavi(URL):
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-extensions')
    browser = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver',options=options)
    sleep(3)
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

            ## メールアドレス
            
            if len(browser.find_elements(By.XPATH,'//*[@id="info-table"]/table/tbody/tr[12]/td/ul/li'))==0:
                mail = 'None'

            else:
                mail_link = browser.find_elements(By.XPATH,'//*[@id="info-table"]/table/tbody/tr[12]/td/ul/li')
                for mail_href in mail_link:
                    if len(mail_href.find_elements(By.TAG_NAME,'a'))==0:
                        mail ='None'

                    else:
                        if mail_href.find_element(By.TAG_NAME,'a').get_attribute('href').startswith('mailto'):
                            mail = mail_href.find_element(By.TAG_NAME,'a').get_attribute('href').replace('mailto:','')
                            break
                        
                        else:
                            mail = 'None'

            #number
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
            if len(browser.find_elements(By.CLASS_NAME,"go-off"))== 1:
                page = browser.find_element(By.CLASS_NAME,"go-off").get_attribute('href')
                if page.startswith('https'):
                    SSL = 'True'
                else:
                    SSL = 'False'
            
            elif len(browser.find_elements(By.CLASS_NAME,"sv-of"))==1:
                page = browser.find_element(By.CLASS_NAME,"sv-of").get_attribute('href')
                if page.startswith('https'):
                    SSL = 'True'
                else:
                    SSL = 'False'
                    
            else :
                page = None
                SSL = 'False'
            

           
            
            


        else:
            break
        

        browser.close()
        data.append([name, mail, number, prefecture, municipality, addres, build, page, SSL])

while len(data)<50:
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-extensions')
    browser = webdriver.Chrome('/usr/lib/chromium-browser/chromedriver',options=options)
    grunavi(URL)
    sleep(3)
    browser.get(URL)
    next = browser.find_element(By.CLASS_NAME,"style_pages__Y9bbR").find_elements(By.TAG_NAME,"li")[9].find_element(By.TAG_NAME,"a").get_attribute('href')
    URL = next
    browser.close()
    
    
    
pd.DataFrame(data,columns =['店舗名', 'メールアドレス', '電話番号', '都道府県', '区市町村', '番地', '建物名', 'URL', 'SSL'])

df = pd.DataFrame(data,columns =['店舗名', 'メールアドレス', '電話番号', '都道府県', '区市町村', '番地', '建物名', 'URL', 'SSL'])

df.to_csv('1-2.csv',encoding='cp932',index=False)


#sql保存用コード

# from sqlalchemy import create_engine, text
# import sys
# from sqlalchemy import *
# from sqlalchemy.orm import *
# from sqlalchemy.ext.declarative import declarative_base
# from sqlalchemy import Column, Integer, String, Float, DateTime

# DATABASE = 'mysql://%s:%s@%s/%s?charset=utf8mb4' % (
#     "root",  #ユーザー「docker」の
#     "mysql",  #パスワード「docker」で    
#     "mysql3",  #MySQLサーバ(http:\/\/127.0.0.1:3306)に接続し
#     "SCHOOL", #データベース「test_db」にアクセスします
# )

# ENGINE = create_engine(
#     DATABASE,
#     echo=True  #SQLをログに吐き出すフラグ
# )

# session = scoped_session(
#     sessionmaker(
#         autocommit = False,
#         autoflush = False,
#         bind = ENGINE
#     )
# )




# df.to_sql('datas', ENGINE, index=False,  
#            method = "multi",chunksize = 10000 ,if_exists='replace')