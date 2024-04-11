## -*- coding: utf-8 -*- 
<%include file="/common/message.mako" />

${h.form_search()}
<div class="row margin0">
  <div class="col-sm-6 search1">
    <table class="search2" width="100%">
      <col width="50%"/>
      <col width="50%"/>
      <tr>
        <td class="fh">${_("Eesnimi")}</td>
        <td>${h.text('eesnimi', c.eesnimi)}</td>
      </tr>
      <tr>
        <td class="fh">${_("Perekonnanimi")}</td>
        <td>${h.text('perenimi', c.perenimi)}</td>
      </tr>
    </table>
  </div>
  <div class="col-sm-6 search1">
    <table width="100%">
      <tr>
        <td colspan="2">
          ${h.checkbox('jagatud', 1, checked=c.jagatud,
          label=_('Kuva need, kellele on juba jagatud'))}
        </td>
        <td colspan="2">
          ${h.submit_dlg(_("Otsi"), op='otsi')}
        </td>
      </tr>
    </table>
  </div>
</div>
${h.end_form()}
% if c.items != '':
${h.pager(c.items, msg_not_found=_('Isikuid ei leitud'), msg_found_one=_('Leitud üks isik'), msg_found_many=_('Leiti {n} isikut'))}
% endif
% if c.items:
${h.form(h.url_current('create'), method='post')}
      <table border="0" class="table table-borderless table-striped tablesorter" id="table_isikud" width="100%">
        <thead>
          <col width="80px"/>
          <col width="45%"/>
          <col width="45%"/>
          <tr>
            <th></th>
            ${h.th_sort('nimi', _("Nimi"))}
            <th>Kool</th>
          </tr>
        </thead>
        <tbody>
          % for k, tkv in c.items:
          <tr>
            <td>
              % if tkv:
              ##${h.submit_dlg(_('Tühista'), method='DELETE', op=tkv.id)}
              <%
                url_d = h.url('tookogumik_delete_otsivaataja', tookogumik_id=c.tookogumik.id, id=tkv.id)
                onclick = "submit_frm($(this.form), null, 'POST', '%s', $(this).closest('td'))" % url_d
              %>
              ${h.button(_('Tühista'), onclick=onclick)}
              % else:
              <% onclick="submit_frm($(this.form), '%s', 'POST', null, $(this).closest('td'))" % k.id %>
              ${h.button(_('Jaga'), onclick=onclick)}
              % endif
            </td>
            <td>${k.nimi}</td>
            <td>
              % for p in k.pedagoogid:
              % if p.koht:
              ${p.koht.nimi}<br/>
              % endif
              % endfor
            </td>
          </tr>
          % endfor
        </tbody>
      </table>
${h.end_form()}
% endif
