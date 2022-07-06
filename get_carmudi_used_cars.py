from bs4 import BeautifulSoup
import requests
import pandas as pd
import json

"""**Pembuatan Dataset**"""

bases = ["https://www.carmudi.co.id/mobil-bekas-dijual/indonesia_banten?type=used", "https://www.carmudi.co.id/mobil-bekas-dijual/indonesia_dki-jakarta?type=used"]
bulan = {'Januari':1, 'Februari':2, 'Maret':3, 'April':4, 'Mei':5, 'Juni':6, 'Juli':7, 'Agustus':8, 'September':9,'Oktober':10, 'November':11, 'Desember':12}
brands = ['HONDA', 'SUZUKI', 'DAIHATSU', 'NISSAN', 'TOYOTA', 'MITSUBISHI', 'MAZDA', 'KIA', 'ISUZU']
for base_url in bases:
  current_page = 1
  last_page = 1

  while True:
    data = []
    if current_page == 1:
      url = base_url
    else:
      url = base_url + '&page_number=' + str(current_page) + '&page_size=25'
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    cards = soup.find_all('article', class_='listing--card')
    for card in cards:
      if(card.attrs['data-make'].upper() in brands):          
        itemPage = requests.get(card.attrs['data-url'])
        itemSoup = BeautifulSoup(itemPage.content, 'html.parser')
        section = itemSoup.find('section', class_='c-section--key-details')
        detail = itemSoup.find('script', type='application/ld+json')
        if(detail):
          body = json.loads(detail.text)[0]['bodyType']
        else:
          body = ''

        if(section):
          section_spans = section.find_all('span', class_='u-text-bold')
          color = section_spans[3].text
          tgl_tayang = itemSoup.find('section', class_='c-section--masthead').find('span', class_='u-hide@desktop').text.replace('Diperbarui pada: ','').replace('\n','').rstrip().split()
          specs = itemSoup.find('div', {'id': 'tab-specifications'}).find(text='Tipe Bahan Bakar')
          if specs:
            fuel = specs.find_next('span').contents[0]

          data.append({
            'brand': card.attrs['data-make'],
            'model': card.attrs['data-model'],
            'year': card.attrs['data-year'],
            'mileage': card.attrs['data-mileage'], 
            'variant': card.attrs['data-variant'],
            'body': body,
            'transmission': card.attrs['data-transmission'],  
            'price': card.find('div', class_='listing__price').text.replace('Rp ', '').replace('.', ''),
            'color': color,
            'fuel': fuel,
            'year_adv': tgl_tayang[2],
            'month_adv': bulan[tgl_tayang[1]]
          })    
    df = pd.DataFrame(data)
    if current_page == 1 : 
      last_page = int(soup.find('li', class_='last').find('a').attrs['data-page']) + 1
      df.to_csv('carmudi_used_cars.csv', encoding="utf-8", index=False)
    else:
      df.to_csv('carmudi_used_cars.csv', encoding="utf-8", mode='a', header=False, index=False)
    print(url, ' Halaman : ', current_page, '\n')  
    current_page += 1  

    if current_page == last_page:
      break
