"""Lahendaja postitatud vastuste teisendamine tabeli Kysimusevastus kirjeteks
"""
import cgi
import html
import base64
from eis.lib.base import *
from eis.recordwrapper import RecordWrapper, MemKV, MemKS
from eis.s3file import s3file_save
log = logging.getLogger(__name__)
_ = i18n._

import requests
import threading
thread_local = threading.local()

# krati päringud
def get_rsession(handler, key):
    key = f'{key}_session'
    if not hasattr(thread_local, key):
        sess = requests.Session()
        http_proxy = handler.request.registry.settings.get('http_proxy')
        if http_proxy:
            proxies = {'https': http_proxy}
            sess.proxies.update(proxies)        
        setattr(thread_local, key, sess)
    return getattr(thread_local, key)

class BlockResponse(object):
    """Postitatud vastuste salvestamine vastuse kirjetena ja
    automaatne hindamine.
    """
    def __init__(self, handler):
        self.handler = handler
        self.request = handler and handler.request or None
        
    def gen_random_responses(self, ylesanne, responses):
        new_responses = {}
        random_values = {}

        data = []
        for sp in ylesanne.sisuplokid:
            if sp.tyyp == const.BLOCK_RANDOM:
                for kysimus in sp.kysimused:
                    kyslisa = kysimus.kyslisa
                    t = kysimus.tulemus
                    if kyslisa and t:
                        data.append((kysimus,
                                     kyslisa.min_vaartus,
                                     kyslisa.max_vaartus,
                                     kyslisa.samm,
                                     sp,
                                     t.baastyyp,
                                     t.ymard_komakohad))
        for k, min_v, max_v, step, sp, baastyyp, koma in data:
            kv = responses.get(k.kood)
            if kv:
                # juba varem genereeritud
                for ks in kv.kvsisud:
                    svalue = ks.sisu
                    if baastyyp == const.BASETYPE_FLOAT:
                        value = float(svalue)
                    else:
                        value = int(svalue)
                    random_values[kv.kood] = value
                    break
            else:
                # genereerime uue
                if baastyyp == const.BASETYPE_FLOAT:
                    value = random.uniform(min_v, max_v)
                    if koma:
                        value = round(value, koma)
                else:
                    min_v = int(min_v)
                    max_v = int(max_v)
                    if step:
                        value = random.randrange(min_v, max_v + 1, int(step))
                    else:
                        value = random.randint(min_v, max_v)
                random_values[k.kood] = value

                s_value = str(value)
                kv = MemKV.init_k(sp, k)
                ks = MemKS(seq=0, tyyp=const.RTYPE_STRING, sisu=s_value)
                kv.kvsisud.append(ks)
                new_responses[k.kood] = kv
                responses[k.kood] = kv
        return new_responses, random_values

    def gen_shuffle(self, ylesanne, responses):
        "Valikute segamise järjekorra genereerimine"
        def gen_jrk(valikud):
            jrk = [v.kood for v in valikud if not v.fikseeritud]
            random.shuffle(jrk)
            # lisame kindla asukohaga valikud
            for i in range(len(valikud)):
                v = valikud[i]
                if v.fikseeritud:
                    jrk.insert(i, v.kood)
            return jrk

        new_responses = {}

        data = []
        for sp in ylesanne.sisuplokid:
            for k in sp.kysimused:
                if k.segamini == True:
                    data.append((sp, k))
        for sp, k in data:
            kood = k.kood
            kv = responses.get(kood)
            if not kv:
                kv = MemKV.init_k(sp, k)
                responses[k.kood] = kv
            if not kv.valikujrk:
                # loome segamisjärjekorra
                kv.valikujrk = gen_jrk(list(k.valikud))
                new_responses[kood] = responses[kood] = kv
        return new_responses
        
    
    def format_response(self, ylesanne, params, sop):
        """Ülesandele antud vastuse salvestamine
        Kasutaja poolt lahendamise vormilt postitatud vastus
        teisendatakse uuele kujule responses, 
        mis on dict, milles kysimuse koodile vastab vastus
        Parameetrid:
        - ylesanne - mille vastused salvestada;
        - params on postitatud parameetritest eraldatud selle ülesande osa
        - sop näitab, miks salvestati
        """
        q_obj = lambda b, k: MemKV.init_k(b, k)
        varparams = {}
        responses = {}
        buf = ''

        # vastused, mille väljanimi on kujul R_<KOOD>, kus <KOOD> on kysimus.kood
        for key in params:
            if key.startswith(const.RPREFIX) and not key.endswith('_'):
                kood = key[len(const.RPREFIX):]
                li = kood.split('.')
                if len(li) > 1:
                    # pole põhivastus, sisaldab punkti ja väljanime
                    continue
                kysimus = ylesanne.get_kysimus(kood)
                if not kysimus:
                    log.debug('Ülesandes {id} pole küsimust koodiga {s}'.format(id=ylesanne.id, s=kood))
                    buf += _("Ülesandes {id} pole küsimust koodiga {s}").format(id=ylesanne.id, s=kood) + '\n'
                    continue
                response = params.get(key)
                block = kysimus.sisuplokk
                kv = self._decode_q_response(block, params, q_obj, kysimus, response)
                if kv:
                    responses[kood] = kv

        # vastused, mille väljanimi on sisuplokk.blockprefix*
        # ehk b<sisuplokk.id>_result*
        # sisuplokkides, kus pole igal kysimusel oma vastuse välja
        random_k_id = []
        for block in ylesanne.sisuplokid:
            b_responses = self.decode_block_response(block, params, q_obj, sop)
            responses.update(b_responses)
            if block.nahtavuslogi:
                # saadame vbtimer_bID klastrisse
                key = 'vbtimer_%s' % block.get_prefix()
                varparams[key] = params.get(key)
        
        str_responses, yv_vastuseta = self._text_responses(responses, ylesanne)
        # yv_vastuseta-väli tuleb salvestada kohe sooritamise ajal,
        # et saaks lahendajale kuvada, mitu ylesannet on tehtud

        buf += '%s\n' % '\n'.join(str_responses)
        return responses, buf, yv_vastuseta, varparams
    
    def _text_responses(self, responses, ylesanne):
        "Kustutatakse liigsed vastused ning kogutakse andmed tekstina kuvamiseks"
        str_responses = []
        yv_vastuseta = True
        for key in sorted(responses.keys()):
            kv = responses[key]
            kysimus = ylesanne.get_kysimus(None, kv.kysimus_id)
            tulemus = kysimus.tulemus
            kv_vastuseta = True
            if tulemus:
                for ks in kv.get_kvsisud():
                    value = ks.as_string()
                    if value:
                        if kysimus.rtf:
                            value = value.replace('\n', ' ')
                        try:
                            value = html.escape(value)
                        except Exception as ex:
                            log.debug('text_responses: ' +str(ex))
                            value = '*****'
                    str_responses.append('%s: %s' % (key, value))

                    if not ks.on_vastuseta(tulemus):
                        kv_vastuseta = False
                        yv_vastuseta = False
            kv.vastuseta = kv_vastuseta
        return str_responses, yv_vastuseta

    def _decode_q_response(self, block, params, q_obj, kysimus, response):
        "Küsimuse vastuse salvestamine"
        tulemus = kysimus.tulemus
        if tulemus and tulemus.naide:
            return
        baastyyp = tulemus and tulemus.baastyyp
        ctrl = BlockResponse.get(block, self.handler)
        kv = q_obj(block, kysimus)
        ctrl.save(block, response, params, kysimus, tulemus, baastyyp, kv)
        return kv

    def decode_block_response(self, block, params, q_obj, sop):
        """Leitakse vastused nendele plokkidele, mille korral on vastuse väljanimes
        blockresult.
        """
        responses = {}

        kv = None
        seq = -1

        ctrl = BlockResponse.get(block, self.handler)
        response, is_response = ctrl.get_b_response(block, params)
        if not is_response:
            # selle ploki vastuseid ei salvestata praegu
            return []
    
        buf = ''
        if isinstance(response, list) and \
           block.tyyp != const.INTER_GR_ORDASS:
            # kaitse selle vastu, kui brauser teeb väljad topelt
            response = _unique_response(response)
            
        return ctrl.save_b(block, response, params, q_obj)

    @classmethod
    def get(cls, block, handler):
        """Sisuploki sidumine oma tüübile vastava kontrolleriga.
        block 
           sisuploki mudeli objekt
        handler
           päriskontroller (handler)
        """
        t = block.tyyp
        clsname = '_' + block.type_name + 'Response'
        try:
            # ploki oma klass
            ctrl = eval(clsname)(handler)
        except NameError as ex:
            # baasklass
            log.debug(f'puudub {clsname}')
            ctrl = cls(handler)
        return ctrl

    def get_b_response(self, block, params):
        "Parameetritest leitakse ploki vastused"
            
        # vastuse vormiväljade nimed
        block_result = block.get_result()
        try:
            response = params[block_result] # getall
            return response, True
        except KeyError as ex:
            # selle sisuploki vastust parameetrite seas ei ole,
            # sest neid praegu ei salvestata
            return None, False
        
    def save(self, block, response, params, kysimus, tulemus, baastyyp, kv):
        "Küsimuse vastuse salvestamine (sisuplokitüüpides, milles salvestatakse küsimuste kaupa)"
        if not isinstance(response, list):
            response = [response]
        else:
            # kaitse selle vastu, kui brauser teeb väljad topelt
            response = _unique_response(response)

        for seq, r in enumerate(response):
            kv._current_seq += 1
            if baastyyp == const.BASETYPE_IDENTIFIER:
                ks = kv.set_kvsisu(kv._current_seq, const.RTYPE_IDENTIFIER, kood1=r)
            else:
                r = r.strip()
                if kysimus.sonadearv or (tulemus and tulemus.min_sonade_arv): 
                    sonade_arv = _count_words(r, kysimus.rtf)
                else:
                    sonade_arv = None
                ks = kv.set_kvsisu(kv._current_seq, const.RTYPE_STRING, sisu=r, sonade_arv=sonade_arv)
                
    def save_b(self, block, response, params, q_obj):
        "Sisuploki vastuste salvestamine (sisuplokitüüpides, milles salvestatakse sisuploki kaupa)"
        # üle laadimiseks
        raise Exception('{s} ei ole sisuploki kaupa salvestamiseks'.format(s=block.type_name))
    
class _rubricBlockResponse(BlockResponse):
    def save_b(self, block, response, params, q_obj):
        # alusteksti kommentaarid
        responses = {}
        kysimus = block.get_kysimus()
        if kysimus:
            kv = q_obj(block, kysimus)
            kv._current_seq = seq = 0
            kv.set_kvsisu(kv._current_seq, const.RTYPE_STRING, sisu=response)
            responses[kysimus.kood] = kv
        return responses
    
class _headerResponse(BlockResponse):
    pass
class _googlechartsResponse(BlockResponse):
    pass
class _mathResponse(BlockResponse):
    pass
class _wmathResponse(BlockResponse):
    pass
class _mediaInteractionResponse(BlockResponse):
    pass
class _imageResponse(BlockResponse):
    pass
class _customInteractionResponse(BlockResponse):
    pass

class _geogebraInteractionResponse(BlockResponse):
    def save(self, block, response, params, kysimus, tulemus, baastyyp, kv):
        kv._current_seq = 0
        if response:
            filedata = base64.b64decode(response)
            filename = 'geogebra-response.ggb'
            ks = kv.set_kvsisu(kv._current_seq, const.RTYPE_FILE, filename=filename, filedata=filedata)
            

class _desmosInteractionResponse(BlockResponse):
    def save(self, block, response, params, kysimus, tulemus, baastyyp, kv):
        kv._current_seq = 0
        if response:
            state = response
            filename = 'desmos.json'
            filedata = state.encode('utf-8')
            kv.set_kvsisu(kv._current_seq, const.RTYPE_FILE, filename=filename, filedata=filedata)

class _match2InteractionResponse(BlockResponse):
    def save_b(self, block, response, params, q_obj):
        responses = {}
        kysimus1 = block.get_baaskysimus(seq=1)
        khulk_seq = kysimus1.ridu

        bresponses = dict()
        if response:
            response = response.strip(';').split(';')
            # responses listi element on kujul "KOOD1 KOOD2 ID1 ID2 MAATRIKS"
            # kus MAATRIKS=1, siis: 1 - hulga 1 valik, 2 - hulga 2 valik
            for r in response:
                try:
                    kood1, kood2, id1, id2, maatriks = r.split(' ')
                except:
                    continue
                else:
                    #maatriks = int(maatriks)
                    if khulk_seq == 2:
                        k_kood = kood2
                        v_kood = kood1
                    else:
                        k_kood = kood1
                        v_kood = kood2
                    if not bresponses.get(k_kood):
                        bresponses[k_kood] = [v_kood]
                    else:
                        bresponses[k_kood].append(v_kood)

        for kysimus in block.pariskysimused:
            response = bresponses.get(kysimus.kood) or []
            #buf += _("Sisuploki {s1} küsimuse {s2} ({s3}) vastus").format(s1=block.id, s2=kysimus.id, s3=kysimus.kood) +\
            #    ':%s\n' % (response)
            responses[kysimus.kood] = kv = q_obj(block, kysimus)                    
            for v_kood in response:
                kv._current_seq += 1
                kv.set_kvsisu(kv._current_seq, const.RTYPE_IDENTIFIER, kood1=v_kood)
        return responses
    
class _match3InteractionResponse(BlockResponse):
    # vana kolme hulgaga sobitamine
    def save_b(self, block, response, params, q_obj):
        responses = {}
        kysimus = block.get_kysimus(seq=1)

        # responses listi element on kujul "KOOD1 KOOD2 ID1 ID2 MAATRIKS"
        # kui MAATRIKS=1, siis: 1 - hulga 1 valik, 2 - hulga 2 valik
        # kui MAATRIKS=2, siis: 1 - hulga 2 valik, 2 - hulga 3 valik
        kv = q_obj(block, kysimus)
        if response:
            # parameetrites on antud paarid
            response = response.strip(';').split(';')
            seq = 0
            for r in response:
                try:
                    kood1, kood2, id1, id2, maatriks = r.split(' ')
                except:
                    continue
                else:
                    maatriks = int(maatriks)
                    vahetada = maatriks == 2
                    kv._current_seq += 1
                    kv.set_kvsisu(kv._current_seq, const.RTYPE_PAIR, kood1=kood1, kood2=kood2, maatriks=maatriks, vahetada=vahetada, paarina=False)
                    seq += 1

            # lisame juurde hulga1 ja hulga3 koodide paarid,
            # mis on määratud hulga1 ja hulga2 ning hulga2 ja hulga3 paaride poolt,
            # aga mida võidakse eraldi hindamismaatriksiga hinnata
            responses1 = [ks for ks in kv.get_kvsisud() if ks.maatriks==1]
            responses2 = [ks for ks in kv.get_kvsisud() if ks.maatriks==2]
            for r1 in responses1:
                for r2 in responses2:
                    if r1.kood2 == r2.kood1:
                        kv._current_seq += 1
                        kv.set_kvsisu(kv._current_seq, const.RTYPE_PAIR, kood1=r1.kood1, kood2=r2.kood2, maatriks=3, paarina=False)
                        seq += 1

        responses[kysimus.kood] = kv
        return responses

class _match3aInteractionResponse(BlockResponse):
    def save_b(self, block, response, params, q_obj):
        responses = {}
        # uus kolme hulgaga sobitamine
        kysimus = block.get_kysimus(seq=1)
        response = (response or '').strip(';').split(';')

        # jagame vastused kysimuste kaupa
        response2 = {}
        for r in response:
            # responses listi element on kujul "KOOD1 KOOD2 ID1 ID2 MAATRIKS"
            # kui MAATRIKS=1, siis: 1 - hulga 1 valik, 2 - hulga 2 valik
            # kui MAATRIKS=2, siis: 1 - hulga 2 valik, 2 - hulga 3 valik
            try:
                kood1, kood2, id1, id2, paper = r.split(' ')
            except ValueError as ex:
                # tyhi vastus
                continue
            else:
                paper = int(paper)
                if paper == 1:
                    kood = kood2 + '_H1'
                    vkood = kood1
                else:
                    kood = kood1 + '_H3'
                    vkood = kood2
                if kood not in response2:
                    response2[kood] = []
                response2[kood].append(vkood)

        for kysimus in block.pariskysimused:
            kv = q_obj(block, kysimus)
            k_kood = kysimus.kood
            log.debug(f'kood={k_kood}')
            k_responses = response2.get(k_kood) or []
            for vkood in k_responses:
                kv._current_seq += 1
                kv.set_kvsisu(kv._current_seq, const.RTYPE_IDENTIFIER, kood1=vkood)
                log.debug(f'{kysimus.kood} {kv._current_seq}: {vkood}')
            responses[kysimus.kood] = kv
        return responses

class _match3bInteractionResponse(BlockResponse):
    def save_b(self, block, response, params, q_obj):
        responses = {}
        # kolme hulgaga sobitamine kolmikute hindamisega
        kysimus = block.get_kysimus(seq=1)
        response = (response or '').strip(';').split(';')        

        # uus
        # jagame vastused kysimuste kaupa
        valik1 = {}
        valik3 = {}
        for r in response:
            # responses listi element on kujul "KOOD1 KOOD2 ID1 ID2 MAATRIKS"
            # kui MAATRIKS=1, siis: 1 - hulga 1 valik, 2 - hulga 2 valik
            # kui MAATRIKS=2, siis: 1 - hulga 2 valik, 2 - hulga 3 valik
            try:
                kood1, kood2, id1, id2, maatriks = r.split(' ')
            except ValueError as ex:
                continue
            else:
                maatriks = int(maatriks)
                if maatriks == 1:
                    valik1[kood2] = kood1
                else:
                    valik3[kood1] = kood2

        for kysimus in block.pariskysimused:
            kv = q_obj(block, kysimus)
            kood = kysimus.kood
            kood1 = valik1.get(kood)
            kood3 = valik3.get(kood)
            kv._current_seq += 1
            kv.set_kvsisu(kv._current_seq, const.RTYPE_PAIR, kood1=kood1, kood2=kood3)
            responses[kysimus.kood] = kv
        return responses
    
class _choiceInteractionResponse(BlockResponse):
    pass
class _mchoiceInteractionResponse(BlockResponse):
    pass

class _associateInteractionResponse(BlockResponse):
    def get_b_response(self, block, params):
        is_response = False
        block_result = block.get_result()
        kysimus = block.kysimus
        response = []
        for seq in range(kysimus.max_vastus):
            try:
                kood1 = params['%s_%s_1' % (block_result, seq)]
                kood2 = params['%s_%s_2' % (block_result, seq)]
            except KeyError as ex:
                pass
            else:
                is_response = True
                if kood1 and kood2:
                    response.append((kood1, kood2))
        return response, is_response
    
    def save_b(self, block, response, params, q_obj):
        responses = {}
        kysimus = block.kysimus
        # iga koodi jaoks on oma vastus
        kv = q_obj(block, kysimus)
        for kood1, kood2 in response:
            # tahame välistada nii None kui ka ''
            if kood1 and kood2:
                kv._current_seq += 1
                kv.set_kvsisu(kv._current_seq, const.RTYPE_PAIR, kood1=kood1, kood2=kood2, paarina=False)
        responses[kysimus.kood] = kv
        return responses

class _orderInteractionResponse(BlockResponse):
    def save(self, block, response, params, kysimus, tulemus, baastyyp, kv):
        if response:
            response = response.strip(';').split(';')
            jarjestus = []
            for r in response:
                # r on kujul "i_VALIKID"
                valik_id = r[2:]
                v = model.Valik.get(valik_id)
                if v and v.kysimus_id == kysimus.id:
                    jarjestus.append(v.kood)
            kv._current_seq = 0
            kv.set_kvsisu(kv._current_seq, const.RTYPE_ORDERED, jarjestus=jarjestus)
                
class _hottextInteractionResponse(BlockResponse):
    def save(self, block, response, params, kysimus, tulemus, baastyyp, kv):
        "Küsimuse vastuse salvestamine"
        # vastus eraldatakse semikoolonitega 
        if response:
            response = response.strip(';').split(';')
            for seq, r in enumerate(response):
                kv._current_seq += 1
                ks = kv.set_kvsisu(kv._current_seq, const.RTYPE_IDENTIFIER, kood1=r)

class _colortextInteractionResponse(BlockResponse):
    def save(self, block, response, params, kysimus, tulemus, baastyyp, kv):        
        if response:
            response = response.strip(';').split(';')
        else:
            response = []

        for seq, r in enumerate(response):
            text_k, color_k = r.split(',')
            kv._current_seq += 1
            kv.set_kvsisu(kv._current_seq,
                          const.RTYPE_PAIR,
                          kood1=text_k,
                          kood2=color_k,
                          paarina=False)

class _inlineTextInteractionResponse(BlockResponse):
    pass

class _inlineChoiceInteractionResponse(BlockResponse):
    pass

class _punktInteractionResponse(BlockResponse):
    def save(self, block, response, params, kysimus, tulemus, baastyyp, kv):
        "Küsimuse vastuse salvestamine"
        # kogu lause analyysis kuvamiseks
        sentence = params.get(kysimus.result + '_a_')
        kv.set_kvsisu(const.SEQ_ANALYSIS, const.RTYPE_STRING, sisu=sentence)

        # leiame lynkade koodide ja indeksite vastavuse, et see info kirjutada vastusesse
        q = (model.Session.query(model.Hindamismaatriks.kood2,
                                 model.Hindamismaatriks.koordinaadid)
             .filter(model.Hindamismaatriks.tulemus_id==kysimus.tulemus_id)
             )
        map_pos = {seq: kood for (kood, seq) in q.all()}
        
        # vastused lynkade kaupa
        values = []
        for value in response.split('|'):
            if value:
                # lynga kood : lynka sisestatud kirjavahemärgid
                try:
                    seq, txt = value.split(':', 1)
                    txt = txt.replace('\xa0',' ')
                except:
                    log.error('ipunkt value %s' % value)
                else:
                    kood2 = map_pos.get(seq)
                    values.append((txt, kood2, seq))
        # baastyyp peab olema const.RTYPE_POSSTRING
        seq = -1
        for seq, r in enumerate(values):
            kv._current_seq += 1
            sisu, kood2, seq = r
            kv.set_kvsisu(kv._current_seq,
                          const.RTYPE_POSSTRING,
                          sisu=sisu,
                          kood2=kood2,
                          koordinaat=seq,
                          analyysitav=False)

class _gapMatchInteractionResponse(BlockResponse):
    def get_b_response(self, block, params):
        "Leitakse plokina salvestamise vastused (kui on lünkadeta)"
        bkysimus = block.get_kysimus(seq=0)
        response = []
        is_response = False
        if bkysimus.gap_lynkadeta:
            # igal lyngal oma väli
            block_result = block.get_result()
            if block_result in params:
                # vastus on olemas
                is_response = True
                prefix = block_result + '_'
                for (key, values) in params.items():
                    if key.startswith(prefix):
                        lynk_kood = key[len(prefix):]
                        response.append((lynk_kood, values))
        else:
            is_response = None
        return response, is_response
            
    def save(self, block, response, params, kysimus, tulemus, baastyyp, kv):
        # lynkadega variant
        response2 = params.get(const.RPREFIX + kysimus.kood)
        jarjestus = (response2 or '').split(',')

        # kas teha eraldi analyysikirje
        is_analysis = tulemus and tulemus.kardinaalsus in (const.CARDINALITY_ORDERED, const.CARDINALITY_ORDERED_SQ1, const.CARDINALITY_ORDERED_POS)
        if is_analysis:
            kv.set_kvsisu(const.SEQ_ANALYSIS, const.RTYPE_ORDERED, jarjestus=jarjestus)
            kv._current_seq = -1
        for value in jarjestus:
            kv._current_seq += 1
            kv.set_kvsisu(kv._current_seq, const.RTYPE_IDENTIFIER, kood1=value, analyysitav=not is_analysis)
            
    def save_b(self, block, response, params, q_obj):
        bkysimus = block.get_kysimus(seq=0)
        if bkysimus.gap_lynkadeta:
            # lynkadeta variant

            map_seq2k = dict()
            for kysimus in block.kysimused:
                if kysimus != bkysimus:
                    map_seq2k[kysimus.seq] = kysimus

            responses = {}
            prefix = block.get_result() + '_'
            bseq = 0
            bkv = q_obj(block, bkysimus)
            for (lynk_kood, values) in response:
                    assert lynk_kood.startswith('_seq'), 'ootamatu kood %s' % lynk_kood
                    k_seq = lynk_kood[4:]
                    jarjestus = (values or '').split(',')
                    kysimus = map_seq2k.get(int(k_seq))
                    if kysimus:
                        # lynka viidi
                        kv = q_obj(block, kysimus)
                        # kas teha eraldi analyysikirje
                        is_analysis = kysimus.tulemus.kardinaalsus in (const.CARDINALITY_ORDERED, const.CARDINALITY_ORDERED_SQ1, const.CARDINALITY_ORDERED_POS)
                        if is_analysis:
                            kv.set_kvsisu(const.SEQ_ANALYSIS, const.RTYPE_ORDERED, jarjestus=jarjestus, kood2=k_seq)                        
                        for value in jarjestus:
                            kv._current_seq += 1
                            kv.set_kvsisu(kv._current_seq, const.RTYPE_IDENTIFIER, kood1=value, sisu=k_seq, analyysitav=not is_analysis)
                        responses[kysimus.kood] = kv                            
                    else:
                        # sõnade vahe, kus pole lynka
                        for value in jarjestus:
                            bkv._current_seq += 1
                            bkv.set_kvsisu(bkv._current_seq, const.RTYPE_IDENTIFIER, kood1=value, sisu=k_seq)                            
                        bseq += 1
            responses[bkysimus.kood] = bkv
            return responses
    
class _textEntryInteractionResponse(BlockResponse):
    pass
class _extendedTextInteractionResponse(BlockResponse):
    pass
class _crosswordResponse(BlockResponse):
    pass
class _mathInteractionResponse(BlockResponse):
    pass
class _wmathInteractionResponse(BlockResponse):
    pass
class _sliderInteractionResponse(BlockResponse):
    pass

class _positionObjectInteractionResponse(BlockResponse):
    def save_b(self, block, response, params, q_obj):
        responses = {}
        # igal ploki piltobjektil oma vastus
        # responses listi element on kujul "PILDIKOOD x y"
        if response:
            response = response.strip(';').split(';')            
            for r in response:
                try:
                    pildikood, x, y = r.split(' ')
                except:
                    continue
                else:
                    if pildikood not in responses:
                        kysimus = block.get_kysimus(kood=pildikood)
                        if not kysimus:
                            log.error('Sisuplokis %s (%s) pole kysimust %s' % (block.seq, block.id, pildikood))
                        kv = q_obj(block, kysimus)
                        responses[pildikood] = kv
                    else:
                        kv = responses[pildikood]
                    kv._current_seq += 1
                    kv.set_kvsisu(kv._current_seq, const.RTYPE_POINT, punkt=(x,y))
        return responses

class _positionObject2InteractionResponse(BlockResponse):
    def save_b(self, block, response, params, q_obj):
        responses = {}
        # igal tekstil oma vastus
        # responses listi element on kujul "PILDIKOOD x y"
        if response:
            response = response.strip(';').split(';')                        
            if block.tyyp == const.INTER_TXPOS2:
                prkkysimus = block.get_baaskysimus(2)
            else:
                prkkysimus = block.get_baaskysimus(1)                    
            for r in response:
                try:
                    vkood, x, y = r.split(' ')
                    x = int(float(x))
                    y = int(float(y))
                except:
                    continue
                else:
                    # leiame piirkonna, kuhu tekst lohistati
                    prk_kood = _get_prk(x, y, prkkysimus)
                    # salvestame vastuse
                    if vkood not in responses:
                        kysimus = block.get_kysimus(kood=vkood)
                        if not kysimus:
                            log.error('Sisuplokis %s (%s) pole kysimust %s' % (block.seq, block.id, vkood))
                        kv = q_obj(block, kysimus)
                        responses[vkood] = kv
                    else:
                        kv = responses[vkood]
                    kv._current_seq += 1
                    kv.set_kvsisu(kv._current_seq, const.RTYPE_IDENTIFIER, kood1=prk_kood, punkt=(x,y))
        return responses
    
class _positionTextInteractionResponse(_positionObjectInteractionResponse):
    pass

class _txpos2InteractionResponse(_positionObject2InteractionResponse):
    pass

class _txgapInteractionResponse(BlockResponse):
    def save_b(self, block, response, params, q_obj):
        responses = {}
        # response listi element on kujul "TEXTID[#n] X Y PIIRKONDID"
        # teisendame kujule (TEXTID, PIIRKONDID, 'x,y'), 
        if response:
            seq = 0
            response = response.strip(';').split(';')
            for r in response:
                try:
                    obj_id, x, y, hotspot_id = r.split(' ')
                except:
                    continue
                else:
                    if obj_id.find('#') > -1:
                        # kui pilti on mitu tükki, siis eraldamiseks paneb area.js id lõppu #N
                        obj_id = obj_id[:obj_id.find('#')]
                    kv = responses.get(obj_id)
                    if not kv:
                        kysimus = block.get_kysimus(kood=obj_id)
                        if not kysimus:
                            log.error('Sisuplokis %s (%s) pole kysimust %s' % (block.seq, block.id, obj_id))
                        responses[obj_id] = kv = q_obj(block, kysimus)
                    kv._current_seq += 1
                    kv.set_kvsisu(kv._current_seq, const.RTYPE_IDENTIFIER, kood1=hotspot_id, punkt=(x,y))
                    seq += 1
        return responses

class _txassInteractionResponse(_txgapInteractionResponse):
    def save_b(self, block, response, params, q_obj):
        responses = {}
        # response listi element on kujul "TEXTID PIIRKONDID"
        # teisendame kujule (TEXTID, PIIRKONDID)
        if response:
            seq = 0
            response = response.strip(';').split(';')
            for r in response:
                try:
                    obj_id, hotspot_id = r.split(' ')
                except:
                    continue
                else:
                    kv = responses.get(obj_id)
                    if not kv:
                        kysimus = block.get_kysimus(kood=obj_id)
                        if not kysimus:
                            log.error('Sisuplokis %s (%s) pole kysimust %s' % (block.seq, block.id, obj_id))
                        responses[obj_id] = kv = q_obj(block, kysimus)
                    kv._current_seq += 1
                    kv.set_kvsisu(kv._current_seq, const.RTYPE_IDENTIFIER, kood1=hotspot_id)
                    seq += 1
        return responses

class _drawingInteractionResponse(BlockResponse):
    def save(self, block, response, params, kysimus, tulemus, baastyyp, kv):
        if response and kysimus.joonistamine.on_arvutihinnatav:
            # arvutihinnatav joonistus
            response = response.strip(';').split(';')                        
            # response listi element on kujul "polyline [[x,y],[x,y],...[x,y]],"
            for r in response:
                try:
                    # polyline [[251,278],[377,100],[347,296],[217,122],[142,309]];
                    shape, coords = r.split(' ', 1) # polyline, line, ray
                    assert shape in ('polyline', 'line', 'ray'), 'vastuses vale kujund "{s}"'.format(s=shape)
                    m = re.findall('\[(\d+), ?(\d+)\]', coords)
                    li_coords = [[int(r[0]),int(r[1])] for r in m]
                except Exception as e:
                    log.debug(e)
                    continue
                else:
                    kv._current_seq += 1
                    kv.set_kvsisu(kv._current_seq, const.RTYPE_COORDS, koordinaadid=li_coords, kujund=shape)
        else:
            # käsitsihinnatav joonistus
            kv.set_kvsisu(kv._current_seq, const.RTYPE_STRING, sisu=response)
                
                    
class _graphicGapMatchInteractionResponse(BlockResponse):
    def save_b(self, block, response, params, q_obj):
        responses = {}
        # response listi element on kujul "PILTID[#n] X Y PIIRKONDID"
        # teisendame kujule (PILTID, PIIRKONDID, 'x,y'), 
        kysimus = block.kysimus
        kv = q_obj(block, kysimus)
        if response:
            seq = 0
            response = response.strip(';').split(';')                        
            for r in response:
                try:
                    obj_id, x, y, hotspot_id = r.split(' ')
                except:
                    continue
                else:
                    if obj_id.find('#') > -1:
                        # kui pilti on mitu tükki, siis eraldamiseks paneb area.js id lõppu #N
                        obj_id = obj_id[:obj_id.find('#')]

                    kv._current_seq += 1
                    kv.set_kvsisu(kv._current_seq, const.RTYPE_PAIR, kood1=obj_id, kood2=hotspot_id, punkt=(x,y), paarina=False)
                    seq += 1
        responses[kysimus.kood] = kv
        return responses

class _colorareaResponse(BlockResponse):
    pass

class _uncoverResponse(BlockResponse):
    def save(self, block, response, params, kysimus, tulemus, baastyyp, kv):
        "Küsimuse vastuse salvestamine"
        kv._current_seq += 1
        ks = kv.set_kvsisu(kv._current_seq, const.RTYPE_STRING, sisu=response)
        # pildi avamise abi kasutamise arv
        ks.kood2 = params.get(kysimus.result + '_hlp_')

class _trailInteractionResponse(BlockResponse):
    def save(self, block, response, params, kysimus, tulemus, baastyyp, kv):        
        # response listi element on kujul "PILTID[#n] X Y PIIRKONDID"
        # salvestame samal kujul tekstina
        kv._current_seq += 1
        kv.set_kvsisu(kv._current_seq, const.RTYPE_STRING, sisu=response)

class _hotspotInteractionResponse(BlockResponse):
    def save(self, block, response, params, kysimus, tulemus, baastyyp, kv):
        if response:
            # response on list valitud piirkondade koodidest
            response = response.strip(';').split(';')
            for seq, r in enumerate(response):
                kv._current_seq += 1
                kv.set_kvsisu(kv._current_seq, const.RTYPE_IDENTIFIER, kood1=r)
    
class _graphicOrderInteractionResponse(BlockResponse):
    def save(self, block, response, params, kysimus, tulemus, baastyyp, kv):    
        if response:
            jarjestus = response.strip(';').split(';')
            # response on list järjestatud piirkondade koodidest
            kv._current_seq = 0
            kv.set_kvsisu(kv._current_seq, const.RTYPE_ORDERED, jarjestus=jarjestus)
    
class _graphicOrdAssociateInteractionResponse(BlockResponse):
    "Võrguülesanne"
    def save_b(self, block, response, params, q_obj):
        responses = {}
        kysimus = block.kysimus
        kv = q_obj(block, kysimus)
        if response:
            response = response.strip(';').split(';')
            # response on list järjestatud piirkondade koodidest
            kv._current_seq = 0
            kv.set_kvsisu(kv._current_seq, const.RTYPE_ORDERED, jarjestus=response)
            responses[kysimus.kood] = kv
        # valede vastuste loenduriga
        cnt_incorrect = 0
        if response:
            seq = 0
            try:
                # RecordWrapper
                entries = kysimus.list_correct_entries
            except AttributeError:
                # Kysimus
                entries = kysimus.correct_entries()
            correct = [entry.kood1 for entry in entries]
            for kood in response:
                if correct and kood == correct[0]:
                    correct.pop(0)
                else:
                    cnt_incorrect += 1

        # valede vastuste arv läheb kysimus2 vastuseks
        kysimus2 = block.get_kysimus(seq=2)
        kv2 = q_obj(block, kysimus2)
        kv2._current_seq = 0                        
        kv2.set_kvsisu(kv._current_seq, const.RTYPE_STRING, sisu=str(cnt_incorrect))
        responses[kysimus2.kood] = kv2
        return responses
    
class _selectPointInteractionResponse(BlockResponse):
    def save(self, block, response, params, kysimus, tulemus, baastyyp, kv):
        # response listi element on kujul "X Y"
        if response:
            response = response.strip(';').split(';')                        
            for r in response:
                try:
                    x, y = r.split(' ')
                except:
                    continue
                else:
                    kv._current_seq += 1                        
                    kv.set_kvsisu(kv._current_seq, const.RTYPE_POINT, punkt=(x,y))

class _select2PointInteractionResponse(BlockResponse):
    def save(self, block, response, params, kysimus, tulemus, baastyyp, kv):        
        if response:
            response = response.strip(';').split(';')
            prkkysimus = block.get_baaskysimus(1)
            for r in response:
                try:
                    x, y = r.split(' ')
                    x = int(float(x))
                    y = int(float(y))
                except Exception as ex:
                    log.debug('ex %s' % ex)
                    continue
                else:
                    # leiame piirkonna, kuhu tekst lohistati
                    prk_kood = _get_prk(x, y, prkkysimus)
                    # salvestame vastuse
                    kv._current_seq += 1
                    kv.set_kvsisu(kv._current_seq, const.RTYPE_IDENTIFIER, kood1=prk_kood, punkt=(x,y), paarina=False)

class _graphicAssociateInteractionResponse(BlockResponse):
    def save(self, block, response, params, kysimus, tulemus, baastyyp, kv):        
        # response listi element on kujul "HOTSPOT_ID1 HOTSPOT_ID2"
        if response:
            response = response.strip(';').split(';')                        
            for r in response:
                try:
                    id1, id2 = r.split(' ')
                except:
                    continue
                else:
                    kv._current_seq += 1                        
                    kv.set_kvsisu(kv._current_seq, const.RTYPE_PAIR, kood1=id1, kood2=id2, paarina=False)
    
class _audioInteractionResponse(BlockResponse):
    def save(self, block, response, params, kysimus, tulemus, baastyyp, kv):
        "Küsimuse vastuse salvestamine"
        if isinstance(response, (cgi.FieldStorage, model_s.TFileStorage)):
            try:
                filedata = response.value
                filename = _fn_local(response.filename) or 'file'
            except Exception as ex:
                # fail on ainult ylesande vormilt salvestamisel
                # testi vormilt salvestades faili enam ei ole
                log.error('audio vastus: %s' % ex)
            else:
                # kui fail saadi, siis see salvestatakse (fail on olemas ainult sop=file korral)
                kv._current_seq += 1
                kv.set_kvsisu(kv._current_seq, const.RTYPE_FILE, filename=filename, filedata=filedata)
                model.Session.flush()
        else:
            # peale esimest salvestamist rohkem faili ei saadeta
            kv._current_seq = len(kv.kvsisud) - 1
            
class _uploadInteractionResponse(BlockResponse):
    def save(self, block, response, params, kysimus, tulemus, baastyyp, kv):
        seq = 0
        kv._current_seq = 0
        filedata = filename = None
        if isinstance(response, (cgi.FieldStorage, model_s.TFileStorage)):
            try:
                filedata = response.value
                filename = _fn_local(response.filename)
            except Exception as ex:
                # fail on ainult ylesande vormilt salvestamisel
                # testi vormilt salvestades faili enam ei ole
                log.error('upload vastus: %s' % ex)
        if filedata:
            # kui fail saadi, siis see salvestatakse
            kv.set_kvsisu(kv._current_seq, const.RTYPE_FILE, filename=filename, filedata=filedata)

class _krattResponse(BlockResponse):
    def save(self, block, response, params, kysimus, tulemus, baastyyp, kv):
        "Küsimuse vastuse salvestamine"
        # response on vastuse staatuse pärimise URL
        file_url = response
        if file_url:
            kv._current_seq += 1
            ks = kv.set_kvsisu(kv._current_seq, const.RTYPE_FILE, koordinaat=file_url)
            # hiljem päritakse URL ja lisatakse filedata ja sisu
            model.Session.flush()
            # kohe ei saa pärida, sest ks.id puudub
            #kratt_download(self.handler, ks)

def kratt_download(handler, ks):
    "Proovitakse alla laadida krati tulemus"
    file_url = ks.koordinaat
    if file_url and not (ks.has_file or ks.sisu):
        # päritakse staatus, kas on valmis
        log.debug(f'kratt status: {file_url}')
        rsession = get_rsession(handler, 'kratt')
        try:
            res = rsession.get(file_url, timeout=10)
        except Exception as ex:
            if handler:
                handler._error(ex, 'kratt status', rollback=False)
            else:
                log.error(ex)
            return
        else:
            log.debug(f'kratt status resp: {res.text}')
            result = res.json()

        # status: pending/success
        status = result.get('status')
        if status == 'success':
            # valmis sai, saab laadida MP3 ja transkriptsiooni
            mp3_url = result.get('file_url')
            ks.sisu = result.get('transcription')
            if mp3_url:
                log.debug(f'kratt mp3: {mp3_url}')
                try:
                    res = rsession.get(mp3_url, timeout=10)
                except Exception as ex:
                    if handler:
                        handler._error(ex, 'kratt get', rollback=False)
                    else:
                        log.error(ex)
                else:
                    ks.filename = 'vastus.mp3'
                    s3file_save('kvsisu', ks, res.content)
            return True
            
class _formulaResponse(BlockResponse):
    def get_b_response(self, block, params):
        # valemi korral tagastame, et vastus on olemas, et hiljem jõutaks save_b-sse
        return None, True

    def save_b(self, block, response, params, q_obj):
        # loome ainult Kysimusevastus kirje
        # vastused genereerime peale kasutaja vastuste hindamist
        responses = {}
        kysimus = block.kysimus
        kv = q_obj(block, kysimus)
        kv._current_seq = 0
        responses[kysimus.kood] = kv
        return responses
    
class _randomResponse(BlockResponse):
    pass

def _unique_response(response):
    # kaitse selle vastu, kui IE brauser teeb välju topelt
    new_response = []
    for r in response:
        if r not in new_response:
            new_response.append(r)
    return new_response

def _count_words(value, is_rtf):
    "Vastuse sõnade arvu kokkulugemine"
    if is_rtf:
        value = re.sub('<[^<]*>', '', value or '').replace('&amp;nbsp;', ' ').replace('&nbsp;', ' ')
    value = ' ' + re.sub('[-–]+', '', value or '') + ' '
    li = re.split('[\s.,;:\-!?/]+', value)
    cnt = len(li) - 2
    return cnt

def _get_prk(x, y, prkkysimus):
    "Leiame esimese piirkonna, kuhu vastus sattus"
    prk_kood = const.VALIK_X
    #log.debug('X=%s, Y=%s prk %s' % (x, y, prkkysimus.id))
    if prkkysimus:
        for prk in prkkysimus.valikud:
            if model.util.point_in_shape(x, y, prk.koordinaadid, prk.kujund):
                #log.debug('prk %s ? %s' % (prk.koordinaadid, prk.kood))
                prk_kood = prk.kood
                break
        return prk_kood

def _fn_local(fnPath):
    """
    Rajast eraldatakse failinimi.
    """
    pos = max(fnPath.rfind('\\'), fnPath.rfind('/'))
    if pos > -1:
        return fnPath[pos + 1:]
    else:
        return fnPath

