<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

<%def name="page_title()">
${c.item.nimi}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Minu töölaud"), h.url('tookogumikud'))} 
${h.crumb(c.item.nimi or _("Ülesanne"))}
</%def>
<%def name="page_headers()">
<style>
% if c.is_edit:
  ## eemaldame valiku ymbert raami ja taustavärvi, lisame alljoone
  .div-teemad .select2-container--default .select2-selection--multiple .select2-selection__choice {
  background-color: #fff;
  overflow:hidden;
  border: none;
  border-radius:0;
  border-bottom: .5px solid #afafaf;
  }
  ## proovime eemaldada alljont viimaselt valikult
  .div-teemad .select2-container--default .select2-selection--multiple .select2-selection__choice:last-child {
  border-bottom: none;
  }
  ## teeme valikud kogu rea pikkuseks
  .div-teemad .select2-container--default .select2-selection--multiple .select2-selection__choice {
    float:none;
  }
  ## ristike veidi suuremaks (muidu on 75%)
  .div-teemad .select2-container--default .select2-selection--multiple .select2-selection__choice__remove {
  font-size:150%;
  }
  ## valiku tekst ristikesega samale reale kogu rea laiuses
  .div-teemad .select2-container--default .select2-selection--multiple .select2-selection__choice div.row{
  width:99%;
  float:right;
  }

  ## eemaldame valiku ymbert raami ja taustavärvi, lisame alljoone
  .div-opitulemused .select2-container--default .select2-selection--multiple .select2-selection__choice {
  background-color: #fff;
  overflow:hidden;
  border: none;
  border-radius:0;
  border-bottom: .5px solid #afafaf;
  }
  ## proovime eemaldada alljont viimaselt valikult
  .div-opitulemused .select2-container--default .select2-selection--multiple .select2-selection__choice:last-child {
  border-bottom: none;
  }
  ## teeme valikud kogu rea pikkuseks
  .div-opitulemused .select2-container--default .select2-selection--multiple .select2-selection__choice {
    float:none;
  }
  ## ristike veidi suuremaks (muidu on 75%)
  .div-opitulemused .select2-container--default .select2-selection--multiple .select2-selection__choice__remove {
  font-size:150%;
  }

% else:
  .div-teemad tbody>tr.uline>td {
   border-bottom: .5px solid #afafaf;
   width:50%;
  }
  .div-teemad tbody>tr.uline:last-child>td {
   border-bottom: 0;
  }
% endif
  div.ylesandeaine {
    margin:0;
  }
</style>
</%def>
<%
c.can_update = c.user.has_permission('ylesanded', const.BT_UPDATE,c.item) and not c.item.is_encrypted
c.is_edit = c.is_edit and not c.item.is_encrypted
%>
<script>
<%include file="yldandmed.js"/>
</script>

% if c.item.is_encrypted:
${h.alert_notice(_("Ülesande sisu on krüptitud"))}
% endif

${h.form_save(c.item.id)}
${h.rqexp()}
<div class="form-wrapper">
      <div class="form-group row">
        ${h.flb3(_("ID"), 'f_id')}
        <div class="col-md-9" id="f_id">
          ${c.item.id or ''}
          % if c.item.kood:
          (${c.item.kood})
          % endif
        </div>
      </div>
      
      <div class="form-group row">
        ${h.flb3(_("Nimetus"), 'f_nimi', rq=True)}
        <div class="col-md-9">
          ${h.text('f_nimi', c.item.nimi, maxlength=256)}
        </div>
      </div>
  
      <div class="form-group row">
        ${h.flb3(_("Peamine kooliaste"), 'f_aste_kood')}
        <div class="col-md-9">
          <% aste_opt = c.opt.astmed() %>
          ${h.select('f_aste_kood', c.item.aste_kood, aste_opt, empty=True, wide=False)}
        </div>
      </div>
      
      <div class="form-group row">
        ${h.flb3(_("Kooliastmed"), 'v_aste_kood')}
        <div class="col-md-9">
          ${h.select_checkbox('v_aste_kood', c.item.kooliastmed, aste_opt)}
        </div>
      </div>
  
      <%
        c.yaine = (list(c.item.ylesandeained) or [c.new_item(aine_kood=c.aine_kood)])[0]
        c.aste_kood = c.item.aste_kood
        c.yaine_seq = 0
      %>
      <div class="ylesandeained">
        <div class="ylesandeaine">
          <%include file="yldandmed.ylesandeaine.mako"/>
        </div>
      </div>

      <div class="form-group row">
        ${h.flb3(_("Kvaliteedimärk"), 'kvaliteet_kood')}
        <div class="col-md-9">
          ${h.roxt(c.item.kvaliteet_nimi)}
        </div>
      </div>

    <div class="form-group row">
      ${h.flb3(_("Vahendid"), 'vahend_kood')}
      <div class="col-md-9">
      <%
        vahendid_kood = [r.vahend_kood for r in c.item.vahendid]
        opt_vahendid = model.Abivahend.get_opt()
      %>
      ${h.select2('vahend_kood', vahendid_kood, opt_vahendid, multiple=True)}
      </div>
    </div>

    <div class="form-group row">
      ${h.flb3(_("Maksimaalselt toorpunkte"),'maxp')}
      <div class="col-md-9" id="maxp">
        ${h.fstr(c.item.max_pallid or 0)}
      </div>
    </div>


    <div class="form-group row">
      ${h.flb3(_("Märkused"), 'f_markus')}
      <div class="col-md-9">
        ${h.textarea('f_markus', c.item.markus, cols=90, rows=3)}
      </div>
    </div>
    <div class="form-group row">
      ${h.flb3(_("Otsingu märksõnad"), 'f_marksonad')}
      <div class="col-md-9">
        ${h.textarea('f_marksonad', c.item.marksonad, cols=90, rows=2, maxlength=256)}
      </div>
    </div>  
    <div class="form-group row">
      ${h.flb3(_("Autor"), 'f_autor')}
      <div class="col-md-9">
        ${h.roxt(c.item.autor)}
      </div>
    </div>
  
    <div class="form-group row">
      ${h.flb3(_("Keel"), 'f_lang')}
      <div class="col-md-9">    
        ${h.select('f_lang', c.item.lang, c.opt.klread_kood('SOORKEEL', vaikimisi=c.item.lang))}
      </div>
    </div>

    <div class="form-group row">
      ${h.flb3(_("Olek"), 'f_staatus')}
      <div class="col-md-9">    
        <%
          ##  opt_st = [(kood, model.Klrida.get_str('Y_STAATUS', kood)) for kood in const.Y_ST_AV]
          opt_st = [(const.Y_STAATUS_AV_KOOSTAMISEL, _("Koostamisel")),
                    (const.Y_STAATUS_AV_VALMIS, _("Valmis")),
                    (const.Y_STAATUS_AV_ARHIIV, _("Arhiveeritud"))]
          %>
        ${h.select('f_staatus', c.item.staatus, opt_st)}
      </div>
    </div>

  % if c.item.alus_id:
  <div class="form-group row">
    ${h.flb3(_("Algne ülesanne"),'alus_id')}
    <div class="col-md-9" id="alus_id">
      ${h.link_to(c.item.alus_id, url=h.url('ylesanne', id=c.item.alus_id))}
    </div>
  </div>
  % endif
  % if len(c.item.koopiad):
  <div class="form-group row">
    ${h.flb3(_("Koopiad"), 'koopiad')}
    <div class="col-md-9" id="koopiad">
      % for rcd in c.item.koopiad:
        ${h.link_to(rcd.id, url=h.url('ylesanne', id=rcd.id))}
      % endfor
    </div>
  </div>
  % endif
</div>

<%include file="yldandmed.isikud.mako"/>
<div class="d-flex flex-wrap">
  <div class="flex-grow-1">
% if c.is_edit:
%   if c.item.id:
${h.btn_to(_("Vaata"), h.url('ylesanne', id=c.item.id), method='get', level=2)}
%   endif
% elif c.can_update:
${h.btn_to(_("Muuda"), h.url('edit_ylesanne', id=c.item.id), method='get', level=2)}
% endif


% if c.item.id and c.can_update:
${h.btn_remove()}

${h.btn_to_dlg(_('Lisa koostaja'), h.url('ylesanne_isikud', ylesanne_id=c.item.id),
title=_('Ülesande koostajate lisamine'), level=2, size='md', mdicls='mdi-plus')}
% endif

% if c.item.id and c.can_update and not c.item.is_encrypted:
${h.btn_to(_("Kopeeri"), h.url('new_ylesanne', id=c.item.id), level=2)}
% endif

% if c.item.id and c.can_update and not c.item.is_encrypted:
${h.btn_to_dlg(_("Kontrolli"), h.url('edit_ylesanne', id=c.item.id, sub='kontroll', partial=True), 
title=_("Ülesande kontrollimine"), size='lg', level=2)}
% endif
  </div>
  <div>
% if c.is_edit:
${h.submit()}
% endif
  </div>
</div>
${h.end_form()}
