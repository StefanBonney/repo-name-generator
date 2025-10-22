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

Testikattavuus on 62%. Testeistä 43/43 läpäisevät.
Testaamatta jääneet osat ovat pääasiassa:
- UI ja main.py (käyttöliittymää ei testata ohjeistuksen mukaan)
- Builder-funktiot (yksinkertaisia instantiointeja)
- Data-handler (minimaalinen toteutus)

## Mitä on yksikkötestattu ja miten

### Perus Trie

- **Testitiedostot:** `test_trie_1_basic.py`, `test_trie_3_quality.py`
- **Tarkistettavat asiat:**
    - **Rakenteet & Frekvenssit:** Varmistetaan, että $k$-grammien polut ja `next_char_counts` (seuraavien merkkien laskurit) päivittyvät oikein (esim. sanoista ”hello”, ”help”).
    - **Terminaalit:** Tarkistetaan, että sekvenssin viimeinen $k$-grammi on terminaali (sillä ei ole seuraajia).
    - **Realistiset kuviot:** Varmistetaan, että esim. repo-tyyliset nimet (`react-router`, `vue-cli`, ...) muodostavat odotetut siirtymät (esim. ”rea” $\to$ 'c').
    - **Erotin-kuviot:** Tarkistetaan, että ennen viivaa (`-`) tai alaviivaa (`_`) esiintyvät $k$-grammit oppivat oikeat siirtymät ja frekvenssit.
    - **K-arvon vaihtelu**: Testataan eri k-arvoilla (2-10)

### EOS Trie (End-of-Sequence)

- **Testitiedostot:** `test_trie_4_eos.py`, `test_trie_5_eos_quality.py`
- **Tarkistettavat asiat:**
    - **EOS-merkintä:** Varmistetaan, että terminaali $k$-grammit saavat EOS-seuraajan ja laskurit kertyvät useista eri sanoista.
    - **Pariteetti:** Tarkistetaan, että ei-terminaaliset siirtymät säilyvät normaaleina EOS-lisäyksen ohella.
    - **Laatusuhteet:** Hyphen-siirtymien osuus pysyy terveellä välillä; terminaali $k$-grammien EOS-peitto on riittävä (varhaisen lopetuksen tuki).

### Perus Generaattori

* **Testitiedosto:** `test_generator_1_basic.py`, `test_generator_3_quality.py`
* **Tarkistettavat asiat:**
    * **Siemenen säilyvyys:** Tuloksen on aina alettava annetulla siemenellä.
    * **Pituusraja:** Tuloksen pituus on $\le$ `max_length`.
    * **Tuntematon konteksti:** Turvallinen pysäytys — palauttaa alkusanan tai ei jatka.
    * **Batch-uniikkius:** (i) Koulutusdatan duplikaatit suodatetaan pois, (ii) erä ei sisällä sisäisiä duplikaatteja, (iii) `max-attempts` katkaisee silmukan.
    * **Puhdistuksen pariteetti:** Alkusana, joka sisältää erottimen (`/` tai `.`), ei voi jatkua $\to$ palauttaa siemenen sellaisenaan.

### Kokeellinen Generaattori

* **Testitiedostot:** `test_generator_4_experimental.py`, `test_generator_5_experimental_quality.py`
* **Tarkistettavat asiat:**
    * **Tehdasreitti:** Kokeelliset liput (`temperature≠1.0` tai `use_eos_continuation_search`) ohjaavat `GeneratorExperimental`-luokkaan.
    * **Duplikaattisuodatus:** Täsmäkopiot koulutusdatasta hylätään erässä.
    * **Temperature-skaalaus:** Erittäin matala lämpötila suosii todennäköisintä jatkoa (empeeriaalinen raja $\ge 80\%$).
    * **Diversiteetti:** Korkeampi lämpötila $\to$ suurempi Levenshtein-etäisyys otosten välillä.
    * **Pituuden käyttöaste:** Keskipituus hyödyntää tavoitteesta järkevän osuuden; "cap-hit" -osuus pysyy hallinnassa.
    * **Laatu:**  Erikoismerkit heijastuvat, novellius koulutusdataan, hyphen-konventiot, tasapaino uutuuden ja samankaltaisuuden välillä

### Suorituskyky ja Muisti

* **Testitiedostot:** `tests/trie/test_trie_2_performance.py`, `tests/generator/test_generator_2_performance.py`
* **Tarkistettavat asiat:**
    * **Trie-rakennusaika:** 1000 rivin rakentaminen $< 1 \text{ s}$ (paikallinen raja).
    * **Generointiviive:** $N$ nimen tuotto pysyy asetetun aikarajan alla.
    * **Muistinkäyttö:** `tracemalloc`-mittaus pysyy budjetissa (parametrisoitu).

### UI

* **Tiedosto:** `tests/ui/test_ui.py`
* **Tarkistettavat asiat:**
    * **Oletukset:** **Enter** $\to$ oletusarvot palautuvat oikein.
    * **Mukautetut arvot:** Yksilölliset syötteet palautuvat muuttumattomina.
    * **Validointi:** Virheellinen kokonaisluku hylätään, virheilmoitus tulostuu ja uusi arvo hyväksytään.

## Yksikkötestien toistaminen
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

## Notebook-pohjainen testaus ja analyysi (Logipohjainen)

Tämä osio kuvaa prosessin laadun ja suorituskyvyn analysoimiseksi suoraan generaattorin tuottamista JSON-logeista.

- Logipohjaisen testauksen ensisijainen tavoite on suorittaa ei-yksikkötestaavaa laatu- ja suorituskykyanalyysiä generaattorin JSON-logeista (esim. `logs/04-10-2025/`, `logs/2025-10-12/`).
- Käytetään regressioseurantaan ja parametritason vertailuun eri konfiguraatioiden välillä.

Datan lataus & Versiointi

- Luetaan kaikki `generator_debug_*.json` -tiedostot tietyn snapshot-kansion sisältä.
- Notebook on sidottu kyseiseen päivämäärään, mikä takaa toistettavuuden.

Logeista lasketaan seuraavat mittarit suorituskyvyn ja laadun arvioimiseksi:

- Laatu, $n$-gram F1 
- Levenshtein (otosten välillä), 
- pituuden käyttö (`avg_length`/`max_length`) 
- hyphen/underscore-ratio
- konsonantti/vokaali-suhde 
- delimiter-artefaktit (loppuu `-` tai `_`, lyhyet segmentit)
- Suorituskyky, `generation_time_ms` (generoinnin kokonaisaika)

Ryhmittely & Ranking

- Aggregointi suoritetaan konfiguraation mukaan (K, `temperature`, EOS, generaattorityyppi, trim v1/v2, jatkohaku + yritysrajat).
- Lasketaan komposiittipisteytys (painotettu F1, pituus, Levenshtein, hyphen, ym.).
- Listataan top-konfiguraatiot suositeltavia asetuksia varten.

Manuaalinen Tarkistus

- Näytesanat top-ryhmistä tarkistetaan silmämääräisesti.
- Tarkistuskohteet: siemenestä aloitus, luonnolliset katkeamat, epätoivotut merkit (`.`, `/`, `_`), sekä truncation-artefaktit.

Visualisoinnit

- Trendit: $F1$ vs. lämpötila/$K$, Levenshtein vs. lämpötila, pituuden käyttö vs. lämpötila/EOS/Trim, delimiter-ratio.
- Paneelit: Top-10 mittaripaneelit parhaimmille konfiguraatioille.

## Notebook analyysin toistaminen

1.  Aja generaattori debug-logit päällä $\to$ sijoita JSONit kansioon `logs/YYYY-MM-DD/`.
2.  Avaa vastaava notebook (nimetty päivämäärällä) ja suorita kaikki solut.
3.  Vertaa tuloksia aiempiin snapshot-ajoihiin.
