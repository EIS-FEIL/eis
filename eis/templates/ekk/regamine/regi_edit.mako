<%inherit file="/common/page.mako"/>
<%def name="active_menu()">
<% c.menu1 = 'regamised' %>
</%def>

<%def name="page_title()">
${_("Registreerimine")}: ${c.item.nimi}
% if c.item.testimiskord:
${c.item.testimiskord.tahised}
% endif
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Registreerimine"), h.url('regamised'))}
${h.crumb(c.item.nimi, h.url('regamine',id=c.item.id))}
</%def>
${h.form_save(c.item.id)}

<% 
   c.kasutaja = c.item.kasutaja
   c.sooritaja = c.item
   c.lopetanud_tingimused = True # kuvada lõpetamise tingimuste väljad
   testimiskord = c.item.testimiskord
%>
<%include file="isikuandmed.mako"/>

% if testimiskord:
<div class="form-wrapper">
  <div class="form-group row">
    ${h.flb3(_("Soorituskeel"), 'f_lang')}
    <div class="col-md-9">
      ${h.select('f_lang', c.item.lang, testimiskord.opt_keeled, wide=False)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Soovitav soorituspiirkond"),'f_piirkond_id')}
    <div class="col-md-9">
      <%
         c.piirkond_id = c.item.piirkond_id
         c.piirkond_field = 'f_piirkond_id'
         c.piirkond_filtered = testimiskord.get_piirkonnad_id()
      %>
      <%include file="/admin/piirkonnavalik.mako"/>
    </div>
  </div>
  <% opt_kursused = c.item.test.opt_kursused %>
  % if opt_kursused:
  <div class="form-group row">
    ${h.flb3(_("Kursus"),'f_kursus_kood')}
    <div class="col-md-9">
      ${h.select('f_kursus_kood', c.item.kursus_kood, opt_kursused, wide=False)}
    </div>
  </div>
  % endif
  <div class="form-group row">
    ${h.flb3(_("Märkused"),'f_markus')}
    <div class="col-md-9">
      ${h.textarea('f_markus', c.item.markus)}
    </div>
  </div>

  <div class="form-group row">
    ${h.flb3(_("Sooritaja märkused"),'f_reg_markus')}
    <div class="col-md-9">
      ${h.textarea('f_reg_markus', c.item.reg_markus)}
    </div>
  </div>

  % if c.item.test.on_tseis:
  <div class="form-group row">
    ${h.flb3(_("Soovib konsultatsiooni"),'f_soovib_konsultatsiooni')}
    <div class="col-md-9">
      ${h.checkbox1('f_soovib_konsultatsiooni', 1, checked=c.item.soovib_konsultatsiooni)}
    </div>
  </div>
  % endif
</div>

<%include file="rahvusvaheline_eksam.mako"/>

% if c.item.test.testiliik_kood == const.TESTILIIK_TASE:
<div class="form-wrapper">
  <div class="form-group row">
    ${h.flb3(_("Töövaldkond"),'f_tvaldkond_kood')}
    <div class="col-md-9">
      ${h.select('f_tvaldkond_kood', c.item.tvaldkond_kood, 
      c.opt.klread_kood('TVALDKOND', vaikimisi=c.item.tvaldkond_kood), 
      empty=True, wide=False)}
      % if not c.is_edit and c.item.tvaldkond_kood == const.TVALDKOND_MUU:
      ${c.item.tvaldkond_muu}
      % endif
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Amet"),'f_amet_muu')}
    <div class="col-md-9">
      ${h.text('f_amet_muu', c.item.amet_muu)}
    </div>
  </div>
  <div class="form-group row">
    ${h.flb3(_("Haridus"),'f_haridus_kood')}
    <div class="col-md-9">
      ${h.select('f_haridus_kood', c.item.haridus_kood, 
      c.opt.klread_kood('HARIDUS', vaikimisi=c.item.haridus_kood), 
      empty=True, wide=False)}
    </div>
  </div>
</div>
% else:
${h.hidden('f_tvaldkond_kood', c.item.tvaldkond_kood)}
${h.hidden('f_amet_muu', c.item.amet_muu)}
${h.hidden('f_haridus_kood', c.item.haridus_kood)}
% endif

<div class="form-wrapper">
  <div class="form-group row">
    ${h.flb3(_("Kodakondsus"),'kodakond')}
    <div class="col-md-9" id="kodakond">
      % if c.item.staatus in (const.S_STAATUS_REGAMATA, const.S_STAATUS_REGATUD) and c.kasutaja.isikukood_ee and c.kasutaja.kodakond_kood:
      ${c.kasutaja.kodakond_nimi}
      ${h.hidden('f_kodakond_kood', c.kasutaja.kodakond_kood)}
      % else:
      ${h.select('f_kodakond_kood', c.item.kodakond_kood, 
      c.opt.klread_kood('KODAKOND', vaikimisi=c.item.kodakond_kood), 
      empty=True, wide=False)}
      % endif
    </div>
  </div>
  <div class="form-group row">
    <div class="col-md-3">
      ${h.checkbox1('on_lisatingimused', 1, checked=bool(c.kasutaja.lisatingimused),
      onchange="$('#k_lisatingimused').toggleClass('invisible', !this.checked);", label=_("Lisatingimused"))}
    </div>
    <div class="col-md-9">
      ${h.textarea('k_lisatingimused', c.kasutaja.lisatingimused, rows=4,
      class_=not c.kasutaja.lisatingimused and 'invisible' or None)}
    </div>
  </div>
</div>

% endif

<div class="mt-1 d-flex flex-wrap">
  <div class="flex-grow-1">
    ${h.btn_to(_("Vaata"), h.url('regamine', id=c.item.id), level=2)}
  </div>
  ${h.submit()}
</div>
${h.end_form()}
