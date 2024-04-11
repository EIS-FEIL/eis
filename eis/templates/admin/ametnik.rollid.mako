
<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Kasutajad")} | ${c.kasutaja.nimi}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Eksamikeskuse kasutajad"), h.url('admin_ametnikud'))} 
${h.crumb(c.kasutaja.nimi)}
${h.crumb(_("Rollid"))}
</%def>
<%def name="draw_tabs()">
<%include file="ametnik.tabs.mako"/>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>


<%
  can_edit_adm = c.user.on_admin or not c.kasutaja.on_kehtiv_roll(const.GRUPP_ADMIN)
%>
<h1 class="h3">${_("Kasutajarollid")}</h1>

<div class="d-flex flex-wrap my-3 alert alert-secondary">
  <div class="mr-4">
  <% kuni = c.kasutaja.ametnik_kuni %>
  % if kuni and kuni >= const.MAX_DATE:
  ${_("Isik on eksamikeskuse kasutaja")}
  % elif kuni:
  ${_("Isik on eksamikeskuse kasutaja kuni {dt}").format(dt=h.str_from_date(kuni))}
  % else:
  ${_("Isik ei ole eksamikeskuse kasutaja")}
  % endif
  </div>
</div>

<table id="roles" class="table tablesorter list">
% if not c.kasutajarollid:
  <tr>
    <td>${_("Kasutajal pole ühtki rolli")}</td>
  </tr>
% else:
  <thead>
    <tr>
      <th>${_("Kasutajagrupp")}</th>
      <th>${_("Piirkond")}</th>
      <th>${_("Õppeaine")}</th>
      <th>${_("Oskus")}</th>
      <th>${_("Testiliik")}</th>
      <th>${_("Muu info")}</th>
      <th nowrap>${_("Kehtib kuni")}</th>
      <th colspan="2">${_("Kehtivus")}</th>
    </tr>
  </thead>
  <tbody>
    % for cnt,rcd in enumerate(c.kasutajarollid):
    ## välistame rollid, mida püüti lisada, aga tuli viga
    ## välistame ka soorituskohaga seotud rollid (mida näitab testi sooritamisega seotud isikute aken)
    <% prefix = 'r-%s' % cnt %>
    <tr>
      <td>
        ${rcd.kasutajagrupp.nimi}
        % if rcd.lang:
        (${model.Klrida.get_lang_nimi(rcd.lang)})
        % endif
      </td>
      <td>
        ${rcd.piirkond_nimi or ''}
      </td>
      <td>
        ${'<br/>'.join(rcd.ained)}
      </td>
      <td>
        ${rcd.oskus_nimi or ''}
      </td>
      <td>
        ${rcd.testiliik_nimi or ''}
      </td>
      <td>
        % if rcd.allkiri_jrk:
        <div>
          ${_("{n}. allkirjastaja").format(n=rcd.allkiri_jrk)}
        </div>
        % endif
        % if rcd.allkiri_tiitel1:
        <div>${rcd.allkiri_tiitel1}</div>
        % endif
        % if rcd.allkiri_tiitel2:
        <div>${rcd.allkiri_tiitel2}</div>
        % endif
      </td>
      <td>
        ${h.str_from_date(rcd.kehtib_kuni_ui)}
      </td>
      <td>
        ${rcd.kehtiv_str}
      </td>
      <td>
        % if c.user.has_permission('ametnikud', const.BT_UPDATE, testiliik=rcd.testiliik_kood) and can_edit_adm:
        <%
          url = h.url('admin_ametnik_edit_roll',
              kasutaja_id=c.kasutaja.id, id=rcd.id, tyyp=rcd.kasutajagrupp.tyyp)
        %>
        ${h.btn_to_dlg('', url, title=_("Kasutajarolli muutmine"),
        size='lg', mdicls='mdi-file-edit', level=0)}
        % endif
      </td>
    </tr>
    % endfor
  </tbody>
% endif
</table>

% if c.user.has_permission('ametnikud', const.BT_UPDATE) and can_edit_adm:
${h.btn_to_dlg(_("Lisa roll"), h.url('admin_ametnik_new_roll',
kasutaja_id=c.kasutaja.id), title=_("Kasutajaroll"), width=700, mdicls='mdi-plus')}
% endif


<%
  q = (model.Session.query(model.Kasutajarollilogi)
       .filter_by(kasutaja_id=c.kasutaja.id)
       .join(model.Kasutajarollilogi.kasutajaroll)
       .join(model.Kasutajaroll.kasutajagrupp)
       .filter(model.Kasutajagrupp.tyyp.in_((const.USER_TYPE_EKK, const.USER_TYPE_AV)))
       .order_by(model.sa.desc(model.Kasutajarollilogi.id)))
  items = list(q.all())
%>
% if items:
<table class="table mt-3">
  <thead>
    <tr>
      ${h.th(_("Muutja"))}
      ${h.th(_("Aeg"))}
      ${h.th(_("Selgitus"))}
      ${h.th(_("Muudetud õigused"))}
    </tr>
  </thead>
  <tbody>
    % for krl in items:
    <%
      mk = krl.muutja_kasutaja
    %>
    <tr>
      <td>
        ${mk.nimi}
        (${mk.isikukood})
      </td>
      <td>${h.str_from_datetime(krl.aeg)}</td>
      <td>
        % if krl.jira_nr:
        <a href="${krl.jira_url}" target="blank">EJ-${krl.jira_nr}</a>
        % endif
        <div>
          ${h.url_to_link(krl.selgitus)}
        </div>
      </td>
      <td>
        ${krl.sisu}
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
