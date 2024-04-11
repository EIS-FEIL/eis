% if c.items != '':
${h.pager(c.items,msg_not_found=_("Teateid ei leitud"),
          msg_found_one=_("Leiti üks teade"),
          msg_found_many=_("Leiti {n} teadet"))}
% endif
% if c.items:
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
  <tr>
    <th>
      ${h.checkbox1('all', 1)}
    </th>
    % for h_sort, h_title in c.header:
    % if h_sort:
    ${h.th_sort(h_sort, h_title)}
    % else:
    ${h.th(h_title)}
    % endif
    % endfor
    <th>${_("Fail")}</th>
  </tr>
  </thead>
  <tbody>
  <% m6 = model.datetime.now() - model.timedelta(days=180) %>
  % for n, (ks, kiri) in enumerate(c.items):
      <%
        row = c.prepare_item((ks, kiri), n)
        rcd_url = h.url('minu_teade', id=ks.id)
        if ks.staatus == const.KIRI_UUS:
           cls = 'msg-new'
        elif ks.staatus == const.KIRI_ARHIIV:
           cls = 'msg-arch'
        else:
           cls = ''
        ks_cls = f'ks-{ks.staatus}'
        if ks.created < m6:
           # rohkem kui 6 kuu vanune teade, mida ei saa uueks märkida
           ks_cls += ' ks-old'
      %>
  <tr class="${cls}">
    <td>
      ${h.checkbox('ks_id', ks.id, class_=ks_cls)}
    </td>
    % for ind, value in enumerate(row):
    <td>
       % if ind == 3:
         ${h.link_to_dlg(value, rcd_url, title="Teade", size='lg')}
       % else:
         ${value}
       % endif
    </td>
    % endfor
    <td>
      % if kiri.has_file:
      <% url_pdf = h.url_current('download', id=ks.id, format=kiri.fileext) %>
        ${h.pdflink_to(url_pdf)}      
      % endif
    </td>
  </tr>
  % endfor
  </tbody>
</table>
% endif

<script>
function toggle_b(){
    var flds = $('input[name="ks_id"]:checked');
    $('button#loetuks').toggle(flds.filter('.ks-${const.KIRI_UUS}').length > 0);
    $('button#uueks').toggle(flds.filter('.ks-${const.KIRI_LOETUD},.ks-${const.KIRI_ARHIIV}').filter(':not(.ks-old)').length > 0);
    $('button#arhiivi').toggle(flds.filter('.ks-${const.KIRI_UUS},input.ks-${const.KIRI_LOETUD}').length > 0);  
    $('button#arhiivist').toggle(flds.filter('.ks-${const.KIRI_ARHIIV}').length > 0);  
}
## kõigi kirjade märkimine
$('input#all').click(function(){
    $('input[name="ks_id"]').prop('checked', this.checked);
    toggle_b();
});
$('input[name="ks_id"]').click(toggle_b);
toggle_b();
</script>
