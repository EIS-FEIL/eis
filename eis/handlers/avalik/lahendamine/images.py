import os.path

from eis.lib.base import *
_ = i18n._
from eis.s3file import s3file_init
from eis.lib.blockview import BlockView
from eis.lib.testclient import TestClient
log = logging.getLogger(__name__)

class ImagesController(BaseController):
    _permission = 'lahendamine'
    _authorize = False
    _lang = None
    
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
            lang = self._lang

        if not ylesanne_id:
            ylesanne_id = self.request.matchdict.get('ylesanne_id')
        vy_id = self.request.matchdict.get('vy_id')
        
        self.prf()
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
        item_tr = item.tran(lang)
        if hotspot:
            # pilti täiendatakse
            filedata = item_tr.filedata or item.filedata
            filedata, mimetype = BlockView.draw_hotspots(item, filedata, valikud)
        else:
            # serveerime failinime kaudu
            filepath = item_tr.path_for_response
            last_modified = item_tr.modified
            if not filepath:
                filepath = item.path_for_response
                last_modified = item.modified

        self.prf()
        if not self._check_esitlus(item, ylesanne_id):
            return Response(_("Puudub õigus failile ligipääsuks"))
        else:
            self.prf()
            # õigus on olemas
            filename = item.filename or '_F%d.file' % item.id
            inline = item.mimetype == const.MIMETYPE_TEXT_HTML or \
                     item.is_audio or item.is_video or item.is_image
            self.prf()
            model.Session.rollback()
            if filepath:
                return utils.cache_download(self.request, filepath, filename, mimetype, inline=inline, last_modified=last_modified)
            else:
                return utils.download(filedata, filename, mimetype, inline=inline)

    def _check_esitlus(self, item, ylesanne_id):
        # õiguse kontroll
        c = self.c
        rc = False
        test_id = self.request.matchdict.get('test_id')
        # if test_id and c.user.is_authenticated:
        #     rc = c.user.has_permission('testid', const.BT_VIEW, test_id=test_id)
        # else:
        #     # autentimata kasutajal peab olema esitlus ja ylesanne peab olema avalik
        #     rc = c.user.has_permission('lahendamine', const.BT_SHOW, obj=item.sisuplokk.ylesanne)
        # if not rc:
        #     log.debug('IMAGES: puudub õigus sisuobjekti %s vaatamiseks' % item.id)
        #     raise NotAuthorizedException('avaleht')
        rc = True
        return rc
    
    def shared(self):
        """Ühised failid
        """
        filename = self.request.matchdict.get('filename')
        cl = TestClient(self)
        item = cl.get_shared(filename)
        if not item:
            raise NotFound(_("Faili ei leitud"))

        item3 = s3file_init('yhisfail', item)
        last_modified = item.modified
        mimetype = item.mimetype
        filename = item.filename
        filepath = item3.path_for_response
        
        return utils.cache_download(self.request, filepath, filename, mimetype, inline=True, last_modified=last_modified)

    def testimages(self):
        """Testi failid (tagasisidevormil)
        """
        test_id = self.request.matchdict.get('test_id')
        filename = self.request.matchdict.get('filename')
        cl = TestClient(self)
        item = cl.get_tagasisidefail(test_id, filename)
        if not item:
            raise NotFound(_("Faili ei leitud"))

        item3 = s3file_init('tagasisidefail', item)
        last_modified = item.modified
        mimetype = item.mimetype
        filename = item.filename
        filepath = item3.path_for_response

        return utils.cache_download(self.request, filepath, filename, mimetype, inline=True, last_modified=last_modified)

    def __before__(self):
        # kui ylesanne_id on URLis eraldi
        self.ylesanne_id = self.request.matchdict.get('ylesanne_id')
        # kui ylesanne_id on URLis args sees
        args = self.request.matchdict.get('args')
        if args:
            li = args.split('_')
            if len(li) > 1:
                ylesanne_id = li[1]
                if ylesanne_id:
                    self.ylesanne_id = ylesanne_id

