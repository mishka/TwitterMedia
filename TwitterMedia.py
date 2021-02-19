import requests
from pathlib import Path
from bs4 import BeautifulSoup
from shutil import copyfileobj
from urllib.parse import quote as qt

class TwitterMedia:
    def __init__(self):
        self.token = ''
        self.switch = 0 # check if the token has been generated before
        self.main_page = 'https://twittervideodownloader.com/'
        self.download_page = 'https://twittervideodownloader.com/download'
        
    def browser(self, post, url, **kwargs):
        with requests.Session() as session:
            if post:
                return session.post(url, headers=kwargs['headers'], cookies=kwargs['cookies'], data=kwargs['rawdata'])
            else:
                return session.get(url, stream = True)

    def download(self, url, custom = None):
        orj_name = (url.split('/')[-1]).split('?')[0]
        filename = f'{custom}.mp4' if custom else orj_name

        with self.browser(0, url) as data:
            with open(filename, 'wb') as video:
                copyfileobj(data.raw, video)
        return filename

    def generate_token(self):
        self.switch = 1
        if Path('csrftoken').exists():
            with open('csrftoken', 'r') as f:
                self.token = f.readline()
            print('Loaded the csrf token from cache.\n')
        else:
            session = self.browser(0, self.main_page)
            print(session.cookies)
            csrftoken = session.cookies['csrftoken']
            
            self.token = csrftoken
            with open('csrftoken', 'w') as f:
                f.write(csrftoken)
            print('Created a new csrf token!\n')

    def fetch_media(self, url):
        if not self.switch:
            self.generate_token()
        
        html = self.browser(
            1, self.download_page,
            cookies = {'csrftoken': self.token},
            rawdata = f'csrfmiddlewaretoken={self.token}&tweet={qt(url)}&submit=',
            headers = {'referer': self.main_page,
                    'authority' : 'twittervideodownloader.com',
                    'content-type': 'application/x-www-form-urlencoded',
                    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
                    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
            }
        )

        if 'Download Video' not in str(html.content):
            print('Deleting the csrf token!')
            if Path('csrftoken').is_file():
                Path('csrftoken').unlink()
            return

        urls, res = [], []
        soup = BeautifulSoup(html.content, 'html.parser')
        for url in soup.find_all('a', {'class': 'expanded button small float-right'}):
            urls.append(url['href'])

        if len(urls) == 1:
            type = 'gif' if 'tweet_video' in urls[0] else 'video'
            return {'url': urls[0], 'type': type}
        else:
            for url in urls:
                resolution = url.split('/')[7]
                res.append(int(resolution.split('x')[1]))
            return {'url': urls[res.index(max(res))], 'type': 'video'}