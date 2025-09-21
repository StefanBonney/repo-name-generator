# Viikkoraportti 3

**Käytetty aika:** n. 12–14 tuntia

## Mitä olen tehnyt tällä viikolla?
- Lisäsin Trie-luokkaan palautteen mukaiset getterit ja `__str__`-metodin rakenteen visualisointiin:
  - `get_children()`, `get_next_counts()` TrieNodelle
  - `get_k()`, `get_root()` Trielle
- Toteutin Generator-luokan [src/generator/generator.py] joka käyttää trie-rakennetta nimien generointiin:
  - `find_node()` navigoi triessä k-grammin mukaan
  - `weighted_random_choice()` valitsee seuraavan merkin frekvenssipainotuksella
  - `generate()` tuottaa yhden nimen seedistä alkaen
  - `generate_batch()` tuottaa useita nimiä kerralla
- Loin UI-luokan [src/ui.py] yksinkertaisella komentorivi-käyttöliittymällä:
  - `get_user_input()` kysyy parametrit (seed, pituus, k, prefix)
  - `show_results()` näyttää generoidut nimet numeroituina
- Toteutin pääsilmukan [src/main.py] joka yhdistää komponentit:
  - Välimuisti: data ladataan uudelleen vain kun data_size muuttuu; trie rakennetaan vain kun k muuttuu tai data vaihtuu
  - Generatorin elinkaari: rakennetaan / päivitetään vain, jos asetukset (n_suggestions) muuttuvat; trie injektoidaan uudelleen kun se päivittyy.
- Lisäsin debug-toiminnallisuuden:
  - `DEBUG_TRIE`: näyttää trie-rakenteen ja muuta triehen liittyvää tietoa
  - `DEBUG_GENERATOR`: näyttää generoinnin polun ja muuta generointiin liittyvää tietoa, lokittaa generoinnin JSON-tiedostoon
  - Generator-debug [src/utils/generator_debug.py] analysoi tuloksia
- Loin testausdokumentin jossa:
  - Testikattavuus 62% (trie 95%, generator 79%)
  - Kuvaus testatuista komponenteista
  - Empiirisen testauksen tulokset eri k-arvoilla
- Tein factory-patternit projektin rakenteeseen:
  - `trie_factory.build()` datasta ja k:sta
  - `generator_factory.build()` triestä

## Miten ohjelma on edistynyt?
- Ohjelma on nyt toimiva ensimmäinen versio jolla voi generoida repo-nimiä eri parametreilla
- Generointi toimii hyvin eri k-arvoilla:
  - k=2: satunnaisempia yhdistelmiä ("hellocenzg", "helloud")
  - k=3: koherentimpia nimiä ("hello_nest", "hello-webh")
  - k=4: realistisimpia ("hello-world", "hello-wasm")
- seed toteutus toimii
- Välimuistitus toimii: samalla esim. k:lla trie ei rakennu uudelleen (kuvailtu tarkemmin ylhäällä)
- Ydinkomponentit - trie, generaattori - toimivat hyvin yhdessä muiden komponenttien kanssa
- Logitusta on lisätty runsaasti ja ne voidaan laittaa pois/päälle flagien kautta 
  - logeista tulostus sekä konsoliin että logeina
  - debug-lokit syntyvät automaattisesti `logs/` hakemistoon
  - jupyter notebook luotu jolla tarkoitus analysoida logeja
  - lisää yksikkötestejä analysoinnin perusteella
  - repo-käytäntö, commit vain tiedosto ei logeja (.gitkeep + .gitignore). Tarkoitus tehdä skripti joka antaa syötteitä ohjelmalle ja sitä kautta saadaan analysoitavia logeja.
- Ohjelma toimii tehokkaasti, ainoa aikaa vaativa osio on trien luonti ja uuden trien teko tapahtuu vain kun sellaisia parametreja muutetan jotka tarkoittavat että se on pakko luoda uusiksi.
- Factory rakenteiden ja debug utils tiedostojen yksi pääasiallinen tarkoitus on ollut pitää trie ja generator luokat mahdollisimman keskittyneitä ydintoiminnallisuuteen, silti antaen mahdollisuuden lisätä näiden ympärille toiminnallisuutta
  - mielestäni tämä on onnistunut kohtuullisen hyvin

## Mitä opin tällä viikolla?
- Painotetun satunnaisvalinnan toteuttamisen kumulatiivisilla summilla
- Pytest-fixtuurien hyödyntämisen testien yksinkertaistamiseen (`find_node` fixture)
- Factory-patternin soveltamista käytön joustavuuden lisäämiseen
- Debug-lokituksen järjestämisen JSON-muodossa myöhempää analyysiä varten

## Mikä jäi epäselväksi tai tuotti vaikeuksia?
- Tyhjän seedin käsittely: kun seed on "", ei ole k-grammia mistä aloittaa
  - Ratkaisu: tällä hetkellä palauttaa tyhjän, bootstrap-logiikka myöhemmin
- Testien kirjoittaminen generaattorille on haastavaa koska tulokset ovat stokastisia
  - käytän fixed random seed testeissä reproducibilityn vuoksi
  - analysoin debuggauksesta tulevia logeja ja yritän niiden avulla seuraavilla viikoilla toteuttaa lisää testejä jotka mittaavat generoinnin onnistumista
- Päätös siitä mikä koodi kuuluu mihinkin moduuliin, luokkaan tai funktiion (esim. find_node Generator vs Trie)
  - pidin Trien minimalistisena, navigointi kuuluu Generatorille
- Ongelmien juurisyyn löytäminen ja muutosten vaikutus
  - ohjelma laajenee ja se on välillä aiheuttanut vaikeuksia hahmottaa mihin kaikkialle muutos vaikuttaa tai mikä on jonkin virheen juurisyy
- Olisin halunut tehdä vielä lisää yksikkötestejä mutta muun toiminnalisuuden tekeminen vei niin paljon aikaa että en saannut niitä nyt tehtyä enempää aikaiseksi.

## Mitä teen seuraavaksi?
- Toteutan fallback-strategiat seedille joka ei löydy triestä
- kirjoitan lisää testejä että saan paremmman testikattavuuden
- Tarkistan generoinnin toimivuuden debug-tulosteiden avulla (logs -> jupyter notebook)
  - kirjoitan lisää yksikkö-testejä jotka testaavat toiminnallisuuden toteutumista
- Mietin miten voisin parhaiten hyödyntää similarity-filtteröintiä generoiduille nimille (osaltaan k-aste toteuttaa jo tätä)
- Yritän parantaa generoinnin toimivuutta 
  - saada aikaiseksi sanoja jotka muistuttavat läheisemmin sanoja joita käyttäjä oikeasti haluaisi käyttää repojen niminä (eli opitun mallin/harjoitusdatan mukaisia, merkityksellisiä sanoja, mutta jotka eivät vain toista harjoitusdatan sanoja)
  - toinen esimerkki: EOS toiminnalisuus tekee sen että jotkut sanat päätyvät liian usein (esim. tulostuksena voi olla, n5: mask, mask, mask, maskerade, mask)
  - mitattavat kriteerit (esim. "EOS-toistojen osuus < X%", "kielimäisyys-metriikan mediaani")
 - Skripti joka antaa syötteitä ohjelmalle ja sitä kauttaa saadaan analysoitavia logeja.


## Muuta / palaute
- Ohjelma toimii jo hyvin perustasolla. Generointi tuottaa suhteellisen uskottavia repo-nimiä ja debug-lokit auttavat tulosten analysoinnissa. Olisi hyvä saada palautetta siitä, ovatko nykyiset ydintoiminnallisuuden ominaisuudet ja suorituskyky riittäviä, sekä pitäisikö keskittyä johonkin tiettyyn osa-alueeseen seuraavaksi.