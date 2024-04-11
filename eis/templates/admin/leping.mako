<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${c.item.nimetus or _("Uus leping")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_("Lepingud"), h.url('admin_lepingud'))} 
${h.crumb(c.item.nimetus or _("Uus leping"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>

<h1>${_("Lepingu andmed")}</h1>
${h.form_save(c.item.id)}

<% ch = h.colHelper('col-md-2 text-md-right', 'col-md-10') %>
${h.rqexp()}
<div class="form-wrapper mb-1">
  <div class="form-group row">
    ${ch.flb(_("Nimetus"), 'f_nimetus', rq=True)}
    <div class="col-md-10">
      ${h.text('f_nimetus', c.item.nimetus)}      
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("URL"), 'f_url', rq=True)}
    <div class="col-md-10">
      ${h.text('f_url', c.item.url)}
      % if c.item.url:
      ${h.link_to(c.item.url, c.item.url, noreferrer='true')}
      % endif
    </div>
  </div>
  <div class="form-group row">
    <div class="col-md-2"></div>
    <div class="col-md-10">
      ${h.checkbox1('f_yldleping', 1, checked=c.item.yldleping, label=_("Üldleping"))}
      <br/>
      ${h.checkbox1('f_sessioonita', 1, checked=c.item.sessioonita, label=_("Lepingut ei sõlmita iga testsessiooni jaoks eraldi"))}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Aasta alates"), 'f_aasta_alates')}
    <div class="col-md-1">
      ${h.posint5('f_aasta_alates', c.item.aasta_alates, minval=2015, maxlength=4)}
    </div>
    ${ch.flb(_("kuni"), 'f_aasta_kuni')}
    <div class="col">
      ${h.posint5('f_aasta_kuni', c.item.aasta_kuni, minval=2015, maxlength=4)}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Testsessioon"), 'f_testsessioon_id')}
    <div class="col-md-10">
      ${h.select('f_testsessioon_id', c.item.testsessioon_id, c.opt_sessioon, prompt=_("Kõik tingimustele vastavad sessioonid"), add_missing=True, wide=False)}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Läbiviijate rollid"), 'rollid')}
    <div id="rollid" class="col-md-10">
      ${self.lepingurollid(c.item)}
    </div>
  </div>
  % if c.item.id:
  <div class="form-group row">
    ${ch.flb(_("Testimiskorrad"), 'tkorrad')}
    <div id="tkorrad" class="col-md-10">
      <% litk = [] %>
      % for tl in c.item.testilepingud:
      <% tk = tl.testimiskord %>
      % if tk.id not in litk:
      ${h.link_to(tk.tahised, h.url('test_kord', test_id=tk.test_id, id=tk.id))}
      <% litk.append(tk.id) %>
      % endif
      % endfor
      % if not litk:
      ${_("Lepingu tingimustele ei vasta ükski testimiskord")}
      % endif
    </div>
  </div>    
  <div class="form-group row">
    ${ch.flb(_("Sõlmitud lepingud"), 'noustunud')}
    <div id="noustunud" class="col-md-10">
      ${self.solmitud_lepingud(c.item)}
    </div>
  </div>
  % endif
</div>

<div class="d-flex flex-wrap">
  ${h.btn_back(url=h.url_current('index'))}      
  % if c.is_edit and c.item.id:
  ${h.btn_to(_("Vaata"), h.url_current('show', id=c.item.id), method='get', level=2)}
  % endif
  % if not c.is_edit and c.user.has_permission('lepingud', const.BT_UPDATE):
  ${h.btn_to(_("Muuda"), h.url_current('edit', id=c.item.id), method='get')}
  % endif
  % if c.item.id and c.user.has_permission('lepingud', const.BT_UPDATE):
  ${h.btn_to(_("Kopeeri"), h.url_current('new', copy_id=c.item.id), level=2)}
  % endif
  % if c.is_edit:
  <div class="flex-grow-1 text-right">
    % if c.item.id:
    ${h.btn_remove()}
    % endif
    ${h.submit()}
  </div>
  % endif
</div>
${h.end_form()}

<%def name="lepingurollid(item)">
<%
  grid_id = 'tbl_lr'
  prefix = 'lr'
%>
<table id="${grid_id}" class="table">
  <thead>
    <tr>
      <th>${_("Läbiviija roll")}</th>
      <th>${_("Õppeaine")}</th>
      <th>${_("Testiliik")}</th>
      % if c.is_edit:
      <th></th>
      % endif
    </tr>
  </thead>
  <tbody>
  % if c._arrayindexes != '' and not c.is_tr:
## valideerimisvigade korral
  %   for cnt in c._arrayindexes.get(prefix) or []:
        ${self.row_lepinguroll(c.new_item(),'%s-%s' % (prefix, cnt))}
  %   endfor
  % else:
## tavaline kuva
  %   for cnt,subitem in enumerate(item.lepingurollid):
        ${self.row_lepinguroll(subitem,'%s-%s' % (prefix, cnt))}
  %   endfor
  % endif
  </tbody>
  % if c.is_edit:
  <tfoot id="sample_${grid_id}" class="d-none sample">
   ${self.row_lepinguroll(c.new_item(), '%s__cnt__' % prefix)}
  </tfoot>
  % endif
</table>
% if c.is_edit:
${h.button(_("Lisa"), onclick=f"grid_addrow('{grid_id}', null, null, true);", level=2, mdicls='mdi-plus')}
% endif
</%def>

<%def name="row_lepinguroll(item, prefix)">
  <tr>
    <td>
      ${h.select(prefix + '.kasutajagrupp_id', item.kasutajagrupp_id, c.opt_kasutajagrupp, add_missing=True)}
    </td>
    <td>
      ${h.select(prefix + '.aine_kood', item.aine_kood, c.opt_aine, prompt=_("Kõik õppeained"), add_missing=True)}
    </td>
    <td>
      ${h.select(prefix + '.testiliik_kood', item.testiliik_kood, c.opt_testiliik, add_missing=True)}
    </td>
    % if c.is_edit:
    <td>
      ${h.grid_s_remove('tr', confirm=True)}
      ${h.hidden(prefix + '.id', item.id)}
    </td>
    % endif
  </tr>
</%def>

<%def name="solmitud_lepingud(rcd)">
<%
  q = (model.SessionR.query(model.Labiviijaleping.testsessioon_id,
                           model.Testsessioon.nimi,
                           model.sa.func.count(model.Labiviijaleping.id))
      .filter(model.Labiviijaleping.leping_id==rcd.id)
      .outerjoin(model.Labiviijaleping.testsessioon)
      .group_by(model.Testsessioon.nimi, model.Labiviijaleping.testsessioon_id)
      .order_by(model.Testsessioon.nimi))
  data = [r for r in q.all()]
%>
% if not data:
${_("Keegi pole lepingut sõlminud")}
% else:
<table class="table table-striped table-align-top">
  <thead>
    <tr>
      <th>${_("Testsessioon")}</th>
      <th>${_("Lepinguga nõustumiste arv")}</th>
      <th>${_("Lepinguga nõustunud läbiviijad")}</th>
    </tr>
  </thead>
  <tbody>
    % for sessioon_id, sessioon_nimi, sessioon_cnt in data:
    <tr>
      <td>
        ${sessioon_nimi or _("sessioonita")}
      </td>
      <td>
        ${sessioon_cnt}
      </td>
      <td>
          <%
            q1 = (model.SessionR.query(model.Kasutaja.id, model.Kasutaja.nimi, model.Labiviijaleping.noustunud)
                 .join(model.Kasutaja.labiviijalepingud)
                 .filter(model.Labiviijaleping.leping_id==rcd.id)
                 .filter(model.Labiviijaleping.testsessioon_id==sessioon_id)
                 .order_by(model.Kasutaja.nimi, model.Labiviijaleping.noustunud))
          %>
          % for k_id, k_nimi, noustunud in q1.all():
          <div>${h.link_to('%s %s' % (k_nimi, h.str_from_date(noustunud)), h.url('admin_kasutaja', id=k_id))}</div>
          % endfor
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
</%def>
