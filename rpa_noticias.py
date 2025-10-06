import redis
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote, urljoin
import sys
import os
from dotenv import load_dotenv

# Configuração robusta do Redis

load_dotenv()

URI = os.getenv("REDIS_URI")
r = redis.Redis.from_url(URI, decode_responses=True) 



def fix_encoding(text):
    if isinstance(text, bytes):
        try:
            return text.decode('utf-8')
        except UnicodeDecodeError:
            return text.decode('latin-1').encode('utf-8').decode('utf-8')
    return str(text)

def search_news(term):
    base_url = "https://ge.globo.com"
    search_url = f"{base_url}/busca/?q={quote(term)}"
    
    try:
        response = requests.get(search_url, timeout=30)
        response.encoding = 'utf-8'
        
        soup = BeautifulSoup(response.text, 'html.parser')
        results = []
        
        for widget in soup.select('li.widget--card.widget--info'):
            title = fix_encoding(widget.select_one('.widget--info__title').get_text(strip=True))
            link = urljoin(base_url, widget.find('a')['href'])
            date = fix_encoding(widget.select_one('.widget--info__meta').get_text(strip=True))
            desc = fix_encoding(widget.select_one('.widget--info__description').get_text(strip=True))
            
            results.append({
                'titulo': title,
                'link': link,
                'data': date,
                'descricao': desc
            })
        
        return results
    except Exception as e:
        print(f"Erro: {str(e)}", file=sys.stderr)
        return []

def save_to_redis(news_items):
    for item in news_items:
        key = f"news:{hash(item['link']) & 0xffffffff}"
        mapping = {
            'titulo': fix_encoding(item['titulo']),
            'link': fix_encoding(item['link']),
            'data': fix_encoding(item['data']),
            'descricao': fix_encoding(item['descricao'])
        }
        r.hset(key, mapping=mapping)

if __name__ == "__main__":
    term = "emissões de carbono"
    news = search_news(term)
    
    if news:
        save_to_redis(news)
        print(f"{len(news)} notícias salvas no Redis")
        
        # Teste de leitura
        sample_key = r.keys("news:*")[0]
        print("\nExemplo armazenado:")
        print(r.hgetall(sample_key))
    else:
        print("Nenhuma notícia encontrada")