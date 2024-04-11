<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>
<%def name="requirenw()">
<% c.pagenw = True %>
</%def>

<%def name="page_title()">
${c.item.nimi or _("Ülesanne")} | ${_("Üldandmed")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Ülesandepank"), h.url('ylesanded'))}
${h.crumb(c.item.nimi or _("Ülesanne"), None, True)}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'ylesanded' %>
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
    margin:10px 0 0 0;
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

${h.rqexp()}
${h.form_save(c.item.id)}

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

      ${self.ained()}

      % if c.is_edit or c.item.keeletase_kood:
      <div class="form-group row keeletase">
        ${h.flb3(_("Keeleoskuse tase"), 'f_keeletase_kood')}
        <div class="col-md-9">
          ${h.select('f_keeletase_kood', c.item.keeletase_kood,
          c.opt.klread_kood('KEELETASE', None, empty=True, vaikimisi=c.item.keeletase_kood, ylem_none=True), wide=False)}
        </div>
      </div>
      % endif

      % if c.item.staatus not in const.Y_ST_AV:
      <div class="form-group row">
        ${h.flb3(_("E-kogu"), 'kogud_id')}
        <div class="col-md-9">
          <%
            kogu_opt = [(r.id, r.nimi) for r in model.Ylesandekogu.query.order_by(model.Ylesandekogu.nimi).all()]
            selected_id = [r.ylesandekogu_id for r in c.item.koguylesanded]
          %>
          ${h.select2('kogud_id', selected_id, kogu_opt, multiple=True, on_select='testiliik_by_ylkogu')}
        </div>
      </div>
      % endif
      
      <div class="form-group row">
        ${h.flb3(_("Kvaliteedimärk"), 'kvaliteet_kood')}
        <div class="col-md-9">
          % if c.user.has_permission('ylkvaliteet', const.BT_UPDATE, c.item):
          ${h.select2('kvaliteet_kood', c.item.kvaliteet_kood, c.opt.klread_kood('KVALITEET'), multiple=True, max_sel_length=1)}
          % else:
          ${c.item.kvaliteet_nimi}
          ${h.hidden('kvaliteet_kood', c.item.kvaliteet_kood)}
          % endif
        </div>
      </div>
 
      <div class="form-group row">
        ${h.flb3(_("Mõtlemistasand"), 'mtkood')}
        <div class="col-md-9">
          ${h.select_checkbox('mt.kood', [mt.kood for mt in c.item.motlemistasandid], c.opt.klread_kood('MOTE'))}
        </div>
      </div>

      <div class="form-group row">
        ${h.flb3(_("Testi liik"), 'tlkood')}
        <div class="col-md-9">
          ${h.select_checkbox('tl.kood', [tl.kood for tl in c.item.testiliigid], c.opt.testiliik)}
        </div>
      </div>

      <div class="form-group row">
        ${h.flb3(_("Ülesande kasutus"), 'kasutliik_kood')}
        <div class="col-md-9">
          <%
            selected = [r.kasutliik_kood for r in c.item.kasutliigid]
            opt_kasutliik = c.opt.klread_kood('KASUTLIIK')
          %>
          ${h.select_checkbox('kasutliik_kood', selected, opt_kasutliik)}
        </div>
      </div>
      
      <div class="form-group row">
        ${h.flb3(_("Vastamise vorm"), 'f_vastvorm_kood')}
        <div class="col-md-9">    
          ${h.select('f_vastvorm_kood', c.item.vastvorm_kood,
          c.opt.klread_kood('VASTVORM', empty=True, vaikimisi=c.item.vastvorm_kood))}
        </div>
      </div>

      <div class="form-group row">
        ${h.flb3(_("Hindamise meetod"), 'f_hindamine_kood')}
        <div class="col-md-9">
          % if c.item.arvutihinnatav:
          ${h.roxt(c.item.hindamine_nimi)}
          % else:
          ${h.select('f_hindamine_kood', c.item.hindamine_kood,
          c.opt.klread_kood('HINDAMINE', empty=True, vaikimisi=c.item.hindamine_kood))}
          % endif
        </div>
        ${h.flb3(_("Arvutiga hinnatav"),'arvutihinnatav')}
        <div class="col-md-9" id="arvutihinnatav">
          ${h.roxt(h.sbool(c.item.arvutihinnatav))}
        </div>
      </div>

      <div class="form-group row">
        ${h.flb3(_("Sobivus e-testiks"), 'f_etest')}
        <div class="col-md-9">
          ${h.select_bool('f_etest', c.item.etest or '')}
        </div>
        ${h.flb3(_("Sobivus p-testiks"), 'f_ptest')}
        <div class="col-md-9">
          ${h.select_bool('f_ptest', c.item.ptest or '')}
        </div>
      </div>

      <div class="form-group row">
        ${h.flb3(_("Diagnostilise testi ülesanne"), 'f_adaptiivne')}
        <div class="col-md-9">
          % if c.item.arvutihinnatav:
          ${h.select_bool('f_adaptiivne', c.item.adaptiivne or '')}
          % else:
          ${h.roxt(h.sbool(c.item.adaptiivne))}
          % endif
          ## vastamise vorm suuline -> hindamise meetod subjektiivne, pole arvutihinnatav, pole sobiv etestiks, pole sobiv adaptiivseks
          ## hindamise meetod subjektiivne -> pole arvutiga hinnatav
          ## adaptiivseks testiks sobilik -> sobiv e-testiks ja arvutiga hinnatav
        </div>
      </div>

    <div class="form-group row">
      ${h.flb3(_("Tagasisidega ülesanne"), 'f_on_tagasiside')}
      <div class="col-md-9">
        % if c.item.arvutihinnatav:
        ${h.select_bool('f_on_tagasiside', c.item.on_tagasiside or '')}
        % else:
        ${h.roxt(h.sbool(c.item.on_tagasiside))}
        % endif
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
      ${h.flb3(_("Maksimaalselt toorpunkte"), 'maxp')}
      <div class="col-md-9" id="maxp">
        ${h.fstr(c.item.max_pallid or 0)}
        &nbsp;&nbsp;
        ${h.checkbox('f_ymardamine', 1, checked=c.item.ymardamine, label=_("Ümardamine"))}
        &nbsp;&nbsp;
        ${h.checkbox('f_pallemaara', 1, checked=c.item.pallemaara, label=_("Avaliku vaate testi koostaja saab pallid ise määrata"))}
      </div>
    </div>

    <div class="form-group row">
      ${h.flb3(_("Raskusaste"), 'f_raskus_kood')}
      <div class="col-md-9">
        ${h.select('f_raskus_kood', str(c.item.raskus_kood or 0), c.opt.opt_raskus)}
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
        ${h.text('f_autor', c.item.autor, maxlength=128)}
      </div>
    </div>
    
  <% c.lang_tr_del = c.lang_tr_konesyntees = c.lang_asendatav = True %>
  <%include file="/common/lang_div.mako" />
  <%
    c.edit_tahemargid = c.is_edit and c.user.has_permission('ylesandetahemargid', const.BT_UPDATE, c.item)  
    c.show_tahemargid = c.edit_tahemargid or c.user.has_permission('ylesandetahemargid', const.BT_VIEW, c.item)
  %>
  % if c.show_tahemargid:
  <div class="form-group row">
    <div class="col-md-9">
        % if c.item.tahemargid is not None:
        <span class="brown">${_("{n} tähemärki").format(n=c.item.tahemargid)}</span>
        % endif
    </div>
  </div>
  % endif
  
  % if c.item.alus_id:
  <div class="form-group row">
    ${h.flb3(_("Algne ülesanne"), 'alus_id')}
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

<div class="d-flex flex-wrap">
${h.btn_back(url=h.url('ylesanded'))}

% if c.item.id and c.can_update:
${h.btn_remove()}
% endif

% if c.item.id and c.user.has_permission('ylesanded', const.BT_UPDATE) and not c.item.is_encrypted:
${h.btn_to(_("Kopeeri"), h.url('new_ylesanne', id=c.item.id), level=2)}
% endif

% if c.item.id and not c.item.is_encrypted:
  <%
    if c.user.has_permission('ylesanded', const.BT_UPDATE, obj=c.item):
       url_k = h.url('edit_ylesanne', id=c.item.id, sub='kontroll',partial=True)
    else:
       url_k = h.url('ylesanne', id=c.item.id, sub='kontroll',partial=True)
  %>
  ${h.btn_to_dlg(_("Kontrolli"), url_k, title=_("Ülesande kontrollimine"), size='lg', level=2)}
% endif
${h.btn_to_dlg(_("Lisa testi"), h.url('ylesanne_lisatesti', ylesanne_id=c.item.id),
title=_("Lisa ülesanne testi"), width=700, level=2)}

  <div class="flex-grow-1 text-right">
% if c.is_edit:
%   if c.item.id:
${h.btn_to(_("Vaata"), h.url('ylesanne', id=c.item.id), method='get', level=2)}
%   endif
${h.submit()}
% elif c.can_update:
${h.btn_to(_("Muuda"), h.url('edit_ylesanne', id=c.item.id), method='get')}
% endif
  </div>
</div>
</div>

${h.end_form()}

<%def name="ained()">
<%
  li_ained = list(c.item.ylesandeained) or [c.new_item()]
  c.aste_kood = c.item.aste_kood
  if c._arrayindexes != '':
     ya_indexes = c._arrayindexes.get('ya') or []
     li_ained = [li_ained[n] for n in ya_indexes if n < len(li_ained)]
     while len(ya_indexes) > len(li_ained):
        li_ained.append(c.new_item())
%>
<div class="ylesandeained" counter="${len(li_ained)}">
  % for c.yaine_seq, c.yaine in enumerate(li_ained):
  <div class="ylesandeaine">
  <%include file="yldandmed.ylesandeaine.mako"/>
  </div>
  % endfor
</div>
% if c.is_edit:
<div class="d-flex justify-content-end">
  ${h.button(_("Lisa õppeaine"), id="addsubject", href=h.url('ylesanded_new_ylesandeaine'), level=2)}
</div>
% endif
</%def>
