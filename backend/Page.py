import requests
import requests_cache
import json

#Install cache for reqeusts
requests_cache.install_cache()
    
class Page:
    def __init__(self, wikipage):
        url = f'https://en.wikipedia.org/w/api.php?action=parse&format=json&page={wikipage}&redirects=1&prop=text&disableeditsection=1&formatversion=2'
        r = requests.get(url)
        json_data = r.json()
        self.title = json_data['parse']['title']
        self.html = json_data['parse']['text']
        
    def export(self):
        return {'html': self.html, 'title': self.title}
