"""Ülesande sisuplokis olevate valemite arvutamise keskkond
"""
import re
from eis.lib.base import *
_ = i18n._
import eis.lib.helpers as h
log = logging.getLogger(__name__)

class FormulaEnv(object):
    def __init__(self, handler):
        self.handler = handler

    def test_formula(self, block, f_locals):
        # testime syntaksit

        kysimus = block.kysimus
        ylesanne = block.ylesanne or model.Ylesanne.get(block.ylesanne_id)

        # väärtustame valemi testimiseks lokaalsed muutujad
        for plokk in ylesanne.sisuplokid:
            if plokk == block:
                continue
            for k in plokk.kysimused:
                tulemus = k.tulemus
                if tulemus and k.kood:
                    kardinaalsus = tulemus.kardinaalsus or const.CARDINALITY_SINGLE
                    baastyyp = tulemus.baastyyp
                    if baastyyp == const.BASETYPE_INTEGER:
                        value = 1
                    elif baastyyp == const.BASETYPE_FLOAT:
                        value = 1.
                    elif baastyyp == const.BASETYPE_MATH:
                        value = 'x'                        
                    elif baastyyp in (const.BASETYPE_STRING, const.BASETYPE_IDENTIFIER):
                        value = '2'
                    elif baastyyp == const.BASETYPE_POINT:
                        value = (1,1)
                    elif baastyyp == const.BASETYPE_BOOLEAN:
                        value = False
                    elif baastyyp in (const.BASETYPE_PAIR, const.BASETYPE_DIRECTEDPAIR):
                        value = ('A','B')
                    else:
                        value = None
                    if value and kardinaalsus == const.CARDINALITY_SINGLE:
                        f_locals[k.kood] = value
                    elif value:
                        f_locals[k.kood] = [value]

                    for hm in tulemus.hindamismaatriksid:
                        if hm.tahis:
                            f_locals[hm.tahis] = 0

        # funktsioonide keha vt blockresponses
        f_locals.update(self.formula_funcs({}))
        f_locals.update(self.get_sisuvaatamised(ylesanne, []))
        
        value, err0, err, buf1 = model.eval_formula(block.sisu, f_locals)
        return err

    def formula_funcs(self, responses, loendurid=None, sisuvaatamised=[]):
        "Valemites kasutatavate funktsioonide defineerimine"
        f_locals = dict()

        # funktsioon, mis leiab kysimuse koodi järgi kysimuse eest antud punktid
        # (kysimuse kood võib olla regulaaravaldis)
        def get_pt(kood):
            total = 0
            for key in responses:
                kv = responses[key]
                if re.match(kood + '$', key) and kv:
                    total += kv.toorpunktid or 0
            log.debug('pt(%s)=%s' % (kood, total))
            return total
        f_locals['pt'] = get_pt


        # funktsioon, mis leiab kysimuse koodi järgi pildil avamise ABI-nupu vajutamiste arvu
        # (kysimuse kood võib olla regulaaravaldis)
        def get_uncover_help_cnt(kood):
            cnt = 0
            for key in responses:
                kv = responses[key]
                if re.match(kood + '$', key) and kv:
                    if kv.kysimus.sisuplokk.tyyp == const.INTER_UNCOVER:
                        cnt += len([True for kvs in kv.kvsisud if kvs.kood2])
            return cnt
        f_locals['uncover_help_cnt'] = get_uncover_help_cnt
    
        # funktsioon, mis leiab kysimuse koodi järgi vastuste listi
        # (kysimuse kood võib olla regulaaravaldis)
        def get_val(kood):
            li = []
            for key in responses:
                kv = responses[key]
                if re.match(kood + '$', key) and kv:
                    baastyyp = kv.kysimus.tulemus.baastyyp
                    for kvs in kv.kvsisud:
                        if  baastyyp in (const.BASETYPE_INTEGER,
                                         const.BASETYPE_FLOAT,
                                         const.BASETYPE_STRING,
                                         const.BASETYPE_IDENTIFIER):
                            value = kvs.kood1 or kvs.sisu
                        elif baastyyp in (const.BASETYPE_PAIR,
                                          const.BASETYPE_DIRECTEDPAIR):
                            value = (kvs.kood1, kvs.kood2)
                        else:
                            value = None
                        if value:
                            if baastyyp == const.BASETYPE_INTEGER:
                                # float selleks juhuks, kui value on nt 1.0
                                try:
                                    value = int(float(value.replace(',','.')))
                                except ValueError:
                                    value = None
                                except OverflowError:
                                    value = None
                            elif baastyyp == const.BASETYPE_FLOAT:
                                try:
                                    value = float(value.replace(',','.'))
                                except ValueError:
                                    value = None
                                except OverflowError:
                                    value = None
                            li.append(value)
            if loendurid:
                for key in loendurid:
                    if re.match(kood + '$', key):
                        li.append(loendurid[key])
            return li
        f_locals['val'] = get_val

        # funktsioon leiab elemendile vastava järjekorranumbri jadas (algab 1-st) või 0
        def indexin(li, elem):
            if elem is None:
                return 0
            try:
                n = li.index(elem)
                return n+1
            except ValueError:
                return 0
        f_locals['indexin'] = indexin

        # funktsioon leiab nende jada liikmete arvu, millel on antud väärtus
        # nt:
        #   lenval([3,2,0,2]) = 3
        #   lenval([3,2,0,2],2) = 2
        def lenval(li, value=None):
            if value:
                f = lambda x: x==value
            else:
                f = bool
            return len(list(filter(f, li)))
        f_locals['lenval'] = lenval

        # funktsioon tagastab -1 (kui a < b) või 0 (kui a == b) või 1 (kui a > b)
        def cmp(a, b):
            return (a > b) - (a < b)
        f_locals['cmp'] = cmp

        return f_locals
        
    def get_sisuvaatamised(self, ylesanne, sisuvaatamised):
        tahised = {}
        for sp in ylesanne.sisuplokid:
            if sp.nahtavuslogi:
                tahised[sp.id] = sp.tahis or str(sp.seq)

        # funktsioon leiab sisuploki kuvamiste arvu
        def bvcount(tahis):
            cnt = 0
            for si in sisuvaatamised:
                b_tahis = tahised.get(si.sisuplokk_id)
                if b_tahis and re.match(tahis + '$', b_tahis):
                    cnt += si.nahtav_kordi or 0
            return cnt
        
        # funktsioon leiab sisuploki kuvamise koguaja sekundites
        def bvtime(tahis):
            cnt = 0
            for si in sisuvaatamised:
                b_tahis = tahised.get(si.sisuplokk_id)
                if b_tahis and re.match(tahis + '$', b_tahis):                
                    cnt += si.nahtav_aeg or 0
            return cnt

        return {'bvcount': bvcount,
                'bvtime': bvtime,
                }
