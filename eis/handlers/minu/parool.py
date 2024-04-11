from eis.lib.base import *
_ = i18n._

log = logging.getLogger(__name__)

class ParoolController(BaseController):
    """Oma parooli muutmine
    """
    _authorize = False

    @action(renderer='minu/parool.mako')
    def index(self):
        return self.response_dict

    def create(self):
        self.form = Form(self.request, schema=forms.minu.ParoolForm)
        if not self.form.validate():
            return Response(self.form.render('minu/parool.mako',
                                             extra_info=self.response_dict))
            
        # kasutaja on sisestanud ja vajutanud nupule
        parool_vana = self.form.data.get('parool_vana')
        parool_uus = self.form.data.get('parool_uus')
        parool_uus2 = self.form.data.get('parool_uus2')
        kasutaja = self.c.user.get_kasutaja()
        if not kasutaja:
            self.error(_("Palun esmalt sisse logida"))
        elif self.c.user.has_pw and not kasutaja.check_password(parool_vana) \
             and not kasutaja.check_password_old(parool_vana):
            self.error('Vana parool on vale')
        else:
            # leiame kirjutatava sessiooni kirje
            kasutaja = model.Kasutaja.query.filter_by(id=kasutaja.id).first()
            kasutaja.set_password(parool_uus, False)
            model.Session.commit()
            self.success('Parool on vahetatud!')

        url = self.c.request_url or self.url('avaleht')
        # suunatakse kasutaja sinna, kuhu ta algselt minna tahtis, 
        # aga kohe ei saanud, sest oli autentimata
        return HTTPFound(location=url)

    def __before__(self):
        self.c.request_url = self.request.params.get('request_url')

    def _get_log_params(self):
        return {key: key.startswith('parool') and '*' or value for (key, value) in self.request.params.items()}
