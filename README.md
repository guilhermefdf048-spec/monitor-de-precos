# Monitor de Preços

Automação em Python que acompanha o preço de produtos em sites, guarda o histórico e avisa (no terminal ou no Discord) quando o preço chega ao valor que você quer pagar.

![Testes](../../actions/workflows/testes.yml/badge.svg)

## Funcionalidades

- Lê uma lista de produtos com URL, seletor CSS do preço e preço-alvo
- Entende preços no formato brasileiro (`R$ 1.299,90`) e americano (`$1,299.90`)
- Salva cada verificação num banco SQLite e mostra o histórico e o menor preço
- Envia alerta no terminal e, se configurado, num canal do Discord via webhook
- Modo contínuo, verificando a cada X minutos
- Testes automatizados com pytest, rodando no GitHub Actions a cada push

## Tecnologias

Python 3.10+ · requests · BeautifulSoup · SQLite · pytest · GitHub Actions

## Como usar

```bash
# 1. Instale as dependências
pip install -r requirements.txt

# 2. Crie sua lista de produtos a partir do exemplo
cp produtos.example.json produtos.json

# 3. Verifique os preços uma vez
python -m monitor verificar

# Verificar a cada 60 minutos
python -m monitor loop --intervalo 60

# Ver o histórico de um produto
python -m monitor historico "Livro de exemplo"
```

### Configurando os produtos

```json
{
  "produtos": [
    {
      "nome": "Livro de exemplo",
      "url": "https://books.toscrape.com/catalogue/a-light-in-the-attic_1000/index.html",
      "seletor": ".product_main .price_color",
      "preco_alvo": 60.00
    }
  ]
}
```

Para achar o `seletor`: abra a página no navegador, clique com o botão direito no preço → **Inspecionar** e use a classe ou o id do elemento (ex.: `.preco-atual`). Se o site guarda o preço numa tag `<meta itemprop="price" content="...">`, use `meta[itemprop=price]`.

### Alertas no Discord (opcional)

Crie um webhook no seu servidor (Configurações do canal → Integrações → Webhooks) e defina a variável de ambiente:

```bash
export DISCORD_WEBHOOK_URL="https://discord.com/api/webhooks/..."
```

## Estrutura

```
monitor/
├── __main__.py   # linha de comando (verificar, loop, historico)
├── config.py     # leitura do produtos.json
├── scraper.py    # download da página e extração do preço
├── price.py      # conversão de texto em preço
├── storage.py    # histórico em SQLite
├── monitor.py    # verifica um produto e decide se alerta
└── notifier.py   # alertas no terminal e Discord
tests/            # testes com páginas HTML de exemplo (não precisam de internet)
```

## Testes

```bash
pytest -v
```

## Uso responsável

Respeite os termos de uso e o `robots.txt` de cada site e use intervalos longos entre as verificações. O site do exemplo, [books.toscrape.com](https://books.toscrape.com), foi feito justamente para praticar web scraping.

## Licença

Distribuído sob a licença MIT. Veja o arquivo [LICENSE](LICENSE).
