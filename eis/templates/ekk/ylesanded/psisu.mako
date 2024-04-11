<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'sisu' %>
<%include file="tabs.mako"/>
</%def>

<%def name="require()">
<% c.includes['subtabs'] = True %>
</%def>

<%def name="page_title()">
${c.item.nimi or _("Ülesanne")} | ${_("P-testi ülesanne")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Ülesandepank"), h.url('ylesanded'))}
${h.crumb(c.item.nimi or _("Ülesanne"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'ylesanded' %>
</%def>

<%def name="draw_subtabs()">
<%namespace name="tab" file='/common/tab.mako'/>
<%
  edit = c.is_edit and c.user.has_permission('ylesanded', const.BT_UPDATE,c.ylesanne) and '_edit' or ''
%>
% if c.item.id:
${tab.subdraw('sisu', h.url('ylesanded%s_sisu' % edit, id=c.item.id, lang=c.lang), _("Detailne sisu"), c.tab2)}
${tab.subdraw('psisu', h.url('ylesanne%s_psisu' % edit, id=c.item.id, lang=c.lang), _("P-testi lihtsustatud sisu"), c.tab2)}
% else:
${tab.subdraw('sisu', None, _("Detailne sisu"), c.tab2)}
${tab.subdraw('psisu', None, _("P-testi lihtsustatud sisu"), c.tab2)}
% endif
</%def>

<%
c.can_update = c.user.has_permission('ylesanded', const.BT_UPDATE,c.item) and not c.item.is_encrypted
c.is_edit = c.is_edit and not c.item.is_encrypted
%>
${h.form_save(c.item.id)}
% if not c.item.id and c.vy_id:
${h.hidden('vy_id', c.vy_id)}
% endif
% if c.item.is_encrypted:
${h.alert_notice(_("Ülesande sisu on krüptitud"))}
% endif

${h.rqexp()}
<div class="form-wrapper">
  % if c.item.id:
  <div class="form-group row">
    ${h.flb3(_("ID"), 'yid')}
    <div class="col" id="yid">
      % if c.item.id:
      ${c.item.id}
      % if c.item.kood:
      (${c.item.kood})
      % endif
      % endif
    </div>
  </div>
  % endif
  <div class="form-group row">
    ${h.flb3(_("Nimetus"),'f_nimi',rq=True)}
    <div class="col">
      ${h.text('f_nimi', c.item.nimi, maxlength=256)}
    </div>
  </div>

<%
  yaine = None
  for yaine in c.item.ylesandeained:
     break
  if not yaine:
     yaine = c.new_item(aine_kood=c.aine_kood)
%>
  <div class="form-group row">
    ${h.flb3(_("Põhiõppeaine"), 'f_aine_kood', rq=True)}
    <div class="col">
      <% aine_opt = c.opt.klread_kood('AINE') %>
      ${h.select('f_aine_kood', yaine.aine_kood, aine_opt, empty=True, class_="aine")}
    </div>
  </div>
  <% ty_max_p = c.vy and c.vy.testiylesanne.max_pallid or None %>
  <div class="form-group row">
    ${h.flb3(_("Punktide arv"), 'max_p')}
    <div class="col" id="max_p">    
      ${h.fstr(c.item.max_pallid or 0)}
      % if ty_max_p:
      (${_("testis {p}p").format(p=h.fstr(ty_max_p))})
      % endif
    </div>
  </div>
</div>

% if c.item.id:
${self.sisuplokid()}
% endif

<br/>
% if c.is_edit:
${h.submit()}
%   if c.item.id:
${h.btn_to(_("Vaata"), h.url('ylesanne_psisu', id=c.item.id), method='get')}
%   endif
% elif c.can_update:
${h.btn_to(_("Muuda"), h.url('ylesanne_edit_psisu', id=c.item.id), method='get')}
% endif

% if c.item.id:
% if c.vy_id and c.vy_test_id and c.vy_testiosa_id:
${h.btn_to(_("Tagasi testi"), h.url('test_valitudylesanded', test_id=c.vy_test_id))}
% else:
${h.btn_to_dlg(_("Lisa testi"), h.url('ylesanne_lisatesti', ylesanne_id=c.item.id),
title=_("Lisa ülesanne testi"), width=700)}
${h.btn_to(_("Tagasi"), h.url('ylesanded'))}
% endif

% endif

${h.end_form()}

<%def name="sisuplokid()">
<%
  sisuplokid = list(c.item.sisuplokid)
%>
% if len(sisuplokid) == 0:
<p>${_("Sisuplokke pole lisatud")}</p>
% else:
<table class="table table-borderless table-striped" >
  <thead>
    <tr>
      <th>${_("Sisuploki tüüp")}</th>
      <th>${_("Küsimuse ID")}</th>
      <th>${_("Max punktide arv")}</th>
      <th>${_("Parameetrid")}</th>      
      <th></th>
    </tr>
  </thead>
  <tbody>
  %   for cnt,item in enumerate(sisuplokid):
        ${self.row_sisuplokk(item)}
  %   endfor
  </tbody>
</table>
% endif
<br/>

% if c.is_edit and c.item.id: 
${h.btn_to_dlg(_("Lisa sisuplokke"), h.url('ylesanne_edit_psisu', id=c.item.id, sub='lisa'), 
title=_("Sisuplokkide lisamine"), width=800)}
% endif
<br/>

</%def>

<%def name="row_sisuplokk(item)">
<%
  kysimused = list(item.pariskysimused) or [None]
  cnt = len(kysimused)
%>
% for ind, kysimus in enumerate(kysimused):
<%
  tulemus = kysimus and kysimus.tulemus or None
%>
<tr>
  % if ind == 0:
  <td rowspan="${cnt}">
    ${h.link_to(item.tyyp_nimi, h.url('ylesanne_edit_sisuplokk', id=item.id, ylesanne_id=c.item.id))}
  </td>
  % endif
  <td>
    ${kysimus and kysimus.kood}
  </td>
  <td>
    <% max_pallid = tulemus and tulemus.max_pallid or '' %>
    ${h.fstr(max_pallid)}
  </td>
  <td>
    <table class="table" >
    % if item.tyyp == const.INTER_CHOICE:
      <tr>
        <td class="fh">${_("Max vastuste arv")}</td>
        <td>
          ${kysimus.max_vastus}
        </td>
      </tr>
      <tr>
        <td class="fh">${_("Õige vastuse punktide arv")}</td>
        <td>
          ${h.fstr(tulemus.oige_pallid)}
        </td>
      </tr>
      <%
        v_correct = []
        if tulemus:
           for v_hm in tulemus.hindamismaatriksid:
              if v_hm.pallid > 0:
                  v_correct.append(v_hm.kood1)
      %>
      <tr>
        <td class="fh">${_("Õige valik")}</td>
        <td>
          % for indv, valik in enumerate(kysimus.valikud):
          <% label = valik.get_sisestusnimi(kysimus.rtf) %>
          % if kysimus.max_vastus == 1:
          ${h.radio('oige_%s' % kysimus.id, valik.kood, checked=valik.kood in v_correct, label=label, disabled=True)}
          % else:
          ${h.checkbox('oige_%s' % kysimus.id, valik.kood, checked=valik.kood in v_correct, label=label, disabled=True)}
          % endif
          % endfor
        </td>
      </tr>
    % elif item.tyyp == const.INTER_EXT_TEXT:
    <tr>
      <td class="fh">${_("Punktide intervall")}</td>
      <td>${h.fstr(tulemus.pintervall)}</td>
    </tr>
    % endif
    </table>
  </td>
  <td>
    % if item.tyyp in (const.INTER_CHOICE, const.INTER_EXT_TEXT):
    ${h.btn_to_dlg(_("Muuda"), h.url('ylesanne_edit_psisu', sub='sp', sisuplokk_id=item.id, id=c.item.id),
    title=_("Sisuplokk"), width=800)}
    % endif
    ${h.btn_remove(h.url('ylesanne_delete_psisu', sub='sp', sisuplokk_id=item.id, id=c.item.id),
                   confirm=_("Kas oled kindel, et soovid kustutada?"))}
  </td>
</tr>
% endfor
</%def>

