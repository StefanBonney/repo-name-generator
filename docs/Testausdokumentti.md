# Testausdokumentti

## Yleiskuva
Projektin ydin on k-gram Markov -generaattori, jonka siirtymät tallennetaan trie-rakenteeseen. Testauksen tavoitteet:
- varmistaa **oikeellisuus** (trie rakentuu oikein, siirtymäjakaumat oikein),
- varmistaa **toistettavuus** (RNG siementäminen),
- mitata **suorituskykyä ja muistia** edustavalla datalla,
- osoittaa, että tuotokset ovat **realistisia** suhteessa oikeisiin repo-nimiin.

Testit ajetaan `pytest`illä; kattavuus raportoidaan `coverage`:lla.

Testit keskittyvät trie-tietorakenteen, generaattorin ja niiden yhteistoiminnan testaukseen. Testit on jaettu toiminnallisuuden mukaan eri tiedostoihin.

## Testikattavuus

Testikattavuus on 62%. Testaamatta jääneet osat ovat pääasiassa:
- UI ja main.py (käyttöliittymää ei testata ohjeistuksen mukaan)
- Builder-funktiot (yksinkertaisia instantiointeja)
- Filterer (ei vielä toteutettu)

## Mitä on testattu ja miten

### Trie-tietorakenne (`test_trie_simple.py`, `test_trie_realistic.py`)
- **Perusrakenteet**: Testataan että k-grammit tallentuvat oikein trieen
- **Frekvenssit**: Varmistetaan että seuraajamerkkien lukumäärät päivittyvät oikein
- **K-arvon vaihtelu**: Testataan eri k-arvoilla (2-10)
- **Realistiset nimet**: Testataan oikeilla repositorionimillä

### Generaattori (`test_generator_simple.py`)
- **Seed-säilyvyys**: Generoitu sana alkaa aina annetulla seedillä
- **Pituusrajoite**: Generoitu sana ei ylitä max_length
- **EOS-käsittely**: Generaatio pysähtyy sanan päättyessä
- **Virheellinen seed**: Käsitellään turvallisesti

### Suorituskyky (`test_trie_performance.py`)
- **Rakentamisnopeus**: 1000 nimen käsittely < 1 sekunti
- **Muistinkäyttö**: 2000 nimeä < 20 MiB
- **K-grammien jakaminen**: Varmistetaan ettei duplikaatteja

## Testisyötteet

1. **Yksinkertaiset testisanat**: "hello", "help", "helicopter"
2. **Realistiset repo-nimet**: Ladataan 500-2000 nimeä training_data.txt:stä
3. **Reunatapaukset**: 
   - Lyhyet sanat (< k)
   - Virheelliset seedit ("zz")
   - Tyhjä syöte

## Testien toistaminen
```bash
# Kaikki testit
pytest tests

# Tietty testitiedosto
pytest tests/test_trie_simple.py -v

# Testikattavuus
pytest --cov=src --cov-branch --cov-report=term-missing

# HTML-raportti
pytest --cov=src --cov-branch --cov-report=html
start .\htmlcov\index.html  # Windows
# tai
open htmlcov/index.html      # Mac/Linux
```

Testattu manuaalisesti main.py:n kautta eri parametreilla, esim:
* k-arvot: 2, 3, 4
* Seedit: "he", "hello", "web", "api"
* Pituudet: 10, 15, 20
