# -*- coding: utf-8 -*- 
# $Id: tseis_update.py 9 2015-06-30 06:34:46Z ahti $
"""
TE ja SE tunnistuste andmete kandmine TSEISi tunnistuste registrisse.

TSEISi kantakse TE ja SE liiki tunnistused, 
mida veel pole TSEISi kantud (aeg_registris on NULL)
või mida on peale TSEISi kandmist muudetud (aeg_registris<modified).

Käivitada crontabist igal ööl:

python -m eis.scripts.tseis_update 
"""
from datetime import datetime, timedelta
import re
from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mssql import BIT
import sqlalchemy as sa
import traceback

from .scriptuser import *
from eis.lib.xtee import ads, SoapFault
from eis.lib.mailer import Mailer

Base = declarative_base()

class DiplomaRegistryEntry(Base):
    "TSEISi tunnistuste registri andmetabel"
    __tablename__ = 'DiplomaRegistryEntry'

    id = Column(Integer, primary_key=True, autoincrement=True)
    IsValid = Column(BIT)
    IssuedDate = Column(DateTime)
    IssueBasisDiplomaBasisDocumentId = Column(Integer)
    AnnullmentBasisDiplomaBasisDocumentId = Column(Integer)
    FormNumber = Column(String(510))
    IssuerName = Column(String(510))
    LevelName = Column(String(510))
    FirstName = Column(String(510))
    LastName = Column(String(510))
    DiplomaId = Column(Integer)
    IdentificationCode = Column(String(40))
    DateOfBirth = Column(DateTime) 
    ExamDate = Column(DateTime)
    ExamProtocolNumber = Column(String(510))
    ExamType = Column(String(510))
    ExamLevel = Column(String(510))
    ExamLocationAddress = Column(String(510))
    ExamLocationCity = Column(String(510))
    ExamLocationCounty = Column(String(510))
    ExamLocationZipCode = Column(String(510))
    DuplicateIssuedDate = Column(DateTime)
    DuplicateIssuedBasisDiplomaBasisDocumentId = Column(Integer)
    CreatedDate = Column(DateTime)
    CreatedByUserInfoId = Column(Integer)
    LastModified = Column(DateTime)
    ModifiedByUserInfoId = Column(Integer)
    CurrentId = Column(Integer) 
    IsDeleted = Column(BIT)
    PartResults = Column(Text)
    ExamPlanEntryRegionName = Column(String(510))
    ExamLocationName = Column(String(510))
    IssueBasis = Column(Text)


def push_data(tsession):
    "Andmete kandmine TSEISi tunnistuste registrisse"
    testiliigid = (const.TESTILIIK_TASE, const.TESTILIIK_SEADUS)
    q = model.Session.query(model.Tunnistus).\
        filter(model.Tunnistus.testiliik_kood.in_(testiliigid)).\
        filter(sa.or_(model.Tunnistus.aeg_registris==None,
                      model.Tunnistus.aeg_registris<model.Tunnistus.modified))

    log.info('TSEISi on vaja kanda %d kirjet' % q.count())
    cnt = 0

    def _encode(s):
        if s:
            charset = 'utf-8'
            return s.encode(charset, errors='replace')

    # mitme kande järel teha commit
    commit_cnt = 100
    
    # tsykkel yle ylekantavate tunnistuste
    for rcd in q.all():
        test = sooritaja = sooritus = koht = aadress = None
        for r in rcd.testitunnistused:
            sooritaja = r.sooritaja
            test = sooritaja.test
            sooritus = sooritaja.sooritused[0]
            koht = sooritus.testikoht.koht
            aadress = koht.aadress
            break

        kasutaja = rcd.kasutaja
        tunnistusenr = _encode(rcd.tunnistusenr)
        r = None
        if rcd.aeg_registris:
            # muuta olemasolevat kirjet
            r = tsession.query(DiplomaRegistryEntry).filter_by(FormNumber=tunnistusenr).first()
        if not r:
            # lisada
            r = DiplomaRegistryEntry()
            tsession.add(r)

        r.IsValid = rcd.staatus and 1 or 0
        r.IssuedDate = rcd.valjastamisaeg
        r.FormNumber = tunnistusenr
        r.IssuerName = _encode('SA Innove')
        r.LevelName = _encode(test and test.keeletase_nimi)
        r.FirstName = _encode(rcd.eesnimi)
        r.LastName = _encode(rcd.perenimi)
        r.IdentificationCode = _encode(kasutaja.isikukood)
        r.DateOfBirth = kasutaja.synnikpv
        r.ExamDate = sooritaja and sooritaja.algus or None
        r.ExamLevel = _encode(test and test.keeletase_kood)
        r.ExamLocationAddress = _encode(aadress and aadress.lahi_aadress)
        r.ExamLocationCity = _encode(aadress and aadress.vald)
        r.ExamLocationCounty = _encode(aadress and aadress.maakond)
        r.ExamLocationZipCode = _encode(koht and koht.postiindeks)
        r.IsDeleted = 0
        r.ExamLocationName = _encode(koht and koht.nimi)
        r.IssueBasis = _encode(rcd.alus)

        # ajale liidetakse pisike varu, kuna EISi tabelis salvestamisel
        # muudetakse välja modified väärtus ja sinna võib veel pisut aega minna
        rcd.aeg_registris = datetime.now() + timedelta(seconds=90)

        if cnt % commit_cnt == 0:
            tsession.commit()
            model.Session.commit()

        cnt += 1

    tsession.commit()
    model.Session.commit()
    log.info('TSEISi on kantud %d kirjet' % cnt)

def _error(exc, msg=''):
    model.Session.rollback()

    subject = 'Veateade (TSEISi liides)'
    subject += ': ' + msg.split('\n')[0].split(',')[0][:100]

    if exc:
        msg += '\n' + traceback.format_exc()

    log.error(msg)

    if registry.settings.get('smtp.error_to'):
        Mailer(handler).error(subject, msg)

    sys.exit(1)   

def _get_tsession():
    "TSEISi andmebaasiseansi loomine"
    tseis_url = registry.settings.get('tseis.url')
    if not tseis_url:
        _error(None, 'EISi konfiguratsioonis pole TSEISi andmebaasi andmeid')
        
    engine = sa.create_engine(tseis_url)
    TSession = sa.orm.sessionmaker(bind=engine)
    return TSession()

def usage():
    print('Kasuta kujul:')
    print('   python -m eis.scripts.tseis_update [-f KONFIFAIL]')
    print()
    sys.exit(0)

if __name__ == '__main__':
    engine = tsession = None
    try:
        tsession = _get_tsession()
        push_data(tsession)

    except Exception as e:
        _error(e, str(e))
    finally:
        if tsession:
            tsession.close()
