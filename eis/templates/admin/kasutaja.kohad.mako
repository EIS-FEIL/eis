<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<% c.includes['jstree'] = True %>
</%def>
<%def name="page_title()">
${_("Kasutajad")} | ${c.kasutaja.nimi or _("Uus kasutaja")}
</%def>
<%def name="breadcrumbs()">
${h.crumb(_("Kasutajad"), h.url('admin_kasutajad'))} 
${h.crumb(c.kasutaja.nimi, h.url('admin_kasutaja', id=c.kasutaja.id))}
${h.crumb(_("Soorituskohad"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>
<%def name="draw_tabs()">
<%include file="kasutaja.tabs.mako"/>
</%def>

<table width="100%" class="table table-striped">
  <caption>${_("Kasutajarollid soorituskohtadel")}</caption>
  <thead>
    <tr>
      ${h.th(_("Soorituskoht"))}
      ${h.th(_("Roll"))}
      ${h.th(_("Kehtib kuni"))}
      <th></th>
    </tr>
  </thead>
  <tbody>
    <%
       rc = False
       kooligrupid = [r[0] for r in c.opt.kooligrupp]
       antavad = [r[0] for r in c.opt.get_antav_kooligrupp(c.app_ekk)]
    %>
    % for cnt,rcd in enumerate(c.kasutaja.kasutajarollid):
      % if rcd.kasutajagrupp_id in kooligrupid:
        <%
          rc = True
          kasutajagrupp = rcd.kasutajagrupp
          koht = rcd.koht
        %>
    <tr>
      <td>${h.link_to(koht.nimi, h.url('admin_koht', id=rcd.koht.id))}</td>
      <td>${c.opt.grupp_dict().get(rcd.kasutajagrupp_id)}
        % if rcd.kasutajagrupp_id == const.GRUPP_AINEOPETAJA:
        / ${rcd.aine_nimi}
        % endif
      </td>
      <td>${h.str_from_date(rcd.kehtib_kuni_ui)}</td>
      <td align="right">
        % if c.user.has_permission('kasutajad', const.BT_UPDATE) and rcd.kasutajagrupp_id in antavad:
        ${h.remove(h.url('admin_kasutaja_delete_koht', kasutaja_id=c.kasutaja.id,
        id=rcd.id, sub='roll'), confirm_id="confirm_kr_%s" % rcd.id)}
        <span id="confirm_kr_${rcd.id}" style="display:none">
          ${_("Kas oled kindel, et soovid isikult rolli ära võtta ({kool}, {roll})?").format(kool=koht.nimi, roll=kasutajagrupp.nimi)}
        </span>
        % if c.kasutaja.on_labiviija:
        <% url = h.url('admin_kasutaja_edit_koht', kasutaja_id=c.kasutaja.id, id=rcd.id, sub='roll') %>
        ${h.btn_to_dlg('', url, title=_("Rolli kehtivusaja muutmine"),
        size='lg', mdicls='mdi-file-edit', level=0)}
        % endif
        % endif
      </td>
    </tr>
      % endif
    % endfor
    % if not rc:
    <tr>
      <td colspan="4">${_("Isikul pole üheski soorituskohas kasutajarolli")}</td>
    </tr>
    % endif
  </tbody>
  % if c.user.has_permission('kasutajad', const.BT_UPDATE) and c.kasutaja.on_labiviija:
  <tfoot>
    <tr>
      <td colspan="4">
        ${h.btn_to_dlg(_("Lisa soorituskoht"), h.url('admin_kasutaja_new_koht',
        kasutaja_id=c.kasutaja.id, sub='roll'), title=_("Soorituskoht"), width=600, mdicls='mdi-plus')}
      </td>
    </tr>
  </tfoot>
  % endif
</table>

<table width="100%" class="table table-striped" >
  <caption>${_("Isikuga seotud soorituskohad (isik on hindajate, korraldajate jne kiirvalikus)")}</caption>
  <thead>
    <tr>
      ${h.th(_("Soorituskoht"))}
      <th width="20px"></th>
    </tr>
  </thead>
  <tbody>
    <% rc = False %>
    % for cnt,rcd in enumerate(c.kasutaja.kasutajakohad):
    <% rc = True %>
    <tr>
      <td>${h.link_to(rcd.koht.nimi, h.url('admin_koht', id=rcd.koht.id))}</td>
      <td>
      % if c.user.has_permission('kasutajad', const.BT_UPDATE):
      ${h.remove(h.url('admin_kasutaja_delete_koht', kasutaja_id=c.kasutaja.id,
      id=rcd.id, sub='koht'))}
      % endif
      </td>
    </tr>
    % endfor
    % if not rc:
    <tr>
      <td colspan="2">${_("Isik ei ole ühegi soorituskohaga seotud")}</td>
    </tr>
    % endif
  </tbody>
  % if c.user.has_permission('kasutajad', const.BT_UPDATE) and c.kasutaja.on_labiviija:
  <tfoot>
    <tr>
      <td colspan="2">
        ${h.btn_to_dlg(_("Lisa soorituskoht"), h.url('admin_kasutaja_new_koht',
        kasutaja_id=c.kasutaja.id, sub='koht'), title=_("Soorituskoht"), width=600)}
      </td>
    </tr>
  </tfoot>
  % endif
</table>




<%
  q = (model.Session.query(model.Kasutajarollilogi)
       .filter_by(kasutaja_id=c.kasutaja.id)
       .filter_by(tyyp=const.USER_TYPE_KOOL)
       .order_by(model.sa.desc(model.Kasutajarollilogi.id)))
  items = list(q.all())
%>
% if items:
<table class="table mt-3">
  <caption>${_("Kasutajarollide muutmise logi")}</caption>
  <thead>
    <tr>
      ${h.th(_("Muutja"))}
      ${h.th(_("Aeg"))}
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
        ${krl.sisu}
      </td>
    </tr>
    % endfor
  </tbody>
</table>
% endif
