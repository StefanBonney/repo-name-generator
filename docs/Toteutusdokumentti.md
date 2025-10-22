# Toteutusdokumentti — Repo Name Generator

### Ohjelman yleisrakenne

> Ohjelma luo uusia, uskottavia mutta uniikkeja repository-nimiä hyödyntäen k-gram Markov-ketjuja. Se oppii tyypillisistä merkkiyhdistelmistä 1,5 miljoonan aidon repository-nimen harjoitusdatasta ja tuottaa niiden pohjalta luovia uusia nimiä.

> Arkkitehtuuri on rakennettu tehdasmallin (Factory Pattern) ympärille, joka mahdollistaa dynaamisen komponenttien valinnan syötettyjen konfiguraatioparametrien perusteella. Ohjelma eristää tehokkaan perusalgoritmin (Oletus) kokeellisista laajennuksista (Kokeellinen), ja käyttäjän valinnat ohjaavat toteutusta seuraavasti:

![System Architecture](images/readme-5-b.png)

---

### Generointiprosessi ja Komponenttivalinnat

1.  **Käynnistys ja Konfiguraation Asetus** (`main.py`)
    - Komentoriviparametrit määrittävät ajotilan ja sen mukaiset komponenttivalinnat.
    - Käyttöliittymä kerää syötteet: aloitussana (seed), k:n arvo ja maksimipituus (max_length).
    - Oletustilassa ohjelma seuraa uskollisesti harjoitusdatan luonnollisia siirtymätodennäköisyyksiä, tuottaen autenttisia k-gram-ketjuja ilman keinotekoisia muokkauksia jakaumiin tai siirtymiin.
    - Kokeellinen tila puolestaan muokkaa harjoitusdatan siirtymiä lisäparametreilla, mahdollistaen satunnaisuuden säätämisen, sekä kontekstien vaihtelun ja harjoitusdatasta opittujen lopetuspisteiden käytön.
    - Kokeellinen tila aktivoituu automaattisesti, jos `temperature` $\neq 1.0$ tai jos EOS-jatkohaku (`use_eos_continuation_search`) on käytössä.

2.  **Trie-rakenne** (`trie_factory.py`)
    - Valinta määrittää, miten trie-rakenne käsittelee nimen lopetuksen. Trie välimuistitetaan ja rakennetaan uudelleen vain, jos $k$:n arvo muuttuu.
    - Oletus: Rakenna `Trie` ilman EOS-merkkejä → maksimoi k-grammien harjoitusdatan hyödyntämistä.
    - Kokeellinen: Rakenna `TrieEOS` → sisältää EOS-merkit luonnollisten lopetusehtojen toteuttamiseksi.

3.  **Generaattori-algoritmi** (`generator_factory.py`)
    - Valinta määrittää seuraavan merkin valintamekanismin monimutkaisuuden.
    - Oletus: Valitse `Generator`, joka käyttää puhdasta frekvenssipohjaista satunnaisvalintaa.
    - Kokeellinen: Valitse `GeneratorExperimental`, joka tukee lämpötilasäätöä (satunnaisuuden hallinta) ja EOS-jatkohakua (vaihtoehtoisten polkujen tutkiminen).
    - Yhteistä molemmille: Kaikki generaattorit suodattavat duplikaatit harjoitusdataa vastaan.
    - Generoidut nimet voidaan siistiä kahdella algoritmilla: **v1** (delimiter-pohjainen, poistaa lyhyet segmentit) tai **v2** (morfologisesti tietoinen, tunnistaa epäluonnolliset päätteet kuten `"repositor"` → trimmaa delimiteriin). Tapahtuu generoinnin jälkeen, O(n).

4.  **Nimien Generointi**
    - Valittu generaattori käyttää viimeisiä $k$ merkkiä kontekstina.
    - Etsii valitusta trie-rakenteesta seuraavien merkkien todennäköisyysjakauman.
    - Valitsee seuraavan merkin painotetulla satunnaisuudella valitun algoritmin mukaisesti.
    - Prosessi jatkuu, kunnes nimellä on max_length pituus tai kunnes saavutetaan lopetusehto.

***

### Aika- ja tilavaativuudet

**Trie-rakentamisen kompleksisuus**
- $O(N \cdot L)$
- Perustelu: Jokainen sana käsitellään kerran ($N$ sanaa), ja jokaiselle sanalle luodaan $L-k+1$ k-grammia, missä $L$ on sanan pituus. Pahimmassa tapauksessa jokainen merkki vaatii uuden solmun luonnin.
- Käytännön mittaukset:
    - Trie-rakennus (k=3, 1.5M riviä): ~9-11 sekuntia
    - Trie-rakennus (k=4, 1.5M riviä): ~11-14 sekuntia  
    - Trie-rakennus (k=5, 1.5M riviä): ~15-16 sekuntia
    - Nopein mitattu konfiguraatio: 8.9s (k=3, temperature=0.8)
    - Hitain mitattu konfiguraatio: 16.4s (k=5, täysi data)
- Skaalautuvuus: Lineaarinen sanojen määrässä, mutta k-arvo vaikuttaa vakiokertoimeen (suurempi k = vähemmän k-grammeja per sana).

**Generoinnin kompleksisuus**
- $O(m \cdot k)$
- Perustelu: Jokaiselle generoitavalle merkille ($m$ kpl) haetaan k-pituinen konteksti triestä. Haku vaatii $k$ solmun läpikäyntiä puurakenteessa.
- Käytännön suorituskyky:
    - Yksittäinen generointi: <1ms (välimuistista) 
    - Generaattori-rakentaminen: ~0.5ms
    - Batch-generointi: 8.9-16.4s riippuen k-arvosta ja konfiguraatiosta
    - Pullonkaula: Duplikaattien suodatus O(n²), ei itse generointi O(m·k)

**Muistikompleksisuus**
- $O(\min(|\Sigma|^k, \text{todellinen k-gram määrä}))$
- Teoreettinen yläraja: $|\Sigma|^k$ solmua, missä $|\Sigma|$ = aakkosto (esim. a-z + erikoismerkit $\approx 40$)
- Käytännön suorituskyky: 
 - Todellinen muistin käyttö paljon pienempi kuin teoreettinen |Σ|^k maksimi
 - Trie tallentaa vain harjoitusdatassa esiintyvät k-grammit
 - Esim. k=3, |Σ|≈40 → teoreettinen max 64,000 solmua, käytännössä vain esiintyvät kombinaatiot
- Optimointi: Trie-rakenne eliminoi redundanssin verrattuna hash-tauluun, jossa jokainen k-grammi tallennettaisiin erikseen.
- Optimoinnin rajoitus: Lapsisolmujen frekvenssien tallettaminen ei tarpeellista, kun riittäisi tallettaa solmuun sen oma frekvenssi.

**Välimuistitehokkuus**
- Trie rakennetaan kerran per k-arvo ja käytetään uudelleen kaikissa generoinneissa
- Uudelleenrakennus vain jos k muuttuu tai harjoitusdata päivittyy
- Käytännössä: ensimmäinen ajo 7s, seuraavat ajot välittömiä

***

### Työn mahdolliset puutteet ja parannusehdotukset

**Testaus**
- Lisättävä testikattavuutta ja testien määrää
- Kokonaiskattavuus: **60%** rivikattavuus (34 testiä läpi)
- Komponenttikohtainen kattavuus:
    * `trie.py`: **96%** - k-gram rakentaminen, frekvenssit, terminaalisolmut
    * `trie_eos.py`: **92%** - EOS-merkinnät, lopetuspisteet
    * `generator.py`: **82%** - siemenen säilytys, `max_length`, duplikaattisuodatus
    * `generator_experimental.py`: **60%** - temperature-skaalaus, EOS-jatkohaku

**Puutteet ja jatkokehitys**
- Lisättvä testikattavuutta ja testien määrää
- Near-duplicate suodatus: Nyt vain *exact-match*, voisi laajentaa Levenshtein-etäisyyteen.
- Huolellisempi testaus bugien tunnistamiseksi ja edge case käyttäytymisen tunnistamiseksi
- syötteiden parempi validointi
- Käyttäjävaroitukset: Esimerkiksi kun `len(results) < requested`, voisi informoida käyttäjää.

***

### Laajojen kielimallien käyttö

Hyödynsin projektissa ChatGPT:tä konsultatiivisessa ja tutkivassa roolissa. Malli toimi sparrauskumppanina suunnitteluvaiheessa, mutta koodi ja sen toteutuspäätökset ovat omaa työtäni.

Mallin käyttö oli korkean tason tukea ja keskittyi seuraaviin osa-alueisiin:

- Aihealuiden ymmärtäminen: Käsitteiden ja algoritmien perusperiaatteiden tutkiminen ja selventäminen ennen niiden soveltamista projektiin.
- Koodin ymmärtäminen: Aihealueisiin keskittyvien rakenteiden tai esimerkkien analysointi niiden toimintalogiikan omaksumiseksi.
- Arkkitehtuuri: Konsultointi optimaalisen yleisen tason toteutuksen ja eristyksen varmistamiseksi.
- Testausstrategia: Avun hakeminen esimerkiksi realistisen testikattavuustavoitteen määrittelyyn ja testattavien/testaamattomien koodiosien rajaamiseen.
- Refaktorointi: Palautteen pyytäminen koodin rakenteesta ja toimivuudesta. Yleisen tason palautetta ainoastaan.
- Debug-apu: Apu vaikeissa debug tilanteissa, esimerkiksi kun poetry ympäristö antoi virheimoituksia joista en saanut selkeyttä.
- Batch-testikonfiguraatiot: JSON-konfiguraatiotiedostojen generointi batch-ajoja varten. Tuotti systemaattisia testitapauksia eri parametriyhdistelmillä (k-arvot, temperature, seed-sanat, data-koot).

***

### Viitteet

**N-gram-kielimallit ja Markov-ketjut:**
- Goodrich, Tamassia, Goldwasser (2013). Data Structures and Algorithms in Python. Luku 13. 
- Miller & Ranum (2011). Problem Solving with Algorithms and Data Structures Using Python. Luvut 3,6.
- Sarkar (2nd ed., 2019). Text Analytics with Python. Luvut 1, 3-4, 6.
- Jurafsky, D., & Martin, J. H. (2023). Speech and Language Processing (3rd ed.). Luku 3.
- Liu, J., Min, S., Zettlemoyer, L., Choi, Y., & Hajishirzi, H. (2024). Infini-gram: Scaling Unbounded n-gram Language Models to a Trillion Tokens. 


**Suorituskyky, arkkitehtuuri ja optimointi:**
- Gorelick & Ozsvald (2020). High Performance Python (2nd ed.). Luku 2.
- Slatkin (2020). Effective Python (2nd ed.). Luvut 2, 8-9.

**Testaus ja laatu:**
- Okken (2022). Python Testing with pytest (2nd ed.). Luvut 2, 3, 8-9.

**Harjoitusdata:**
- Katz, J. (2020). Libraries.io Open Source Repository and Dependency Metadata (Version 1.6.0) [Data set]. Zenodo. https://doi.org/10.5281/zenodo.3626071

**Muut:**
- Python dokumentaatio. https://docs.python.org/3/
- Poetry dokumentaatio. https://python-poetry.org/