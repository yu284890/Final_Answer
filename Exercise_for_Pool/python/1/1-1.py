from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import time

URL = 'https://r.gnavi.co.jp/area/aream7303/rs/'

# urlの取得
res = requests.get(URL)
soup = BeautifulSoup(res.text, 'html.parser')
shop_list = soup.find_all('a', {'class': 'style_titleLink__oiHVJ'})
data = []

#50レコード以上のurlを取得できるまでページを移動し、追加
while len(shop_list)<50:
    next_url = soup.find('ul', {'class': 'style_pages__Y9bbR'}).find_all('li')[9].find('a').get('href')
    URL = 'https://r.gnavi.co.jp'+next_url
    
    res = requests.get(URL)
    soup = BeautifulSoup(res.text, 'html.parser')
    ad_list = soup.find_all('a', {'class': 'style_titleLink__oiHVJ'})
    shop_list.extend(ad_list)

#50レコード分の情報を取得



for i in range(50):
    time.sleep(3)
    shop_url = shop_list[i].get('href')
    res_shop = requests.get(shop_url)
    item = BeautifulSoup(res_shop.content, 'html.parser')
    title = item.find('h1',{'class':'shop-info__name'}).get_text()
    #店舗名
    title = title.replace('\n','').replace('\xa0','')
    #電話番号
    phone = item.find('span',{'class':'number'}).get_text()
    region = item.find('span',{'class':'region'}).get_text()

    #
    pattern = '''(...??[都道府県])((?:旭川|伊達|石狩|盛岡|奥州|田村|南相馬|那須塩原|東村山|武蔵村山|羽村|十日町|上越|
    富山|野々市|大町|蒲郡|四日市|姫路|大和郡山|廿日市|下松|岩国|田川|大村|宮古|富良野|別府|佐伯|黒部|小諸|塩尻|玉野|
    周南)市|(?:余市|高市|[^市]{2,3}?)郡(?:玉村|大町|.{1,5}?)[町村]|(?:.{1,4}市)?[^町]{1,4}?区|.{1,7}?[市町村])(.+)'''

    result = re.match(pattern, region)
    prefecture = result.group(1) #都道府県
    municipality = result.group(2) #市区町村
    addres = result.group(3) #番地

    #span .locallyのタグがあるとき、建物もあるので、その区別
    if item.select_one('span.locality'):
        build = item.find('span',{'class':'locality'}).get_text()
    else:
        build = None
        
    #店舗のホームページを記載してある店とそうでない店の区別
    #もしあれば、そのホームページがSSLかどうかを判断
    
    if item.select_one('a.sv-of'):
        page = item.find('a', {'title': 'オフィシャルページ'}).get('href')
        if page.startswith('https'):
            SSL = True
        else:
            SSL = False

    
    else:
        page =None
        SSL = False
#データの格納
    data.append([title,phone, prefecture, municipality, addres, build, page, SSL])

#データフレーム作成
df = pd.DataFrame(data,columns =['店舗名', '電話番号', '都道府県', '区市町村', '番地', '建物名', 'URL', 'SSL'])

#csvに出力
df.to_csv('1-1.csv',encoding='cp932',index = False)
