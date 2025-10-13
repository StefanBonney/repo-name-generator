# Viikkoraportti 6

**Käytetty aika:** 14–16 tuntia


## Mitä olen tehnyt tällä viikolla?

### 1. Trim-algoritmien korjaus ja parannus

Edellisen viikon batch-testien analyysin perusteella havaitsin että trim-toiminnallisuus tuotti epäjohdonmukaisia tuloksia:
- Katkaisut epäonnistuivat usein (esim. `controllerikkend-addon-ba` → ei leikattu), muutin trie algoritmia niin että leikkaukset tapahtuvat luotettavasti.
- `trim_v1` tekee vain tällaisia yksinkertaisia lyhitä erottaja-merkkeihin perustuvia leikkauksia
- Tein myös `trim_v2` tiedoston jossa morfologinen analyysi jota sovelletaan vain merkittäviin leikkauksiin ($> 3$ merkkiä).


### 2. eos_continuation_search toiminnallisuus

- Aiemmin suunniteltu idea toiminnalisuudesta `context_shifting` ei vaikuttanut relevantilta enään.   
- Sen sijaan eos-triehen perustuvat generoinnit päättyivät usein liian lyhyeeseen.  
- Tätä varten toteutin toiminnallisuuden `eos_continuation_search`, joka valitsee uuden vaihtoehdon eos sijaan, jos päättyminen ei ole generoitavan snaan (max_len) loppuosassa.
- `max_continuation_attempts` määrittää kuinka monta kertaa tämä ohitus voidaan tehdä yhden genroinnin aikana.
- backtracking ominaisuus puuttuu, esim. k=3 ... tasks -> sks {eos:2} -> ask {eos:2, t:3, a:2}
- testiajojen perusteella kuitenkaan tälle ei vältämättä tarvetta, generoinnit etenevät hyvin max sanamäärää kohti

### 3. Datan sanitointi

Toteutin `_sanitize()` -funktion joka poistaa polkuartefaktit (`.` ja `/`) harjoitusdatasta:
- Sovellettu molemmissa factory-tiedostoissa:
    - `trie_factory.py`: Sanitoi trien rakennuksen yhteydessä.
    - `generator_factory.py`: Sanitoi duplikaattitarkistuksen yhteydessä.
- Ratkaisu notebookin analyysissä havaittuun **"character contamination"** -ongelmaan.
- Varmistaa että path-merkit eivät pääse läpi missään vaiheessa.

### 4. Syöte validoinnit

Toteutin syötteiden validoinnin ja käyttökokemuksen parantamisen:
- UI tiedoston `_validate_int_input()` -metodi tarkistaa syötteet.
    - Range-checking: $k \in [2,10]$, length $\in [1,50]$, $n\_suggestions \in [1,100]$.
    - virheilmoitukset ja uudelleenyritys virheellisellä syötteellä.

### 5. Testikattavuuden parantaminen

Kirjoitin 9 uutta testiä:

**Generator-testit**
* `test_generate_stops_immediately_when_context_unseen()` - Tuntemattoman contextin käsittely
* `test_batch_dedup_respects_max_attempts_and_returns_empty()` - Duplikaattisuodatus harjoitusdatan kanssa
* `test_batch_uniqueness_limits_duplicates()` - Sisäinen deduplikaatio batchissa
* `test_seed_with_slash_returns_seed_unchanged()` - Sanitoinnin validointi
* `test_low_temperature_forces_most_probable_choice()` - Temperature-skaalaus (experimental)

**Trie-testit**
* `test_duplicate_insertions_increase_counts()` - Frekvenssien kasautuminen

**UI-testit**
* `test_ui_defaults_basic_mode()` - Oletusarvojen käsittely
* `test_ui_custom_values()` - Mukautettujen syötteiden prosessointi
* `test_ui_validates_invalid_integer_input()` - Validointisilmukan toiminta
:
**Kattavuus**
* generator.py: 82%
* generator_experimental.py: 60%
* trie.py: 96%
* trie_eos.py: 92%
* Kokonaiskattavuus: 60%

### 6. Debug-logituksen v2

Päivitin generator debug -logitusta sisältämään:
* Trim-statistiikka: Kumpi versio käytössä, onnistumiset/epäonnistumiset.
* Continuation-statistiikka: Kuinka moni sample jatkettiin EOS:n yli.

### 7. Optimaalisten parametrien etsintä ja dokumentointi

- Yhtenä tavoitteena tälle viikolle halusin löytää configuraation ja syöteet jolla saan generoitua järkeviä ja samalla innovatiivisia elementtejä sisältäviä repojen nimiä 
- Nimien tulisi olla sellaisia että niitä oikeasti voitaisiin käyttää repojen niminä sellaisenaan, 
- Koska generoidut nimet ovat usein yhdistelmä sanoja, sanoissa tulisi kokonaisuutena myös olla yhteensopivuutta (esim. huippu-ohjain [ok] vs. huippu-tarvitsen [ei niin ok])   
- Tässä mielessä myös innovatiiviset yhdistlmät ovat laadun merkki, toisaalta yhdistelmät eivät vain saisi olla yhdistelmiä olemasaolevista sanoista

Tähän kirjoitin kaksi suositusta.

**Perusgeneraattorille**

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
Esimerkkejä tulostuksista (k=4): 
> trigger-ts-server111  
> trigger-widge-to-pre  
> trigger-jinjakttv  
> trigger-rails  
> trigger-nodern  

Tässä tulos on kohtuullisen hyvä esimerkiksi trigger-rails on selkeästi vain yhdistelmä olemassaolevia sanoja, mutta kuitenkin koherentti käytettävä ja uniikki yhdistelmä.

Esimerkkejä tulostuksista (k=5):
> gatsby-remote-loader  
> gatsby-request    
> gatsby-response_form  

> bootstrap-feedbackwa  
> bootstrapOverflow   
> bootstrap_forman  

k=5 antaa myös runsaasti vastaavia esimerkkejä, ja joukosta myös sanoja jotka eivät ainakaan ole pelkkää sanojen kauttaviivalla yhdistämstä.
Esimerkiksi `bootstrap_forman` sanan kohdalla löytyy harjoitusdatasta etsimällä  `bootstrap_f` sanoja kuten `bootstrap_farsi` tai `bootstrap_form`, ja vaikka `forman` ei ole sana samassa mielessä kuten esim form, se muistuttaa tarpeeksi läheisesti sanaa `foreman` tai `for man` ollakseen järkevä. 

**Kokeellisen generaattorin** kohdalla tein seuraavan suosituksen.

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

Esimerkkitulostuksia:
> controllery-program  
> controllers-controller   
> controllerator-collective   
> controllery-botocol-serve  
> controller-starter   

Mielestäni nämä ovat myös laadukkaita generointeja. Ne ovat vielä vähemmässä määrin suoraan kauttaviivalla yhdistelyjä olemassaolevista sanoista (esim. controllery ei esiinny harjoitusdatassa, mutta kuullostaa järkevältä sanan jatkeelta), ja yhdisteyty sanat ovat suhteellisen järkevässä sidonnaisuudessa toisiinsa (esim. controller ja program).   


## Miten ohjelma on edistynyt?

- Trim toimii johdonmukaisesti: Molemmat versiot (v1 & v2) leikkaavat lyhyet segmentit oikein.
- Sanitointi poistaa path-artefaktit systemaattisesti.
- Syötteiden validointi estää virheelliset arvot, selkeät virheilmoitukset.
- Testikattavuus parantunut
- Generaatiot ovat tarkoitukseen sopivia, ainakin tietyin parametrein ja syötteillä jotka antavat hyvin mhadollisuuden repo-nimien generointiin


## Mitä opin tällä viikolla?

- Sanitoinnin strategiat: oli helpompi ratkaisu tähän vaiheeseen olla siivoamatta dataa, ja sen sijaan antaa factory:lle toiminnalisuus puhdistaa epätoivotut merkit 
- Testikattavuuteen tähtäävä testaus: uudet testit nostivat hyvin kattavuutta 
- Pistytyksen vaikeus: jouduin vielä pitkälti turvautumaan manuaaliseen tarkistamiseen saadakseni selville mitkä generoinnit tuottivat laadukkaita tuloksia


## Mikä jäi epäselväksi tai tuotti vaikeuksia?

- Testikattavuuden priorisointi: Pitääkö pyrkiä 100% kattavuuteen vai riittääkö kriittisten polkujen testaaminen? Päädyin keskittymään laatuun määrän sijaan - $82\%$ generator-kattavuus tuntuu riittävältä kun testit kattavat kaikki tärkeät skenaariot.


## Mitä teen seuraavaksi?

1.  **Dokumentaation viimeistely**
    - Tällä viikolla  meni paljon aikaa kun yritin saada järkeviä generointeja aikaiseksi
    - oli tarkoitus siistä dokumentaatiota enemmän, mutta nyt jää ensi viikolle
2.  **Koodin viimeistely:**
    * Kommenttien tarkistus ja yhtenäistäminen
    * Turhan koodin ja vanhojen kommenttien poisto

## Palautepyyntö

- Onko testikattavuus nyt riittävällä tasolla, vai pitäisikö vielä nostaa jotain tiettyä osa-aluetta?
- Vaikuttavatko generoinnit hyviltä, vai onko niissä vielä havaittavissa sellaisia puutteita tai parantamisen tarpeita, joita en ole itse huomannut/ylikatsonut?