import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

session = requests.Session()
retry = Retry(connect=3, backoff_factor=1)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)



olx_url = 'https://www.olx.co.id'
base_urls = ['https://www.olx.co.id/banten_g2000004/mobil-bekas_c198?page=', 'https://www.olx.co.id/jakarta-dki_g2000007/mobil-bekas_c198?page=']
 
headers = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}
brands = ['HONDA', 'SUZUKI', 'DAIHATSU', 'NISSAN', 'TOYOTA', 'MITSUBISHI', 'MAZDA', 'KIA', 'ISUZU']
for idx, base in enumerate(base_urls):
  current_page = 1
  total_pages = 2000
  for x in range(total_pages):
    url = base + str(current_page)
    page = session.get(url, headers=headers)
    soup = BeautifulSoup(page.content, 'html.parser')
    items = soup.find_all('li', class_='_31j8e')
    datas = []
    for item in items:
      link = olx_url + item.find('a').attrs['href']
      itemPage = session.get(link, headers=headers)
      scriptSoup = BeautifulSoup(requests.get(link, headers=headers).text, 'html.parser')
      itemSoup = BeautifulSoup(itemPage.content, 'html.parser')
      if itemSoup.find('script', type='application/ld+json'):    
        data = json.loads(itemSoup.find('script', type='application/ld+json').text)
        if 'offers' in data:
          brand = data['brand']
          if(brand.upper() in brands):          
            price = data['offers']['price']
            model = data['model']
            year = data['modelDate']
            mileage = data['mileageFromOdometer']['value']
            fuel_type = data['fuelType']
            color = data['color']
            body = data['bodyType']
            transmission = data['vehicleTransmission']
            tgl = itemSoup.find_all('script', type='text/javascript')[3].text
            parameter_index = tgl.find('parameters')
            views_index = tgl.find('views')
            parameters = json.loads('{"' + tgl[parameter_index:(views_index - 2)] + "}")
            variant = parameters['parameters'][2]['formatted_value']
            created_at_index = tgl.find('created_at') + 13
            tahun_iklan = tgl[created_at_index:(created_at_index + 4)]
            bulan_iklan = tgl[(created_at_index + 5):(created_at_index + 7)]
            datas.append({
                'brand': brand,
                'model': model,
                'year': year,
                'mileage': mileage,
                'variant': variant,
                'body': body, 
                'transmission': transmission,  
                'price': price,
                'color': color,
                'fuel': fuel_type,
                'year_adv': tahun_iklan,
                'month_adv': bulan_iklan,
                'wilayah': idx
            })
    df = pd.DataFrame(datas)
    if current_page == 1 and idx == 0 : 
      df.to_csv('olx_used_cars.csv', encoding="utf-8", index=False)
    else:
      df.to_csv('olx_used_cars.csv', encoding="utf-8", mode='a', header=False, index=False)
    print(base, ' - Halaman : ', current_page, '\n')  
    current_page += 1
