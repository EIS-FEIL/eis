## -*- coding: utf-8 -*- 
<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Kasutajate volitused")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Haldus"))}
${h.crumb(_("Kasutajate volitused"), h.url('admin_volitused'))}
${h.crumb(c.item.nimi)}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'admin' %>
</%def>


<h1>${c.item.nimi} (${c.item.isikukood})</h1>
## c.item on Kasutaja

<table class="table table-borderless table-striped tablesorter my-3">
  <caption>${_("Isikud, kes saavad kasutaja andmeid vaadata")}</caption>
  <thead>
    <tr>
      ${h.th(_("Volitatu"))}
      ${h.th(_("Olek"))}
      ${h.th(_("Tähtaeg"))}
      ${h.th(_("Volituse andja"))}
      ${h.th(_("Andmise aeg"))}
      ${h.th(_("Volituse eemaldaja"))}
      ${h.th(_("Eemaldamise aeg"))}
    </tr>
  </thead>
  <tbody>
    % for rcd in c.item.opilane_volitused:
    <%
      volitatu_kasutaja = rcd.volitatu_kasutaja
      andja_kasutaja = rcd.andja_kasutaja
      tyhistaja_kasutaja = rcd.tyhistaja_kasutaja
    %>
    <tr>
      <td>
        ${volitatu_kasutaja.isikukood}
        ${volitatu_kasutaja.nimi}
      </td>
      <td>${rcd.staatus_nimi}</td>
      <td>${h.str_from_date(rcd.kehtib_kuni)}</td>
      <td>
        ${andja_kasutaja.isikukood}
        ${andja_kasutaja.nimi}
      </td>
      <td>
        ${h.str_from_datetime(rcd.kehtib_alates)}
      </td>
      <td>
        % if tyhistaja_kasutaja:
        ${tyhistaja_kasutaja.isikukood}
        ${tyhistaja_kasutaja.nimi}
        % endif
      </td>
      <td>
        % if rcd.tyhistatud:
        ${h.str_from_datetime(rcd.tyhistatud)}
        % endif
      </td>
    </tr>
  % endfor
  </tbody>
</table>


<table class="table table-borderless table-striped tablesorter my-3">
  <caption>${_("Isikud, kelle andmeid kasutaja saab vaadata")}</caption>
  <thead>
    <tr>
      ${h.th(_("Õpilane"))}
      ${h.th(_("Olek"))}
      ${h.th(_("Tähtaeg"))}
      ${h.th(_("Volituse andja"))}
      ${h.th(_("Andmise aeg"))}
      ${h.th(_("Volituse eemaldaja"))}
      ${h.th(_("Eemaldamise aeg"))}
      <th></th>
    </tr>
  </thead>
  <tbody>
    % for rcd in c.item.volitatu_volitused:
    <%
      opilane_kasutaja = rcd.opilane_kasutaja
      andja_kasutaja = rcd.andja_kasutaja
      tyhistaja_kasutaja = rcd.tyhistaja_kasutaja
    %>
    <tr>
      <td>
        ${opilane_kasutaja.isikukood}
        ${opilane_kasutaja.nimi}
      </td>
      <td>${rcd.staatus_nimi}</td>
      <td>${h.str_from_date(rcd.kehtib_kuni_ui)}</td>
      <td>
        ${andja_kasutaja.isikukood}
        ${andja_kasutaja.nimi}
      </td>
      <td>
        ${h.str_from_datetime(rcd.kehtib_alates)}
      </td>
      <td>
        % if tyhistaja_kasutaja:
        ${tyhistaja_kasutaja.isikukood}
        ${tyhistaja_kasutaja.nimi}
        % endif
      </td>
      <td>
        % if rcd.tyhistatud:
        ${h.str_from_datetime(rcd.tyhistatud)}
        % endif
      </td>
      <td>
        % if not rcd.tyhistatud:
        ${h.remove(h.url('admin_delete_volitus', id=rcd.id))}
        % endif
      </td>
    </tr>
  % endfor
  </tbody>
  <tfoot class="pt-3">
    <tr>
      <td colspan="8" class="fh">
        ${h.form_save(c.item.id)}
        ${h.hidden('roll','opilane')}
        <div class="d-flex">
          <div class="item mr-5">
          ${h.flb(_("Isikukood"), 'isikukood')}
          ${h.text('isikukood', '', maxlength=25, class_="mr-4")}
          </div>
          <div class="item mr-5">
          ${h.flb(_("Kehtib kuni"),'kehtib_kuni')}
          ${h.date_field('kehtib_kuni','')}
          </div>
          <div class="item d-flex align-items-end">
            ${h.submit(_("Lisa volitus"), level=2)}
          </div>
        </div>
        ${h.end_form()}
      </td>
    </tr>
  </tfoot>
</table>
<br/>

