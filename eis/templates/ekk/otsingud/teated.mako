<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Teadete ülevaade")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'otsing' %>
</%def>

<%def name="page_headers()">
<style>
  .mail-body a {
  text-decoration: underline;
  }
</style>
</%def>
<h1>${_("Teadete ülevaade")}</h1>

${h.form_search(url=h.url('otsing_teated'))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
      <% c.testiliik_empty = True %>
      <% c.on_rv = c.on_sisse = c.on_pohikool = c.on_eel = c.on_d2 = c.on_tasemetoo = True %>
    <%include file="teated.otsing_test.mako"/>

    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
          ${h.flb(_("Isikukood"),'isikukood')}
          ${h.text('isikukood', c.isikukood, maxlength=50)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Eesnimi"),'eesnimi')}
        ${h.text('eesnimi', c.eesnimi)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Perekonnanimi"),'perenimi')}
        ${h.text('perenimi', c.perenimi)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Läbiviija roll"),'grupp_id')}
        <% opt_grupp = c.opt.labiviijagrupp %>
        ${h.select('grupp_id', c.grupp_id, opt_grupp, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Läbiviijate teated"),'ltyyp')}
        ${h.select('ltyyp', c.ltyyp, model.Kiri.opt_labiviijateated, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Sooritajate teated"),'styyp')}
        ${h.select('styyp', c.styyp, model.Kiri.opt_sooritajateated, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Muud teated"),'atyyp')}
        ${h.select('atyyp', c.atyyp, model.Kiri.opt_ametnikuteated, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Saatmise aeg"),'saadetud_alates')}
        ${h.date_field('saadetud_alates', c.saadetud_alates)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("kuni"),'saadetud_kuni')}
        ${h.date_field('saadetud_kuni', c.saadetud_kuni)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Edastuskanal"),'teatekanal')}
        <%
          kanalid = c.opt.TEATEKANAL
          opt_kanal = [(k, kanalid.get(k)) for k in (const.TEATEKANAL_EPOST, const.TEATEKANAL_POST, const.TEATEKANAL_STATEOS, const.TEATEKANAL_EIS)]
        %>
        ${h.select('teatekanal', c.teatekanal, opt_kanal, empty=True)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.submit(_("CSV"), id='csv', class_="filter", level=2)}
        ${h.btn_search(_("Otsi saadetud teateid"))}
      </div>
    </div>
  </div>
  <div class="filter">
    ${h.button(_("Läbiviijateadete saatmine"), class_="sendbtn",
    href=h.url('otsing_labiviijateated'), level=2)}
    ${h.button(_("Soorituskohateadete saatmine"), class_="sendbtn",
    href=h.url('otsing_kohateated'), level=2)}
    ${h.button(_("Tulemuste teavituste saatmine"), class_="sendbtn",
    href=h.url('otsing_tulemusteteavitused'), level=2)}
    <script>
      $('button.sendbtn').click(function(){
      this.form.action = $(this).attr('href');
      this.form.sort.value = '';
      this.form.submit();
      });
    </script>
  </div>
</div>
${h.end_form()}

% if c.arv != '' and c.saatmata:
<div class="data-box mb-5">
  <div class="row">
    <div class="column col-md-2">
      ${_("Liik")}
    </div>
    <div class="column col-md-2">
      ${model.Kiri.get_tyyp_nimi(c.styyp or c.ltyyp)}
    </div>
    <div class="column col-md-3">
      ${_("Saadetavaid teateid")}
    </div>
    <div class="column col-md-1">
      ${c.arv}
    </div>
    <div class="column col-md-3">
      % if c.arv:
      ${h.btn_to(_("Väljasta e-postiga"), 
      h.url_current('index', getargs=True, kanal=const.TEATEKANAL_EPOST), method='post', level=2)}
      % if c.on_tseis or c.ltyyp:
      ${h.btn_to(_("Väljasta väljatrükid"), 
      h.url_current('index', getargs=True, kanal=const.TEATEKANAL_POST), method='post', level=2)}
      % endif
      % endif
    </div>
  </div>
</div>
% endif

<div class="listdiv">
<%include file="teated_list.mako"/>
</div>
