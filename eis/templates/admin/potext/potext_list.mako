% if c.items:
<% c.is_edit = c.can_update %>
${h.hidden('page', c.page)}
${h.pager(c.items)}
<table width="100%" class="table table-borderless table-striped" border="0" >
  <tbody>
  % for n, (p_id, msgid, msgstr_en, msgstr) in enumerate(c.items):
  <% prefix = 'p-%d' % n %>
  <tr>
    <td>${p_id}</td>
    <td>
      ${h.hidden(prefix + '.id', p_id)}
      <pre style="white-space:pre-line"><xmp class="m-0">${msgid}</xmp></pre>
      % if c.lang != const.LANG_EN:
      <pre style="white-space:pre-line"><xmp class="m-0">${msgstr_en}</xmp></pre>
      % endif
      ${h.text(prefix + '.msgstr', msgstr)}
    </td>
  </tr>
  % endfor
  </tbody>
</table>
% endif
