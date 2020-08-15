import requests
import requests_cache
import json

requests_cache.install_cache()
    
class Page:

    def __init__(self, wikipage, target=None):
        url = 'https://en.wikipedia.org/w/api.php?action=parse&format=json&page='+wikipage+'&redirects=1&prop=text&disableeditsection=1&formatversion=2'
        r = requests.get(url)
        print('From Cache: ', r.from_cache)
        json_data = r.json()
        self.title = json_data['parse']['title']
        self.target = target
        #self.html = top+self.title+middle+json_data['parse']['text']+bottom
        self.html = json_data['parse']['text']
        
    def export(self):
        return {'html': self.html, 'title': self.title, 'target': self.target}
        





    