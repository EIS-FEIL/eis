from captcha.image import ImageCaptcha
from PIL import Image
from io import BytesIO
from random import Random, randint
import hashlib
from eis.lib.baseresource import *
_ = i18n._
log = logging.getLogger(__name__)

class TunnistusedController(BaseResourceController):
    """Tunnistuste otsimine
    """
    _authorize = False

    _MODEL = model.Tunnistus
    _INDEX_TEMPLATE = 'avalik/tunnistused/otsing.mako'
    _LIST_TEMPLATE = 'avalik/tunnistused/otsing_list.mako'
    _DEFAULT_SORT = 'tunnistus.id'
    _actions = 'index,download,show,edit'
    _ignore_default_params = ['csv','xls','format','otsi','minu']
    _old_captcha = None
    
    def _search_default(self, q):
        return self._search(q)    
    
    def _search(self, q):
        if self.c.minu:
            # kasutaja soovib enda tunnistusi vaadata
            q = q.filter(model.Tunnistus.kasutaja_id==self.c.user.id)
        elif self.c.otsi:
            # kasutaja soovib etteantud tunnistusenumbri järgi päringu teha
            errors = {}
            if not self.c.tunnistusenr:
                errors['tunnistusenr'] = _('Palun sisestada tunnistuse number')
            if not self.c.isikukood:
                errors['isikukood'] = _('Palun sisestada isikukood')
            if errors:
                raise ValidationError(self, errors)
            
            if self.c.captcha.upper() != self._old_captcha:
                self.error(_('Kood pole õige'))
                q = None
            else:
                q = q.filter(model.Tunnistus.tunnistusenr==self.c.tunnistusenr)
                usp = validators.IsikukoodP(self.c.isikukood)
                q = q.filter(usp.filter(model.Kasutaja))
        else:
            q = None
        return q

    def _gen_captcha_code(self):
        """Robotilõksu (captcha) pildil kuvatava juhuarvu genereerimine
        """
        session = self.request.session
        code = ''.join(Random().sample('2345689ACDEFGHKMNPQRSTU', 5))
        session['captcha'] = code
        session.changed()
        #log.debug('GEN CAPTCHA %s' % code)
        
    def _index_captcha(self):
        """Robotilõksu (captcha) pildi kuvamine
        """
        #fn_font = '/srv/eis/ttf/captcha_font.ttf'
        fn_font = '/srv/eis/ttf/times.ttf'
        code = self.request.session.get('captcha') or '0'
        #log.debug('  INDEX %s' % code)
        image = ImageCaptcha(fonts=[fn_font])
        data = image.generate(code)
        return Response(data.read(), content_type='image/png')

    def _query(self):
        self._old_captcha = self.request.session.get('captcha')
        self._gen_captcha_code()

        q = (model.SessionR.query(model.Tunnistus, model.Kasutaja, model.Rveksam.nimi)
             .filter(model.Tunnistus.staatus.in_((const.N_STAATUS_KEHTETU,
                                                  const.N_STAATUS_AVALDATUD)))
             .join(model.Tunnistus.kasutaja)
             .outerjoin(model.Tunnistus.rvsooritaja)
             .outerjoin(model.Rvsooritaja.rveksam))
        return q

    def _download(self, id, format):
        """Näita faili"""
        item = self._MODEL.getR(id)
        if not item or item.staatus != const.N_STAATUS_AVALDATUD:
            raise NotFound(_('Ei leitud'))
        filename = item.filename
        filedata = item.filedata
        mimetype = item.mimetype
        if not filedata:
            raise NotFound(_('Dokumenti ei leitud'))

        return utils.download(filedata, filename, mimetype)

    def _search_default(self, q):
        return None

