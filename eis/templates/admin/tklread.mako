<%include file="/common/message.mako" />

<%
   c.kirjeldus_nimetus = lambda kood: kood == 'ASPEKT' and _("Hindamisjuhis") or kood == 'VAHEND' and _("Sisu") or None
%>

<%def name="row(prefix, item, on_kirjeldus=False)">
<%
   in_use = item.in_use
   tran = item.tran(c.lang, False)
%>
    <tr>
      <td nowrap>
        ${item.kood}
        ${h.hidden('%s.kood' % prefix, item.kood)}
        ${h.hidden('%s.id' % prefix, item.id)}
      </td>
      <td>
        % if c.item.kood == 'TOOKASK':
        ${item.kirjeldus}
        % else:
        ${item.nimi}
        % endif
      </td>
      <td>
       % if c.item.kood == 'TOOKASK':
        ${h.hidden('%s.nimi' % prefix, '-')}
        ${h.textarea('%s.kirjeldus' % prefix, tran and tran.kirjeldus or '', maxlength=512, rows=3)}
       % else:
        ${h.text('%s.nimi' % prefix, tran and tran.nimi or '')}        

        % if on_kirjeldus:
          % if c.is_edit and item.kood:
                  ${h.btn_to_dlg(_("Muuda kirjeldus"), 
                  h.url('admin_edit_tklassifikaator', id=item.id, sub='kirjeldus', lang=c.lang, partial=True), 
                  title=c.kirjeldus_nimetus(c.item.kood), width=800)}             
          % endif
          % if item.kirjeldus:
            % if c.item.kood == 'VAHEND':
              <% 
                 onclick = "open_dlg({dialog_id:'vahend_%s', title: '%s', iframe_url:'%s', width:'%s', height:'%s')" % (item.id, item.nimi, h.url('admin_klrida', id=item.id, sub='vahend', lang=c.lang), item.laius or 600, item.korgus or 400) 
                 ikoon = item.ikoon_url or '/static/abivahendid/muu_ikoon.png'
              %>
              ${h.image(src=ikoon, onclick=onclick, alt=item.nimi, title=item.nimi, height=32)}
            % else:
              ${h.literal(item.tran(c.lang).kirjeldus)}              
            % endif
          % endif
        % endif
       % endif
      </td>
      <td>
        ${item.jrk}
      </td>
      <td>
        ${h.sbool(item.kehtib)}
      </td>
    </tr>
</%def>

<table id="gridtbl" class="table tablesorter list" >
  <caption>${c.item.nimi}</caption>
  <thead>
    <tr>
      <th width="60px">${_("Kood")}</th>
      <th width="40%">${_("Nimi")}</th>
      <th width="40%">${_("Tõlge")}</th>
      <th>${_("Järjestus")}</th>
      <th>${_("Kehtiv")}</th>
    </tr>
  </thead>
  <tbody>
  %   for cnt,item in enumerate(c.items):
        ${self.row('k-%s' % cnt, item, c.kirjeldus_nimetus(c.item.kood))}
  %   endfor
  </tbody>
</table>
<br/>
