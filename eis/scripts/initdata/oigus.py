# -*- coding: utf-8 -*-
import logging
import datetime

from eis.model import *

txt_permissions = """
abi#Abiinfo
minu#Oma parooli muutmine jm seaded
lahendamine#Ülesannete lahendamine
sooritamine#Testimiskorra sooritamine
ylesanded#Kõik õigused ülesannetega, välja arvatud rollid
ylesanded-markused#Ülesannetele märkuste kirjutamine
ylesanded-toimetamine#Ülesannete toimetamine, sisutekstide muutmine põhikeeles
ylesanded-tolkimine#Ülesannete tõlkimine, sisutekstide muutmine tõlkekeeltes
ylesanded-failid#Ülesannete lisafailide lisamine/kustutamine
ylesanderoll#Konkreetse ülesandega seotud rollide andmine
ylesandemall#Ülesandemallide koostamine
ylesandetahemargid#Ülesande tähemärkide kokkulugemine
ylesandekogud#Ülesandekogude haldamine
ylkvaliteet#Ülesande kvaliteedimärgi sisestamine
ylhulgi#Kõigi ülesannete hulgi muutmine
yhisfailid#Ühiste failide lisamine ja muutmine ülesannetes kasutamiseks
ekk-testid#Kõik õigused EKK testidega, välja arvatud rollid
ekk-testid-toimetamine#EKK testi toimetamine
ekk-testid-tolkimine#EKK testi tõlkimine
ekk-testid-failid#EKK testi failid
testhulgi#Kõigi testide hulgi muutmine
ylesannelukustlahti#Ülesande lukust lahti võtmine
lukustlahti#Testi lukust lahti võtmine
korduvsooritatavus#EKK vaate testi korduvsooritatavuse seaded
konsultatsioonid#Konsultatsioonid
testid#Kõik õigused avaliku vaate testidega
testid-toimetamine#Avaliku vaate testi toimetamine
testid-tolkimine#Avaliku vaate testi tõlkimine
testiroll#Konkreetse testiga seotud rollide andmine
regamine#Registreerimine, EKK vaade
ekk-hindamine#Hindamise korraldamine, EKK vaade
ekk-hindamine6#VI hindamine
hindamisanalyys#Hindamise analüüs, EKK vaade
vastusteanalyys#Vastuste analüüs, EKK vaade
vastustevaljavote#Vastuste väljavõte, EKK vaade
eksperthindamine#Eksperthindamine, EKK vaade
ekspertryhmad#Ekspertrühmade haldamine, EKK vaade
hindajamaaramine#Hindajate määramine, EKK vaade
juhendamine#Hindajate juhendamine, EKK vaade
nimekirjad#Testile registreerimise nimekirjad
avtugi#EKK toe ligipääs testimiskorrata nimekirjadele
paroolid#Paroolide muutmine
avalikadmin#Soorituskoha administraatori tegevused
avylesanded#Avalikus vaates ülesande koostamine
aruanded-tunnistused#Päringud/Eksamitunnistused
aruanded-testisooritused#Päringud/Testisooritused
aruanded-kohateated#Päringud/Testisoorituskoha teated
aruanded-vaatlejateated#Päringud/Vaatlejate teated
aruanded-labiviijateated#Päringud/Läbiviijate teated
aruanded-tulemusteteavitused#Päringud/Tulemuste teavitused
aruanded-teated#Päringud/Teadete ülevaade
aruanded-labiviijad#Päringud/Läbiviijate aruanded
aruanded-labiviijakaskkirjad#Päringud/Läbiviijate käskkirjad
aruanded-nousolekud3#Päringud/III hindamise nõusolekud
aruanded-erinevused#Päringud/Hindamiserinevused
aruanded-soorituskohad#Päringud/Soorituskohad
aruanded-tulemused#Päringud/Tulemuste statistika
aruanded-osalemine#Päringud/Osalemise statistika
aruanded-prktulemused#Päringud/Piirkondade tulemused
aruanded-vaided#Päringud/Vaiete statistika
aruanded-osaoskused#Osaoskuste võrdlus
aruanded-testitulemused#Testitulemuste võrdlus
aruanded-rvtunnistused#Päringud/Rahvusvahelised eksamid
aruanded-tugiisikud#Päringud/Tugiisikud
aruanded-sooritajatearv#Päringud/Sooritajate arv
erivajadused#Erivajaduste haldamine
korraldamine#Eksamikorraldamine
sisestamine#Sisestamine
parandamine#Sisestuste parandamine
tunnistused#Tunnistuste genereerimine ja avaldamine
statistikaraportid#Statistikaraportite genereerimine ja avaldamine
lepingud#Läbiviijate lepingute haldamine
lopetamised#Lõpetamise kontroll
regkontroll#Registreerimise kontroll
vaided#Vaiete haldamine (HTM)
skannid#Skannitud eksamitööd
ettepanekud#Ettepanekute vaatamine
testiadmin#Testi administraator
intervjuu#Intervjuu läbiviimine
shindamine#Suulise testi hindamine
khindamine#Kirjaliku testi hindamine
thindamine#Testimiskorrata testi hindamine
nousolekud#Testide läbiviimises osalemise nõusoleku andmine
toovaatamine#Sooritaja testitöö vaatamine
klass#Pedagoogi õigus (klassi õpilaste loetelu, kooli testinimekirjad)
admin#Kõik administreerimismenüü tegevused
olulineinfo#Olulise info muutmine
keskserver#Kohalikus serveris õigus laadida keskserverist andmeid
testimiskorrad#Testimiskordade ja toimumisaegade haldamine, EKK vaade
tkorddel#Testimiskorra kustutamine
piirkonnad#Piirkondade haldus
kohad#Soorituskohtade haldus
kiirvalikud#Kiirvalikute haldus
sessioonid#Testsesioonide haldus
ametnikud#Eksamikeskuse kasutajate haldus (välja arvatud admin)
kasutajad#Testide läbiviimisega seotud kasutajate haldus
eksaminandid#Sooritajate haldus
eksaminandid-ik#Sooritajale isikukoodi lisamine
caeeeltest#CAE eeltesti sooritanute laadimine
kparoolid#Eksamikeskuse vaates parooli genereerimine või määramine (neile, kes pole eksamikeskuse kasutajad)
profiil#Läbiviija profiil
profiil-vaatleja#Vaatleja profiili osa läbiviija profiili vormil
klassifikaatorid#Klassifikaatorite haldus
logi#Logi vaatamine
abimaterjalid#Küsitluste abimaterjalid
toimumisprotokoll#Toimumise protokoll avalikus vaates
tprotsisestus#Toimumise protokolli osalejate sisestamine avalikus vaates
aineopetaja#Aineõpetaja õigus oma õpilaste tulemusi vaadata ja sisestada toimumise protokollile
rveksamid#Rahvusvaheliste eksamite tunnistuste kirjeldamine
failid#Failide allalaadimine koolis
plangid#Plankide haldur koolis
srcedit#Ülesannete koostamisel HTML lähtekoodi kasutamine
koolipsyh#Koolipsühholoogi testid
pslitsentsid#Koolipsühholoogide litsentside haldamine
logopeed#Logopeeditestid
lglitsentsid#Logopeedide litsentside haldamine
omanimekirjad#Avaliku vaate testide sooritajate nimekirjad
tookogumikud#Pedagoogide töökogumikud
kohteelvaade#Soorituskoha administraatori eelvaade
ui-tolkimine#Kasutajaliidese tekstide tõlkimine
tulemusteavaldamine#Tulemuste avaldamine
ettepanemine#Küsimuste ja ettepanekute esitamine avalikus vaates
sisuavaldamine#Ülesannete, testide ja e-kogude avaldamine
sysinfo#Süsteemi monitoorimise info
"""

def insert_kasutajaoigus():
    for line in txt_permissions.split('\n'):
        li = line.split('#')
        if len(li) == 2:
            permission = li[0]
            comment = li[1]
        else:
            permission = line
            comment = None
        if permission:
            Kasutajaoigus(nimi=permission, kirjeldus=comment).flush()

