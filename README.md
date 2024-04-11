# Eksamite infosüsteem (EIS)

## Funktsionaalsuse kokkuvõte

- ülesannete koostamine (üle 40 ülesandetüübi)
- testide koostamine (e-testid ja p-testid; suulised ja kirjalikud)
- testide sooritajate registreerimine
- soorituskohtade määramine, läbiviijate määramine, testide korraldamine
- testide läbiviimine
- e-testide vastamine
- p-testide testitööde sisestamine (vastused, punktid, õige-vale)
- p-testide hindamisprotokollide sisestamine
- testide hindamine (I, II, III, IV ja V hindamine)
- vastuste ja tulemuste statistika arvutamine
- tagasiside genereerimine
- tulemuste avaldamine 
- tulemuste vaidlustamine, vaiete menetlemine
- tunnistuste koostamine
- otsingud ja aruanded

## Konteinerstruktuur

Moodulist eis moodustatakse konteinerid:

- eisapp (avalik vaade)
- eisekk (eksamikeskuse vaade)
- adapter (X-tee adapter)
- eiscron (regulaarselt käivituvad tööd)

Kasutajaliides eeldab, et töötab ka konteiner:

- staticapp (staatilised .js, .css ja pildifailid)

Siit pöördutakse konteinerite poole:

- eisexam (mitu klastrit, mille aadressid registreeritakse kasutajaliideses)
- eistest (eistestproxy vahendusel)
- eisestnltk
- digitempel


## Installimine

### Andmebaaside loomine

Vt sql/README.md


### Installimine toodangukeskkonnas

Luuakse konteiner ja installitakse Kuberneteses, vt Dockerfile.


### Installimine arendaja lokaalses arvutis

Ubuntu 22.04 baasil installimiseks installida Python 3.12:

```
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
sudo apt install python3.12 python3.12-venv python3.12-dev

```

Installida vajalikud Ubuntu paketid (vt Dockerfile).

Luua /srv/eis liivakast:

```
sudo python3.12 -m venv /srv/eis
sudo /srv/eis/bin/pip install -r requirements.txt
```

Viia sisse formencode parandused (vt Dockerfile).

Luua vajalikud kataloogid:

```
sudo bash install.sh
```

Anda rakendust jooksutavale kasutajale õigus kataloogidele:

```
sudo chown -R www-data /srv/eis/var /srv/eis/lib/tmp /srv/eis/log
```


Kataloogist etc võtta näidiskonfifailid:

```
sudo cp etc/gunicorn-conf.py /srv/eis/etc
sudo cp etc/logging.ini /srv/eis/etc
sudo cp etc/eis.ini /srv/eis/etc/config.ini
```

Teha oma keskkonnale vastavad seadistused failis /srv/eis/etc/config.ini .


### Arenduskeskkonna käivitamine

Sättida PYTHONPATH nii, et sisaldab pakettide eiscore ja eis asukohti, näiteks:

```
export PYTHONPATH="~/eiscore:~/eis:$PYTHONPATH"
```

Käivitamine pserve abil:

```
/srv/eis/bin/pserve --reload /srv/eis/etc/config.ini?http_port=5000 -n eis
/srv/eis/bin/pserve --reload /srv/eis/etc/config.ini?http_port=5100 -n ekk

```
Brauseriga saab pöörduda:

- http://host:5100/eis/
- http://host:5200/ekk/

Andmebaasi algväärtustamisel loodi kasutaja admin (parool sama).
Sellena saab sisse logida, et luua EKK vaates tegeliku administraatori kasutaja ning deaktiveerida kasutaja admin.


### Genereerimine

Andmestruktuuri loomise skripti, kommentaaride ja dokumentatsiooni genereerimine:

```
cd sql
bash gen_tables.sh all
```

### Testimine

Testide käivitamine (eeldab kindlate ülesannete ja kasutajate eelnevat olemasolu andmebaasis):

```
/srv/eis/bin/python -m unittest -q eis.tests.unit.test.TestTests
/srv/eis/bin/python -m unittest -q eis.tests.unit.UnitTests
/srv/eis/bin/python -m unittest -q eis.tests.integration.korraldus
```

Testide käivitamine vastu ekk porti 5100:

```
/srv/eis/bin/python -m unittest -q eis.tests.functional.login.TestViews
/srv/eis/bin/python -m unittest -q eis.tests.functional.ylesanne.YlesanneTests
```
