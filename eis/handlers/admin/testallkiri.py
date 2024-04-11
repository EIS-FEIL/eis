# Allkirjastamise testimine
# https://eis.ekk.edu.ee/ekk/testallkirjad

from simplejson import dumps
from eis.lib.baseresource import *
_ = i18n._
import eis.lib.ddocs as ddocs

log = logging.getLogger(__name__)

class TestallkiriController(BaseResourceController):
    """Digiallkirjastamise testimine
    """
    _permission = 'admin'
    _dirname = '/srv/eis/var/data/eis_testallkiri'
    _authorize = False
    _actions = 'index,create,download,show,update'
    
    def index(self):
        return self.render_to_response('/admin/testallkiri.mako')

    def show(self):
        c = self.c
        id = self.request.matchdict.get('id')
        c.item = model_s.Tempvastus.get(id)
        if not c.item:
            self.error('Fail puudub')
            return self.redirect('index')

        if self.request.params.get('signers'):
            c.signers = ddocs.list_signed(self, c.item.filedata, c.item.filename)
            c.signers_ext = 'asice'
        return self.render_to_response('/admin/testallkiri.mako')    

    def create(self):
        # Uue tekstifaili loomine
        filedata = 'TEKST'.encode('utf-8')
        item = model_s.Tempvastus(filedata=filedata,
                                  filename='dokument.txt',
                                  temp_id=-5)
        model_s.DBSession.add(item)
        model_s.DBSession.flush()
        self.success()
        return self._redirect('show', id=item.id)

    def _update_prepare_signature(self, id):
        """Allkirjastamise alustamine: brauserilt on saadud sert,
        selle kohta arvutatakse allkirjastatav räsi.
        """
        # variandid:
        # olemasolev .bdoc
        # olemasolev .asice
        # allkirjastamata fail - teeme .asice
        item = model_s.Tempvastus.get(id)
        if not item:
            res = {'error': 'Fail puudub'}
        else:
            is_new = not item.filename.endswith('.asice')
            filedata = item.filedata
            filename = item.filename
            log.debug('DdocS.prepare_signature %s' % filename)
            filedata, res = ddocs.DdocS.prepare_signature(self, filedata, filename)
            if is_new and filedata:
                # salvestame (allkirjata) konteineri
                item.filedata = filedata
                item.filename = 'dokument.asice'
                model_s.DBSession.flush()
        return res
    
    def _update_finalize_signature(self, id):
        """Allkirjastamise lõpetamine: brauserilt on saadud allkiri,
        see lisatakse pooleli oleva DDOC-faili sisse.
        """
        item = model_s.Tempvastus.get(id)
        log.debug('DdocS.finalize_signature %s' % item.filename)        
        filedata, signers, dformat = ddocs.DdocS.finalize_signature(self, item.filedata)
        if filedata:
            item.filedata = filedata
            item.filename = 'dokument.asice'
            model_s.DBSession.flush()
            self.success('Allkiri antud!')

        return self._redirect('show', id=id)

    def _download(self, id, format):
        "Faili allalaadimine"

        _filename = 'dokument.%s' % format
        item = model_s.Tempvastus.get(id)
        if not id:
            self.error('fail puudub')
            return self._redirect('index')

        return utils.download(item.filedata, item.filename)

