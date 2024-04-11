import logging
import datetime

from eis.model import *

def insert_testandmed():
    ts1 = Testsessioon(nimi='2012 riigieksamid', vaide_tahtaeg=date(2012,7,1), seq=10)
    ts2 = Testsessioon(nimi='2013 riigieksamid', vaide_tahtaeg=date(2012,7,1), seq=11)
    Kiirvalik(nimi='Riigieksamid', staatus=1)
    
    t = Test(nimi='X klassi bioloogia eksam', max_pallid=100, testiliik_kood='r', aine_kood='b',
             skeeled='et en', 
             testityyp=const.TESTITYYP_EKK)

    to1 = Testiosa(test=t, nimi='Esimene osa', piiraeg=7200, tahis='I', 
                   vastvorm_kood=const.VASTVORM_KE, ylesannete_arv=5)
    t.testiosad.append(to1)
    at = Alatest(seq=1, nimi='Alatest nr 1', piiraeg=5000, max_pallid=30)
    to1.alatestid.append(at)

    tp = Testiplokk(seq=1, nimi='Plokk nr 1')
    at.testiplokid.append(tp)
    kw = {'testiplokk': tp, 'alatest': at, 'testiosa': to1, 'max_pallid':5}
    tp.testiylesanded.append(Testiylesanne(nimi='Ülesanne nr 1', valikute_arv=3, **kw))
    tp.testiylesanded.append(Testiylesanne(nimi='Ülesanne nr 2', **kw))
    tp.testiylesanded.append(Testiylesanne(nimi='Ülesanne nr 3', **kw))
    
    tp = Testiplokk(seq=2, nimi='Plokk nr 2')
    at.testiplokid.append(tp)
    kw = {'testiplokk': tp, 'alatest': at, 'testiosa': to1, 'max_pallid':3}
    tp.testiylesanded.append(Testiylesanne(nimi='Ülesanne nr 4', **kw))

    at = Alatest(seq=2, nimi='Alatest nr 2', piiraeg=3000, max_pallid=70)
    to1.alatestid.append(at)    
    at.testiylesanded.append(Testiylesanne(nimi='Ülesanne nr 5', alatest=at, testiosa=to1, max_pallid=4))

    to2 = Testiosa(test=t, nimi='Teine osa', piiraeg=3600, tahis='II', vastvorm_kood=const.VASTVORM_SP, ylesannete_arv=1)
    t.testiosad.append(to2)
    to2.testiylesanded.append(Testiylesanne(nimi='Ülesanne nr 6', testiosa=to2, max_pallid=6))
    to2.testiylesanded.append(Testiylesanne(nimi='Ülesanne nr 7', testiosa=to2, max_pallid=6))
    to2.testiylesanded.append(Testiylesanne(nimi='Ülesanne nr 8', testiosa=to2, max_pallid=6))

    Session.flush()

    k1 = Komplekt(testiosa=to1, tahis='K1-1')
    k1.give_valitudylesanded()

    k2 = Komplekt(testiosa=to1, tahis='K1-2')
    k2.give_valitudylesanded()

    k3 = Komplekt(testiosa=to2, tahis='K2-1')
    k3.give_valitudylesanded()

    tk1 = Testimiskord(tahis='Kord1', test=t, testsessioon=ts1, skeeled='et en')
    tk1.give_toimumisajad()
    tk1.toimumisajad[0].komplektid.append(k1)
    tk1.toimumisajad[0].komplektid.append(k2)
    tk1.toimumisajad[1].komplektid.append(k3)

    tk2 = Testimiskord(tahis='Kord2', test=t, testsessioon=ts1, skeeled='et')
    tk2.give_toimumisajad()

    tk3 = Testimiskord(tahis='Kord3', test=t, testsessioon=ts2, skeeled='et')
    tk3.give_toimumisajad()

def insert_testpedagoog():
    Pedagoog(isikukood='30101010007',koht_id=3, ametikoht_kood='o',seisuga=datetime.now())
    Pedagoog(isikukood='30101010007',koht_id=2, ametikoht_kood='o',seisuga=datetime.now())
    Pedagoog(isikukood='30101010007',koht_id=4, ametikoht_kood='d',seisuga=datetime.now())
    Pedagoog(isikukood='30109010003',koht_id=4, ametikoht_kood='o',seisuga=datetime.now())

