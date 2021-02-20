import requests
from pathlib import Path
from bs4 import BeautifulSoup
from shutil import copyfileobj
from urllib.parse import quote as qt

HEADERS = {
    'authority': 'twittervideodownloader.com',
    'content-type': 'application/x-www-form-urlencoded',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_1_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36',
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'
}


class TwitterMediaContent:
    url = None
    type = None

    def __init__(self, url, type):
        self.url = url
        self.type = type

    def __getitem__(self, name):
        if name == 'url':
            return self.url

        if name == 'type':
            return self.type


class TwitterMedia:
    def __init__(self, use_print=False):
        self._token = ''
        self._is_token_generated = False
        self._use_print = use_print
        self.main_page = 'https://twittervideodownloader.com/'
        self.download_page = 'https://twittervideodownloader.com/download'

    def browser(self, post, url, **kwargs):
        with requests.Session() as session:
            if post:
                return session.post(url, headers=kwargs['headers'], cookies=kwargs['cookies'], data=kwargs['rawdata'])
            else:
                return session.get(url, stream=True)

    def download(self, url, custom=None):
        filename = (url.split('/')[-1]).split('?')[0]
        if custom:
            filename = f'{custom}.mp4'

        with self.browser(0, url) as data:
            with open(filename, 'wb') as video:
                copyfileobj(data.raw, video)

        return filename

    def fetch_media(self, url):
        self._generate_token()

        html = self.browser(
            1,
            self.download_page,
            cookies={'csrftoken': self._token},
            rawdata=f'csrfmiddlewaretoken={self._token}&tweet={qt(url)}&submit=',
            headers={
                **HEADERS,
                'referer': self.main_page
            }
        )

        content = html.content

        if 'Download Video' not in str(content):
            self._print('Deleting the csrf token!')
            if Path('csrftoken').is_file():
                Path('csrftoken').unlink()
            return

        urls, res = [], []

        soup = BeautifulSoup(content, 'html.parser')
        for url in soup.select('a.expanded.button.small.float-right'):
            urls.append(url['href'])
            
        if len(urls) == 1:
            return TwitterMediaContent(urls[0], 'gif')
        else:
            for url in urls:
                resolution = url.split('/')[7]
                res.append(int(resolution.split('x')[1]))
            return TwitterMediaContent(urls[res.index(max(res))], 'video')

    def _generate_token(self):
        # FIXME: Should we instead look for self.token only?
        if self._is_token_generated:
            return

        if Path('csrftoken').exists():
            with open('csrftoken', 'r') as f:
                self._token = f.readline()

            self._print('Loaded the csrf token from cache.\n')
        else:
            session = self.browser(0, self.main_page)
            self._print(session.cookies)
            csrftoken = session.cookies['csrftoken']

            self._token = csrftoken
            with open('csrftoken', 'w') as f:
                f.write(csrftoken)

            self._print('Created a new csrf token!\n')

        self._is_token_generated = True

    def _print(self, *args):
        if self._use_print:
            print(*args)