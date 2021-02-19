# 𐰸𐰆𐱁𐰏𐰡𐰤! 

It is a really simple and lightweight library for scraping and downloading twitter video/gifs.

# Usage

```python
from TwitterMedia import TwitterMedia

# Create an instance
downloader = TwitterMedia()

# Fetch media through an URL
tweet = downloader.fetch_media('https://twitter.com/i/status/1353752993225650177')

# Will print the url
print(tweet['url']) 

# Will print the type, it could either be 'video' or 'gif'
# Twitter keeps gif files in mp4 format
# So if you want to convert them to actual gifs,
# you can use this key to check if the media is a gif or not
print(tweet['type'])

# You can download through the download function with the url key
# It will return a filename upon downloading
dl_filename = downloader.download(tweet['url'])

# You can also assign custom filenames to the downloaded file
# The extension is always '.mp4' for twitter media, be it video or a gif
downloader.download(tweet['url'], custom = 'custom_name')
```