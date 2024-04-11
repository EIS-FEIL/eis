<%inherit file="/common/pagenw.mako"/>
<%def name="require()">
% if c.app_plank:
<meta name="description" content="Plankide moodul"/>
% else:
<meta name="description" content="Ülesanded ja testid õppuritele ja õpetajatele, harjutamiseks ja eksamineerimiseks"/>
% endif
</%def>

<%def name="page_title()">
% if c.app_plank:
${_("Sisenemine plankide moodulisse")}
% else:
${_("Sisenemine infosüsteemi")}
% endif
</%def>
<% 
   c.is_edit = True
   settings = c.user.handler.request.registry.settings
   is_ext = settings.get('is_ext') == 'true'
   is_mobile_id = is_ext and settings.get('digidocservice.m.service')

   # sisselogimise URL samas serveris
   hostless_url = h.url('login', action='signin')
   c.pw_url = hostless_url
   
   pw_host = settings.get('eis.pw.url')
   if settings.get('tara.auth.url'):
       if c.is_devel:
           c.tara_url = h.url('tara_login')  
       else:
           c.tara_url = pw_host + '/eis/tara/login'

   if settings.get('harid.auth.url'):
       if c.is_devel:
           c.harid_url = h.url('harid_login')  
       else:
           c.harid_url = pw_host + '/eis/harid/login'

   # Parooliga sisenemise URL
   # pw.url ei saa kasutada, sest brauser ei luba suunata ymber teisele hostile
   # Cross-Origin Read Blocking (CORB) blocked cross-origin response
   if c.app_ekk and c.inst_name not in ('test','dev'):
      # live serveris EKK vaates ei saa parooliga logida 
      c.pw_url = None
   pw_active = c.pw_url
   harid_active = not pw_active
%>
% if not c.user.id:

% if c.app_plank:
<h1>${_("Sisenemine plankide moodulisse")}</h1>
% else:
<h1>${_("Sisenemine infosüsteemi")}</h1>
% if c.app_eis:
<div>
  ${_("Vali sobilik autentimine. Kui sa ei ole varem seda keskkonda kasutanud, siis luuakse sulle konto automaatselt esimesel mõne ID vahendiga sisselogimisel.")}
</div>
% endif
% endif

<ul class="nav nav-tabs mt-3" role="tablist">
  % if c.pw_url:
    ${self.login_item(_("Parool"), 'pw', pw_active)}
  % endif
  % if c.harid_url:
    ${self.login_item(_("HarID"), 'harid', harid_active)}
  % endif
  % if c.tara_url:
    ${self.login_item(_("ID-kaart / Mobiil-ID / Smart-ID"), 'tara')}
  % endif
</ul>
<div class="tab-content">
  % if c.pw_url:
    ${self.login_pw(is_ext, pw_active)}
  % endif
  % if c.harid_url:
    ${self.login_harid(harid_active)}
  % endif
  % if c.tara_url:
    ${self.login_tara()}
  % endif
</div>
% endif

<%def name="login_item(label, id, active=False)">
  <li class="nav-item" role="tab"
      id="tasks_tab_${id}"
      aria-controls="tab_${id}"
      aria-selected="${active and 'true' or 'false'}">
    <a class="nav-link ${active and 'active' or ''}"
      data-toggle="tab"
      href="#tab_${id}">${label}</a>
  </li>
</%def>

<%def name="login_pw(is_ext, active=False)">
  <div
    class="tab-pane fade show ${active and 'active' or ''}"
    id="tab_pw"
    role="tabpanel"
    aria-labelledby="tasks_tab_pw">
    ${h.form(c.pw_url)}
    <div class="row filter">
      <div class="col-12 col-md-4 col-lg-3">
        <div class="form-group">
          <label class="font-weight-bold" for="username">
            ${_("Isikukood")}
          </label>
	      ${h.text('username', c.username, ronly=False)}
        </div>
      </div>
      <div class="col-12 col-md-4 col-lg-3">
        <div class="form-group">
          <label class="font-weight-bold" for="parool">
            ${_("Parool")}
          </label>
          ${h.password('parool', style="width:100%", ronly=False, autocomplete='off')}
        </div>
      </div>
    </div>
    <div class="d-flex justify-content-right">
      ${h.submit(_("Sisene"), clicked=1000)}
      ${h.hidden('request_url', c.request_url, id="request_url_pw")}
    </div>
    ${h.end_form()}
  </div>
</%def>

<%def name="login_harid(active=False)">
  <div
    class="tab-pane fade show ${active and 'active' or ''}"
    id="tab_harid"
    role="tabpanel"
    aria-labelledby="tasks_tab_harid">
    ${h.form(c.harid_url, id="form_harid")}
    ${h.submit(_("Sisene"), id='login_h', clicked=1000)}
    ${h.hidden('request_url', c.request_url, id="request_url_h")}
    ${h.end_form()}
    <script>
      $('#tasks_tab_harid').click(function(){
        $('form#form_harid').submit();
      });
    </script>
  </div>
</%def>

<%def name="login_tara(active=False)">
  <div
    class="tab-pane fade show ${active and 'active' or ''}"
    id="tab_tara"
    role="tabpanel"
    aria-labelledby="tasks_tab_tara">
    ${h.form(c.tara_url, id='form_tara')}
    ##${h.submit(_("Sisene"), id='login_t', clicked=1000)}
    ${h.hidden('request_url', c.request_url, id="request_url_t")}
    ${h.end_form()}
    <script>
      $('#tasks_tab_tara').click(function(){
        $('form#form_tara').submit();
      });
    </script>
  </div>
</%def>


