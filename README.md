<h1 align="center">🌱 Análise das Emissões de Carbono na Indústria Agrícola 🌍</h1>

---

## 📖 O que o RPA busca?

O Calbon tem como objetivo auxiliar no monitoramento das **emissões de CO₂**, por conta disso, acreditamos que uma boa maneira de manter funcionários e empresas informadas no assunto é adicionando no aplicativo uma parte de notícias sobre emissões de carbono.

> 💡 **Nota:** O rpa busca somente no [site da globo](https://ge.globo.com) devido ao fato de abranger por toda a internet demandaria uma complexidade maior principalmente por conta da diferença na estrutura de cada site. Além disso, o RPA roda **no dia 24 de cada mês** para manter notícias recentes para o usuário.

---

## 🤖 Passo a Passo do funcionamento do código

- Muda a formatação para utf-8 para garantir o funcionamento e retorno correto do RPA

```bash

def fix_encoding(text):
    if isinstance(text, bytes):
        try:
            return text.decode('utf-8')
        except UnicodeDecodeError:
            return text.decode('latin-1').encode('utf-8').decode('utf-8')
    return str(text)
```

##

- Começa definindo o padrão da busca e a URL do site
- Faz a requisição e configura para não bloquear nenhum bot
- Faz um loop de notícias e vai guardando uma a uma com os seguintes parâmetros: 

  | Campo | Descrição |
  |:-------|:-----------|
  | **Título** | Título da notícia |
  | **Link** | Link da notícia |
  | **Data** | Data de publicação da notícia (opcional) |
  | **Descrição** | Descrição d notícia (opcional) |


```bash

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

```
##
- Transforma o link da notícia para que possa ser usada como chave no redis
```bash
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
```

##
- Roda todos os processos juntos passando um termo a ser pesquisado e retorna um exemplo de notícia armazenada

```bash
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
```

>**Nota:** Todas as notícias podem ser visualizadas no aplicativo do Calbon
---



## ⚖️ Licença

Este projeto está sob a licença [**MIT**](https://choosealicense.com/licenses/mit/).  

---

<h3 align="center">✨ Desenvolvido com o objetivo de conscientizar funcionários e empresas 🌿</h3>
