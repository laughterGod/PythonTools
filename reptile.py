import requests
from bs4 import BeautifulSoup


headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36'}
r = requests.get('https://movie.douban.com/cinema/nowplaying/beijing', headers=headers)
content = r.text
soup = BeautifulSoup(r.text, 'lxml')

divs = soup.find_all(class_='poster')

for div in divs:
    movies = div.find_all('img')
    # print(movies)
    for movie in movies:
        print(movie.get('alt'))
    print('------')
