
### 1. Asennus ja käynnistys

#### 1.1. Asennus 

Varmista Poetry-ympäristö projektin sisään (suositus):
```bash
poetry config virtualenvs.in-project true
```

Asenna riippuvuudet (ensimmäisellä kerralla):

```bash
poetry install
```

HUOM: Jos `poetry shell` antaa seuraavanlaisen virheen   
`Split-Path ... Cannot bind argument to parameter 'Path' because it is null`,   
ohita aktivointi ja käytä suoraan `poetry run`, tai aja korjausskripti:

```powershell
# vaihtoehto 1: ohita aktivointi
poetry run pytest -q

# vaihtoehto 2: korjaa venvin activate.ps1 ja käytä shelliä
pwsh -File .\scripts\patch-activate.ps1
poetry shell
```
#### 1.2. Käynnistys

Käynnistä poetry:

```bash
poetry shell
```

Käynnistä sovellus:

```bash
python -m src.main
```
  
Tarkemmat käynnistys- ja ajoohjeet mm. ajoihin eri vaihtoehdoilla enabloituna löytyvät alla.

---

### 2. Ajot eri syöteillä ja asetuksilla

#### 2.1. Syötteet

Käynnistyttyään ohjelma ohjaa käyttäjää interaktiivisen valikon kautta. Ohjelma kysyy seuraavat parametrit:

1. Aloitussana/merkkijono 
    - Mistä merkeistä generoitu nimi alkaa (esim. `data`, `api`, `web`)
2. Maksimipituus 
    - Generoitavan nimen maksimipituus merkkeinä (esim. `12`)
3. K-arvo 
    - Markov-mallin aste, eli kuinka monta edellistä merkkiä huomioidaan seuraavaa ennustaessa (suositus: `2-4`)
    - Pieni k (2) tuottaa luovempia mutta satunnaisempia nimiä. Suurempi k (3-4) tuottaa realistisempia mutta konservatiivisempia nimiä, jotka muistuttavat enemmän opetusdataa.
    - Ohjelma säilyttää trie-rakenteen muistissa. Jos käytät samaa k-arvoa, datan kokoa ja EOS-asetusta uudelleen, generointi on huomattavasti nopeampaa.
4. Ehdotusten määrä 
    - Kuinka monta nimiehdotusta generoidaan (esim. `5`)
5. Datan koko 
    - Kuinka monta riviä opetusdataa käytetään (oletus/max: `1500000`)
    - Pienempää datamäärää tulee lähinnä käyttää jos trien debug on käytössä
6. EOS-tokenien käyttö 
    - Käytetäänkö End-Of-Sequence -tokeneita sanojen päättymisen oppimiseen 
    - Parantaa sanojen luonnollista päättymistä oppimalla mistä kohdasta sanat tyypillisesti loppuvat opetusdatassa.
    - Altistaa kuitenkin generointien ennenaikaiselle lopettamiselle
7. Etuliite 
    - Voidaan valinnaisesti lisätä kaikkiin generoituihin nimiin (esim. `sys-`, `lib-`)


#### 2.2. Asetukset

Ohjelma tukee useita komentoriviparametreja, joilla voidaan säätää toiminnallisuutta.

```bash

# DEBUG

# Näytä trie-rakenteen debug-tiedot
python -m src.main --debug-trie

# Näytä generaattorin debug-tiedot ja tallenna JSON-lokit
python -m src.main --debug-generator

# Näytä pääsilmukan debug-tulosteet
python -m src.main --debug-main

# Kaikki debug-tilat kerralla
python -m src.main --debug-all

# TRIM

# Käytä delimiter-pohjaista trimmausta
python -m src.main --enable-trim-v1

# Käytä morfologisesti tietoista trimmausta (suositeltu)
python -m src.main --enable-trim-v2

# KOKEELLISET OMINAISUUDET

# Säädä lämpötilaa (oletus: 1.0, pienempi = konservatiivisempi, eli valitsee vierlä todennäköisemmin todennäköiset jatkajat)
python -m src.main --temperature 0.8

# Aktivoi EOS-jatkohaku (vaihtoehtoisten polkujen tutkiminen eos lopetuksessa, ennen estimoitua optimaalista päättymispituutta)
python -m src.main --use-eos-continuation-search

# Maksimi jatkohakuyritykset (jatkohakuun liittyen, oletus: 3)
python -m src.main --max-continuation-attempts 5
```

Yhdistelmäesimerkkejä:

```bash
# Debug-tila morfologisella trimmauksella
python -m src.main --debug-generator --enable-trim-v2

# Kokeellinen tila matalalla lämpötilalla ja EOS-jatkohaulla
python -m src.main --temperature 0.7 --use-eos-continuation-search

# Täysi debug kokeellisilla ominaisuuksilla
python -m src.main --debug-all --temperature 0.9 --use-eos-continuation-search # asetta UI:ssa data-size pinemmäksi jos debug trie/all
```

Huomioitavaa:
- Kokeellinen tila aktivoituu automaattisesti kun `--temperature` poikkeaa arvosta 1.0 tai `--use-eos-continuation-search` on käytössä
- Debug-generaattori tallentaa JSON-lokit automaattisesti `logs/`-hakemistoon
- Trim-algoritmit ovat toisensa poissulkevia - voit käyttää vain toista kerrallaan

#### 2.3. Suositus syötteet ja asetukset

- Nimien tulisi olla sellaisia että niitä oikeasti voitaisiin käyttää repojen niminä sellaisenaan, 
- Koska generoidut nimet ovat usein yhdistelmä sanoja, sanoissa tulisi kokonaisuutena myös olla yhteensopivuutta (esim. huippu-ohjain [ok] vs. huippu-tarvitsen [ei niin ok])   
- Tässä mielessä myös innovatiiviset yhdistlmät ovat laadun merkki, toisaalta yhdistelmät eivät pelkästään saisi olla yhdistelmiä olemasaolevista sanoista

Tässä on esitettynä kaksi suositusta jotka johtavat laadukkaisiin tuloksiin.

**Perusgeneraattorille**

Hyvät tulokset repo-nimien generointiin ilman muita kuin perus generattorin ja trien toiminnalisuuksia hyödyntäen, saa esimerkiksi seuraavin kutsuin/parametrein.

Trim on ainoa lisä-toiminnallisuus jota perus generaattori voi hyödyntää. Tämä leikkaa sanojen lopusta sellaiset postfixit jotka eivät vaikuta sanojen luonnollisilta lopetuksilta, esim -ba

```bash
python -m src.main --enable-trim-v2
```

UI-syötteet
```code
- Starting letters     : trigger  (esimerkiksi)
- Max length           : 20       (tarpeeksi kirjaimia jotta generointi voi kehittää järkeviä nimityksiä)
- Markov degree k      : 4 / 5    (isompi k tarkoittaa yleisesti parempi-laatuisia tuloksia, joskin sanat eivät vältämättä ole innovatiivisia, k=4 pitää hyvän tasapainon)
- Number of suggestions: default  (5, tai oman mielen mukaan)
- Training data size   : default  (käytetään kaikki harjoitusdata)
- prefix               :          (oman mielen mukaan)
- Use EOS markers      : default  (base triessä ei eos)
```

**Kokeellisen generaattorin** kohdalla esitetään seuraava suositus.

```bash
python -m src.main --temperature 0.6 --use-eos-continuation-search --max-continuation-attempts 7 --enable-trim-v2
```

UI-syötteet
```code
- Starting letters     : controller (esimerkiksi)
- Max length           : 25         (eos antaa luonnollisia päättymiä, jolloin on hyvä antaa vielä enemmän kirjaimia generoinnille)
- Markov degree k      : 4          (kuin yllä, temperature 0.6 vaikuttaa että on todennäköisempää valita yleisimmin esiintyvät seuraajat)
- Number of suggestions: default    (5, tai oman mielen mukaan)
- Training data size   : default    (käytetään kaikki harjoitusdata)
- prefix               :            (oman mielen mukaan)
- näillä asetuksilla käytetään automaattisesti eos-trie:tä
```
