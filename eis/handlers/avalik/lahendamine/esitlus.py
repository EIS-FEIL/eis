from datetime import datetime, timedelta
import json
import base64
from eis.lib.baseresource import *
_ = i18n._
from eis.s3file import s3file_init
from eis.lib.blockview import BlockView
from eis.lib.blockresponse import BlockResponse, kratt_download
from eis.lib.examclient import ExamClient
from eiscore.recordwrapper import RecordWrapper
from eis.lib.testclient import TestClient
from eiscore.examwrapper import MemYlesandevastus, MemKV, MemKS
log = logging.getLogger(__name__)

class EsitlusController():
    _TASK_TEMPLATE = '/avalik/lahendamine/lahendamine.esitlus.mako'
    _TASK_MSG_TEMPLATE = '/avalik/lahendamine/esitlus.message.mako'
    
    # meetodid: edittask, showtask, correct, showtool, images, datafile

    def correct(self):
        "Õige vastuse genereerimine ja kuvamine"
        c = self.c
        c.block_correct = True
        c.read_only = True

        yv = c.ylesandevastus or None
        if not c.ylesanne:
            ylesanne_id = self.request.matchdict.get('task_id')
            if not self._check_task_test(ylesanne_id):
                err = _("Ülesandele puudub ligipääs")
                return self.render_to_response(self._TASK_MSG_TEMPLATE)                            
            c.ylesanne = model.Ylesanne.get(ylesanne_id)

        err = self._check_task_permission(c.ylesanne, c.sooritus)
        if err:
            self.error(err)
            return self.render_to_response(self._TASK_MSG_TEMPLATE)            
        if not c.lang:
            c.lang = self.request.params.get('lang')
        if not c.sooritaja_eesnimi:
            c.sooritaja_eesnimi = c.user.eesnimi
        c.correct_responses = c.ylesanne.correct_responses(yv,
                                                           lang=c.lang,
                                                           hindaja=False)
        random_responses = {}
        if c.ylesanne.on_juhuarv:
            for plokk in c.ylesanne.sisuplokid:
                if plokk.tyyp == const.BLOCK_RANDOM:
                    for k in plokk.kysimused:
                        kood = k.kood
                        kv = c.correct_responses.get(kood)
                        if kv:
                            for ks in kv.kvsisud:
                                value = ks.sisu
                                random_responses[kood] = value

        template = '/avalik/lahendamine/esitlus.mako'
        viewer = BlockView(self, c.ylesanne, c.lang)
        html = viewer.render_assessment(random_responses, template)
        return Response(html)

    def datafile(self):
        # kratt.dat
        # Krati andmefaili allalaadimine krati poolt
        c = self.c
        ylesanne_id = self.request.matchdict.get('ylesanne_id') or \
            self.request.matchdict.get('task_id')

        cl = TestClient(self)
        data = cl.get_kratt_datafile(ylesanne_id)
        self.prf()
        if not data:
            return Response('')
        
        data['ylesanne_id'] = ylesanne_id
        if c.user.is_authenticated:
            data['isikukood'] = c.user.isikukood
        if c.sooritus_id:
            data['sooritus_id'] = c.sooritus_id

        def replace_text(value):
            if value:
                return (value
                        .replace('{firstname}', c.user.eesnimi or '')
                        .replace('{lastname}', c.user.perenimi)
                        )
        for r in data['krati_kysimused']:
            r['speak'] = replace_text(r['speak'])
            r['text'] = replace_text(r['text'])

        r = data['krati_outro']
        r['speak'] = replace_text(r['speak'])
        r['text'] = replace_text(r['text'])

        json_str = json.dumps(data)
        base64_encoded = base64.b64encode(json_str.encode('utf-8'))
        return Response(base64_encoded, content_type='text/plain')
    
    def showtool(self):
        "Abivahendi kuvamine"
        c = self.c
        vahend_kood = self.request.matchdict.get('vahend')
        ylesanne_id = self.request.matchdict.get('task_id')

        cl = TestClient(self)
        item = cl.get_abivahend(vahend_kood)
        if not item:
            err = _("Vahend pole lubatud")
            log.info(err)
        else:
            self.c.item = item
            template = '/avalik/lahendamine/abivahend.mako'
            return self.render_to_response(template)
        
        return Response(err, content_type='text/plain')

    def _gentask(self, yv=None, hindaja=False, hindamine_id=False, pcorrect=False, bcorrect=True, showres=None, can_commit=True, random_responses={}):
        "Ülesande kuvamine"
        # eelnevalt peab olema c.responses
        c = self.c
        lang = c.lang
        lahendaja = not c.read_only
        template = self._TASK_TEMPLATE
        self.prf()
        err = self._check_task_permission(c.ylesanne, c.sooritus)
        self.prf()
        if err:
            self.error(err)
            return self.render_to_response(self._TASK_MSG_TEMPLATE)

        if not c.sooritaja_eesnimi:
            c.sooritaja_eesnimi = c.user.eesnimi
            
        c.showres = showres
        self.prf()
        c.new_responses = {}
        random_values = {}
        if c.ylesanne.on_juhuarv:
            br = BlockResponse(self)
            # enne esimest kuvamist genereeritakse juhuarvud
            c.new_responses, random_values = br.gen_random_responses(c.ylesanne, c.responses)
            # ja genereeritakse segatavate valikute valikujärjekord
            new_r2 = br.gen_shuffle(c.ylesanne, c.responses)
            c.new_responses.update(new_r2)

        # kratt töötleb faile, kas on valmis saanud
        self._kratt_response_download(c.responses)
            
        viewer = BlockView(self, c.ylesanne, c.lang)
        html = viewer.gen_esitlus_sisu(template,
                                       c.sooritus,
                                       yv,
                                       c.responses,
                                       c.vy,
                                       lahendaja,
                                       hindaja,
                                       hindamine_id,
                                       pcorrect,
                                       bcorrect,
                                       random_values)
        return Response(html)

    def _kratt_response_download(self, responses):
        # kui on krati kysimus, siis tuleb vaadata, kas vastus on valmis saanud
        for kood, kv in responses.items():
            if kv.sptyyp == const.INTER_KRATT:
                for ks in kv.kvsisud:
                    if ks.koordinaat and not ks.has_file:
                        if kratt_download(self, ks):
                            # salvestame saadud vastuse
                            if isinstance(ks, model.Kvsisu):
                                model.Session.commit()
                            elif isinstance(ks, MemKS) and self.c.exapi_host:
                                ExamClient(self, self.c.exapi_host).update_ks(ks)
    
    def decode_yv(self, r):
        "eisexami vastuses oleva ylesandevastuse kirje dekodeerimine"
        kysimusevastused = []
        clsmap = {'ylesandevastus': MemYlesandevastus,
                  'kysimusevastused': MemKV,
                  'kvsisud': MemKS,
                  }
        res = RecordWrapper.create_from_dict(r, clsmap)
        yv = res.ylesandevastus
        responses = {}
        if not yv or not yv.id:
            return None, responses
        for kv in yv.kysimusevastused:
            responses[kv.kood] = kv
        return yv, responses
    
    def images(self):
        """Näitame faili, mille leiame nime järgi ülesande alt sisuobjektide seast
        """
        self.prf()
        args = self.request.matchdict.get('args')
        ylesanne_id = None
        sisuplokk_id = None
        lastarg = None
        if args:
            li = args.split('_')
            if len(li) > 1:
                ylesanne_id = li[1]
            if len(li) > 2 and li[2]:
                sisuplokk_id = li[2]
            if len(li) > 3:
                lastarg = li[3]
            #if len(li) > 4:
            #    dummy_ver_to_avoid_cache = li[4]
                
        filename = self.request.matchdict.get('filename')
        filepath = filedata = last_modified = None
     
        lang = None
        hotspot = False
        math = False

        if lastarg:
            # võib olla kujul K või H või KH või KM, kus:
            # K - keele kood
            # H - tähis, et on vaja hotspotid peale joonistada
            # M - tähis, et on vaja matemaatilist avaldist
            if lastarg[-1] == 'H':
                hotspot = True
                lastarg = lastarg[:-1] or None
            lang = lastarg
        else:
            lang = self.c.lang

        vy_id = None
        if not ylesanne_id:
            ylesanne_id = self.request.matchdict.get('ylesanne_id') or \
                          self.request.matchdict.get('task_id')
            if not sisuplokk_id and not ylesanne_id:
                vy_id = self.request.matchdict.get('vy_id')

        cl = TestClient(self)
        item, valikud = cl.get_sisuobjekt(ylesanne_id, vy_id, sisuplokk_id, filename, hotspot)
        self.prf()

        if not item:
            if sisuplokk_id:
               log.info('Ei leitud sisuobjekti, sisuplokk_id=%s, %s' % (sisuplokk_id, filename))
            if ylesanne_id:
                log.info('Ei leitud sisuobjekti, ylesanne_id=%s, %s' % (ylesanne_id, filename))
            raise NotFound('Kirjet ei leitud')            
        mimetype = item.mimetype
        # originaalobjekt
        item3 = s3file_init('sisuobjekt', item)

        # tõlkeobjekt
        item_tr = item.tran(lang, False)
        if item_tr and item_tr.fileversion:
            # t_sisuobjekt ei sisalda filename
            item_tr.filename = item.filename
            item3_tr = s3file_init('t_sisuobjekt', item_tr)
            last_modified = item_tr.modified
        else:
            item3_tr = item3
            last_modified = item.modified
            
        if hotspot:
            # pilti täiendatakse
            filedata = item3_tr.filedata
            filedata, mimetype = BlockView.draw_hotspots(item3, filedata, valikud)
        else:
            # serveerime failinime kaudu
            filepath = item3_tr.path_for_response

        if not self._check_task_test(ylesanne_id):
            return Response(_("Puudub õigus failile ligipääsuks"))
        else:
            # õigus on olemas
            filename = item3.filename or '_F%d.file' % item.id
            inline = item.mimetype == const.MIMETYPE_TEXT_HTML or \
                     item.is_audio or item.is_video or item.is_image
            if filepath:
                return utils.cache_download(self.request, filepath, filename, mimetype, inline=inline, last_modified=last_modified)
            else:
                return utils.download(filedata, filename, mimetype, inline=inline)
            
    def _check_task_test(self, ylesanne_id):
        "Kas ylesanne kuulub testi"
        c = self.c
        rc = True
        self.prf()
        return rc

    def _check_task_permission(self, ylesanne, sooritus):
        "Kas ylesande avaldamistase ja salastatud lubavad kasutamist"
        return
