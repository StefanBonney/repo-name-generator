# Toteutusdokumentti — Repo Name Generator

### Ohjelman yleisrakenne

> Ohjelma luo uusia, uskottavia mutta uniikkeja repository-nimiä hyödyntäen k-gram Markov-ketjuja. Se oppii tyypillisistä merkkiyhdistelmistä 1,5 miljoonan aidon repository-nimen harjoitusdatasta ja tuottaa niiden pohjalta luovia uusia nimiä.

> Arkkitehtuuri on rakennettu tehdasmallin (Factory Pattern) ympärille, joka mahdollistaa dynaamisen komponenttien valinnan syötettyjen konfiguraatioparametrien perusteella. Ohjelma eristää tehokkaan perusalgoritmin (Oletus) kokeellisista laajennuksista (Kokeellinen), ja käyttäjän valinnat ohjaavat toteutusta seuraavasti:

![System Architecture](images/to-1.png)

---

### Generointiprosessi ja Komponenttivalinnat

1.  **Käynnistys ja Konfiguraation Asetus** (`main.py`)
    * Komentoriviparametrit määrittävät ajotilan ja sen mukaiset komponenttivalinnat.
    * Käyttöliittymä kerää syötteet: aloitussana (seed), k:n arvo ja maksimipituus (max_length).
    * Oletustilassa ohjelma seuraa uskollisesti harjoitusdatan luonnollisia siirtymätodennäköisyyksiä, tuottaen autenttisia k-gram-ketjuja ilman keinotekoisia muokkauksia jakaumiin tai siirtymiin.
    * Kokeellinen tila puolestaan muokkaa harjoitusdatan siirtymiä lisäparametreilla, mahdollistaen satunnaisuuden säätämisen, sekä kontekstien vaihtelun ja harjoitusdatasta opittujen lopetuspisteiden käytön.
    * Kokeellinen tila aktivoituu automaattisesti, jos `temperature` $\neq 1.0$ tai jos kontekstin siirto (context-shifting) on käytössä.

2.  **Trie-rakenne** (`trie_factory.py`)
    * Valinta määrittää, miten trie-rakenne käsittelee nimen lopetuksen. Trie välimuistitetaan ja rakennetaan uudelleen vain, jos $k$:n arvo muuttuu.
    * Oletus: Rakenna `Trie` ilman EOS-merkkejä → maksimoi k-grammien harjoitusdatan hyödyntämistä.
    * Kokeellinen: Rakenna `TrieEOS` → sisältää EOS-merkit luonnollisten lopetusehtojen toteuttamiseksi.

3.  **Generaattori-algoritmi** (`generator_factory.py`)
    * Valinta määrittää seuraavan merkin valintamekanismin monimutkaisuuden.
    * Oletus: Valitse `Generator`, joka käyttää puhdasta frekvenssipohjaista satunnaisvalintaa.
    * Kokeellinen: Valitse `GeneratorExperimental`, joka tukee lämpötilasäätöä (satunnaisuuden hallinta) ja kontekstisiirtoja (monipuolisuuden lisääminen).
    * Yhteistä molemmille: Kaikki generaattorit suodattavat duplikaatit harjoitusdataa vastaan.

4.  **Nimien Generointi**
    * Valittu generaattori käyttää viimeisiä $k$ merkkiä kontekstina.
    * Etsii valitusta trie-rakenteesta seuraavien merkkien todennäköisyysjakauman.
    * Valitsee seuraavan merkin painotetulla satunnaisuudella valitun algoritmin mukaisesti.
    * Prosessi jatkuu, kunnes nimellä on max_length pituus tai kunnes saavutetaan lopetusehto.

***

### Aika- ja tilavaativuudet

**Trie-rakentamisen kompleksisuus**
* $O(N \cdot L)$
* Perustelu: Jokainen sana käsitellään kerran ($N$ sanaa), ja jokaiselle sanalle luodaan $L-k+1$ k-grammia, missä $L$ on sanan pituus. Pahimmassa tapauksessa jokainen merkki vaatii uuden solmun luonnin.
* Käytännön mittaukset:
    * lisättävä ensi viikkoon
* Skaalautuvuus: Lineaarinen sanojen määrässä, mutta k-arvo vaikuttaa vakiokertoimeen (suurempi k = vähemmän k-grammeja per sana).

**Generoinnin kompleksisuus**
* $O(m \cdot k)$
* Perustelu: Jokaiselle generoitavalle merkille ($m$ kpl) haetaan k-pituinen konteksti triestä. Haku vaatii $k$ solmun läpikäyntiä puurakenteessa.
* Käytännön suorituskyky:
    * Yksittäinen generointi: lisättävä ensi viikkoon
    * Batch-generointi (1000 nimeä): lisättävä ensi viikkoon
    * Pullonkaula: duplikaattien suodatus, ei itse generointi

**Muistikompleksisuus**
* $O(\min(|\Sigma|^k, \text{todellinen k-gram määrä}))$
* Teoreettinen yläraja: $|\Sigma|^k$ solmua, missä $|\Sigma|$ = aakkosto (esim. a-z + erikoismerkit $\approx 40$)
* Käytännön suorituskyky: lisättävä ensi viikkoon
* Optimointi: Trie-rakenne eliminoi redundanssin verrattuna hash-tauluun, jossa jokainen k-grammi tallennettaisiin erikseen.
* Optimoinnin rajoitus: Lapsisolmujen frekvenssien tallettaminen ei tarpeellista, kun riittäisi tallettaa solmuun sen oma frekvenssi.

**Välimuistitehokkuus**
* Trie rakennetaan kerran per k-arvo ja käytetään uudelleen kaikissa generoinneissa
* Uudelleenrakennus vain jos k muuttuu tai harjoitusdata päivittyy
* Käytännössä: ensimmäinen ajo 7s, seuraavat ajot välittömiä

***

### Työn mahdolliset puutteet ja parannusehdotukset

**Testaus**
* Lisättvä testikattavuutta ja testien määrää
* Kattavuus: $\mathbf{50\%}$ (25/25 testiä läpi).
* Testatut komponentit:
    * Trie: ($\mathbf{96\%}$ kattavuus) - k-gram rakentaminen, solmujen jakaminen, terminaalisolmut.
    * Generator: ($\mathbf{61\%}$ kattavuus) - siemenen säilytys, `max_length`, duplikaattisuodatus.
    * Laatu: Novelty (ei kopioita), Diversity (Dice-kerroin 0.4-0.95).
    * Suorituskyky: Aika- ja muistirajat.

**Puutteet ja jatkokehitys**
* Lisättvä testikattavuutta ja testien määrää
* Near-duplicate suodatus: Nyt vain *exact-match*, voisi laajentaa Levenshtein-etäisyyteen.
* Huolellisempi testaus bugien tunnistamiseksi ja edge case käyttäytymisne tunnistamiseksi
* Käyttäjävaroitukset: Esimerkiksi kun `len(results) < requested`, voisi informoida käyttäjää.

***

### Laajojen kielimallien käyttö

Hyödynsin projektissa ChatGPT:tä konsultatiivisessa ja tutkivassa roolissa. Malli toimi sparrauskumppanina suunnitteluvaiheessa, mutta koodi ja sen toteutuspäätökset ovat omaa työtäni.

Mallin käyttö oli korkean tason tukea ja keskittyi seuraaviin osa-alueisiin:

* Aihealuiden ymmärtäminen: Käsitteiden ja algoritmien perusperiaatteiden tutkiminen ja selventäminen ennen niiden soveltamista projektiin.
* Koodin ymmärtäminen: Aihealueisiin keskittyvien rakenteiden tai esimerkkien analysointi niiden toimintalogiikan omaksumiseksi.
* Arkkitehtuuri: Konsultointi optimaalisen yleisen tason toteutuksen ja eristyksen varmistamiseksi.
* Testausstrategia: Avun hakeminen esimerkiksi realistisen testikattavuustavoitteen määrittelyyn ja testattavien/testaamattomien koodiosien rajaamiseen.
* Refaktorointi: Palautteen pyytäminen koodin rakenteesta ja toimivuudesta. Yleisen tason palautetta ainoastaan.
* Debug-apu: Apu vaikeissa debug tilanteissa, esimerkiksi kun poetry ympäristö antoi virheimoituksia joista en saanut selkeyttä.

***

### Viitteet

lisättävä tänne ensi viikkoa varten