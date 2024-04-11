# -*- coding: utf-8 -*- 
# $Id: blockentry.py 1197 2017-02-13 14:51:18Z ahti $
"""Sisestaja sisestatud või skannimisel tuvastatud p-testi vastuste 
teisendamine tabeli Kysimusevastus kirjeteks
"""

from eis.lib.block import BlockController
from eis.lib.base import *
import eis.lib.helpers as helpers

log = logging.getLogger(__name__)

class BlockEntry(object):
    """Vastuste sisestamine.
    """
    def __init__(self, handler, prefix=None):
        self.handler = handler
        self.prefix = prefix # väljade prefiks, mida kasutada välja puudumisest teatamisel
        self.sisestamata = False
        self.error = None

    def save_entry(self, ylesandevastus, vy, params, sisestus, sisestusviis, validate=False):
        """Ülesandele antud vastuse sisestuse salvestamine
        """
        #log.debug('SAVE_ENTRY %s START' % ylesandevastus.id)
        ylesanne = vy.ylesanne
        responses, buf = \
                   self.decode_entry(ylesanne, params, ylesandevastus, sisestus, sisestusviis, 
                                     validate=validate)

        sisestatud_kysimuste_koodid = list(responses.keys())
        # eemaldame varasemast jäänud vastused, mida praegu ei salvestatud
        for kv2 in ylesandevastus.kysimusevastused:
            if kv2.sisestus == sisestus: # varasem sisestus
                kysimus2 = kv2.kysimus
                if kysimus2.kood not in sisestatud_kysimuste_koodid or \
                   kysimus2.sisuplokk.ylesanne_id != ylesanne.id:
                    # andmebaasis on vastus sellise koodiga kysimusele, millele praegu vastust ei sisestatud
                    # või
                    # andmebaasis on vastus sellisele kysimusele, mis pole yldse samast ylesandest (muu komplekt)
                    kv2.delete()

        return responses

    def decode_entry(self, item, params, ylesandevastus, sisestus, sisestusviis, validate=False):
        """Postitatud parameetrites olevad vastused salvestatakse kysimusevastuse kirjetena
        """
        responses = {}
        buf = ''
        
        for kood in params:
            #log.debug('decode_entry kood=%s' % kood)
            response = params.get(kood) # getall
            if not isinstance(response, list):
                response = [response]
            
            kysimus = item.get_kysimus(kood)
            #log.debug('decode_entry kysimus=%s' % (kysimus and kysimus.id))
            if not kysimus:
                log.debug('Ülesandes %s pole küsimust koodiga %s' % (item.id, kood))
                buf += 'Ülesandes %s pole küsimust koodiga %s\n' % (item.id, kood)
                continue

            if sisestusviis == const.SISESTUSVIIS_OIGE or not kysimus.sisuplokk.on_sisestatav:
                responses[kood] = self.decode_kysimus_correct(ylesandevastus, sisestus, kysimus, response)
            else:
                responses[kood] = self.decode_kysimus_entry(ylesandevastus, sisestus, kysimus, response, 
                                                            validate=validate)

        str_responses = []
        for key in responses:
            kv = responses[key]
            if kv:
                for ks in kv.kvsisud:
                    str_responses.append('%s: %s' % (key, ks.as_string()))
        buf += '%s\n' % '\n'.join(str_responses)
        #log.debug(u'Vastused:\n%s' % '\n'.join(str_responses))
        return responses, buf

    def decode_kysimus_entry(self, ylesandevastus, sisestus, kysimus, response, validate=False):
        """Sisestatud vastuste salvestamine
        """
        def q_obj(kysimus, sisestus):
            assert kysimus, 'Küsimus puudub'
            kv = ylesandevastus.give_kysimusevastus(kysimus.id, sisestus)
            return kv

        def _validate(kysimus, values, kood):
            if kood not in values:
                log.error('Vigane vastuse kood %s (ülesanne %s, küsimus %s, lubatud koodid: %s)' % \
                              (kood, kysimus.sisuplokk.ylesanne_id, kysimus.kood, ','.join(values)))
                return False
            else:
                return True

        tulemus = kysimus.tulemus
        baastyyp = tulemus and tulemus.baastyyp
        plokk = kysimus.sisuplokk
        kv = None
        #log.debug('tyyp=%s, %s' % (plokk.tyyp, str(response)))

        if plokk.tyyp == const.INTER_ORDER or plokk.tyyp == const.INTER_GR_ORDER:
            #log.debug('decode_kysimus_entry IN ORDER')
            # sisestatud = False
            # oige = None
            # for x in response:
            #     if x:
            #         sisestatud = True
            #         if x.startswith('-'):
            #             oige = int(x[1:])
            #             break
            #if sisestatud:
            if validate:
                values = kysimus.list_kood1()

            not_validate = False
            for seq, x in enumerate(response):
                if validate and not _validate(kysimus, values, x):
                    not_validate = True
                if not x:
                    self._sisestamata(kysimus, seq, '')

            if len([x for x in response if x]) > 0:
                # kui vastus on sisestatud
                kv = q_obj(kysimus, sisestus)
                if not_validate:
                    kv.set_kvsisu(0, const.RTYPE_CORRECT, oige=const.C_LOETAMATU)
                else:
                    kv.set_kvsisu(0, const.RTYPE_ORDERED, jarjestus=response)
                
        elif baastyyp == const.BASETYPE_PAIR or baastyyp == const.BASETYPE_DIRECTEDPAIR:
            #log.debug('decode_kysimus_entry IN PAIR')
            # gr_associate
            # gr_gap
            # match
            # associate
            # gap
            if validate:
                values1 = plokk.kysimus.list_kood1()
                values2 = plokk.kysimus.list_kood2()

            # response on list koodide paaridest
            kv = q_obj(plokk.kysimus, sisestus)
            seq = -1
            for seq, r in enumerate(response):
                id1 = r.get('kood1')
                id2 = r.get('kood2')
                if id1 and id2:
                    if validate and \
                            (not _validate(plokk.kysimus, values1, id1) or \
                                 not _validate(plokk.kysimus, values2, id2)):
                        kv.set_kvsisu(seq, const.RTYPE_CORRECT, oige=const.C_LOETAMATU)
                    else:
                        kv.set_kvsisu(seq, const.RTYPE_PAIR, kood1=id1, kood2=id2)
                else:
                    if not id1:
                        self._sisestamata(plokk.kysimus, seq, 'kood1')
                    if not id2:
                        self._sisestamata(plokk.kysimus, seq, 'kood2')                        
            #log.debug('decode_kysimus_entry SAVED')                
            self._remove_old_kvsisu(kv, seq)
                    
        # elif plokk.tyyp == const.INTER_CHOICE and not kysimus.vastusesisestus:
        #     # sellised valikvastused, mida sisestati linnukestega, nagu lahendaja teeb
        #     kv = q_obj(kysimus, sisestus)
        #     for seq, r in enumerate(response):
        #         kood1 = 
        elif baastyyp == const.BASETYPE_IDENTIFIER:
            # hotspot, choice
            #log.debug('decode_kysimus_entry IN IDENTIFIER')
            kv = q_obj(kysimus, sisestus)
            if validate:
                values = kysimus.list_kood1()
            v_seq = -1
            for seq, r in enumerate(response):
                kood1 = r.get('kood1')
                if kood1:
                    #oige = kood1.startswith('-') and int(kood1[1:]) or None
                    # esialgu on oige=None, hiljem tulemuse arvutamisel määratakse                

                    v_seq += 1   
                    if validate and not _validate(kysimus, values, kood1):
                        kv.set_kvsisu(v_seq, const.RTYPE_CORRECT, oige=const.C_LOETAMATU)
                    else:
                        kv.set_kvsisu(v_seq, const.RTYPE_IDENTIFIER, kood1=kood1)
                else:
                    self._sisestamata(kysimus, seq, 'kood1')
            #log.debug('decode_kysimus_entry SAVED')                
            self._remove_old_kvsisu(kv, v_seq)

        elif baastyyp in (const.BASETYPE_STRING, const.BASETYPE_INTEGER, const.BASETYPE_FLOAT):
            # iinltext
            kv = q_obj(kysimus, sisestus)
            v_seq = -1
            for seq, r in enumerate(response):
                sisu = r.get('sisu')
                if sisu or tulemus and tulemus.lubatud_tyhi:
                    v_seq += 1   
                    if sisu == const.ENTRY_VASTAMATA_STR:
                        kv.set_kvsisu(v_seq, const.RTYPE_CORRECT, oige=const.C_VASTAMATA, sisu=None)
                    elif sisu == const.ENTRY_LOETAMATU_STR:
                        kv.set_kvsisu(v_seq, const.RTYPE_CORRECT, oige=const.C_LOETAMATU, sisu=None)
                    else:
                        kv.set_kvsisu(v_seq, const.RTYPE_STRING, sisu=sisu, oige=None)
                else:
                    self._sisestamata(kysimus, seq, 'sisu')

            self._remove_old_kvsisu(kv, v_seq) 

        else:
            raise Exception('Ei saa sisestada vastust (%s, %s)' % (plokk.tyyp, baastyyp))
        #log.debug('decode_kysimus_entry OUT')                

        if kv and tulemus:
            kv_vastuseta = True
            for ks in kv.kvsisud:
                if not ks.on_vastuseta(tulemus):
                    kv_vastuseta = False
                    break
            kv.vastuseta = kv_vastuseta
        return kv

    def decode_kysimus_correct(self, ylesandevastus, sisestus, kysimus, response):
        """Tekitatakse õige/vale sisestamise kirjed.
        """
        #log.debug('decode_kysimus_correct IN')
        kv = ylesandevastus.give_kysimusevastus(kysimus.id, sisestus)
        seq = -1
        for seq, r in enumerate(response):
            tyyp = const.RTYPE_CORRECT           
            kood1 = r.get('kood1') or None
            oige = r.get('oige')
            try:
                oige = int(oige)
            except:
                oige = None
                self._sisestamata(kysimus, seq, 'oige')
            kv.set_kvsisu(seq, const.RTYPE_CORRECT, kood1=kood1, oige=oige)
            
        #log.debug('decode_kysimus_entry SAVED')
        self._remove_old_kvsisu(kv, seq)
        #log.debug('decode_kysimus_entry OUT')        
        return kv

    def _sisestamata(self, kysimus, n, field):
        """Vastus on sisestamata.
        """
        self.sisestamata = True
        if self.prefix:
            prefix = '%s.r.%s-%d' % (self.prefix, kysimus.kood, n)
            if field:
                prefix += '.%s' % field
            
            self.handler.warnings[prefix] = 'Puudub'

    def _remove_old_kvsisu(self, kv, seq):
        """Peale kvsisude salvestamist kustutatakse varasemast salvestamisest jäänud
        vastused, mille indeks on suurem kui praegu salvestatud suurim indeks.
        """
        if kv:
            for seq2 in range(len(kv.kvsisud)-1, seq, -1):
                kv.kvsisud[seq2].delete()
