<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'isikuandmed' %>
<%include file="avaldus.tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Eksamile registreerimise taotluse sisestamine")}
</%def>      
<%def name="active_menu()">
<% c.menu1 = 'regamised' %>
</%def>

<%def name="breadcrumbs()">
${h.crumb(_("Registreerimine"), h.url('regamised'))} 
${h.crumb(_("Registreerimise taotluse sisestamine"))}
</%def>
${h.form_save(c.kasutaja.id)}
${h.hidden('korrad_id', c.korrad_id)}
<%include file="isikuandmed.mako"/>

<div class="form-wrapper mb-1">
  <div class="form-group row">
    ${h.flb3(_("Kodakondsus"),'dkodakond')}
    <div class="col-md-9" id="dkodakond">
      % if c.kasutaja.isikukood_ee and c.kasutaja.kodakond_kood:
      ${c.kasutaja.kodakond_nimi}
      % else:
      ${h.select('k_kodakond_kood', c.kasutaja.kodakond_kood, 
      c.opt.klread_kood('KODAKOND', vaikimisi=c.kasutaja.kodakond_kood), 
      empty=True, wide=False)}
      % endif
    </div>
  </div>
  <div class="form-group row">
    <div class="col">
    ${h.checkbox('on_lisatingimused', 1, checked=bool(c.kasutaja.lisatingimused),
    onchange="$('#k_lisatingimused').toggleClass('d-none', !this.checked);", label=_("Lisatingimused"))}
    ${h.textarea('k_lisatingimused', c.kasutaja.lisatingimused, rows=4,
    class_=not c.kasutaja.lisatingimused and 'd-none' or None)}
    </div>
  </div>
</div>

<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
    ${h.btn_to(_("Tagasi"), h.url('regamine_edit_avaldus', id=c.kasutaja.id, korrad_id=c.korrad_id), mdicls='mdi-arrow-left-circle', level=2)}
  </div>
  <div>
    ${h.submit(_("Jätka"), mdicls2='mdi-arrow-right-circle')}
  </div>
</div>
${h.end_form()}
