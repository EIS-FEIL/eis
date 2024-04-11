% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
<%
   if c.kord_id and isinstance(c.kord_id, list):
      korrad_id = map(int, c.kord_id)
   elif c.kord_id:
      korrad_id = [int(c.kord_id)]
   else:
      korrad_id = []

   if c.item_id and isinstance(c.item_id, list):
      items_id = c.item_id
   elif c.kord_id:
      items_id = [c.item_id]
   else:
      items_id = []
  
%>
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th_sort('test.nimi', _("Test"))}
      ${h.th_sort('testimiskord.aasta', _("Aasta"))}
      ${h.th(_("Testimiskord"))}
      ${h.th(_("Harno statistikas"))}
      ${h.th(_("Avalikus statistikas"))}
      ${h.th(_("Raport"), colspan=2)}      
    </tr>
  </thead>
  <tbody>
    % for test, aasta in c.items:
    <%
       tkorrad = [r for r in test.testimiskorrad if r.aasta == aasta]
       tkorrad_ekk = []
       tkorrad_aval = []
       len_tkorrad = len(tkorrad)
       kursused = [r.kursus_kood for r in test.testikursused if r.kursus_kood] or [None]
       len_kursused = len(kursused)
       tkorrad_ekk = [r for r in tkorrad if r.statistika_ekk_kpv]
       tkorrad_aval = [r for r in tkorrad if r.statistika_aval_kpv]
    %>
    % for ind_tk, rcd in enumerate(tkorrad):
    <tr>
      % if ind_tk == 0:
      <td rowspan="${len_tkorrad}">
        ${test.nimi}
      </td>
      <td rowspan="${len_tkorrad}">
        ${aasta}
      </td>
      % endif
      <td nowrap>
            ${h.checkbox('kord_id', rcd.id, onclick='toggle_add()', 
            checked=rcd.id in korrad_id, class_='nosave kord_id', label=rcd.tahised)}
      </td>
      <td>
            % if rcd.statistika_ekk_kpv:
            ${_("Alates")} ${h.str_from_date(rcd.statistika_ekk_kpv)}
            % else:
            ${_("Ei")}
            % endif
      </td>
      <td>
            % if rcd.statistika_aval_kpv:
            ${_("Alates")} ${h.str_from_date(rcd.statistika_aval_kpv)}
            % else:
            ${_("Ei")}
            % endif
      </td>
      % if ind_tk == 0:
      % for ind_k, kursus in enumerate(kursused):
        ${self.tds_kursus(test, aasta, kursus, len_kursused, len_tkorrad, tkorrad_ekk, tkorrad_aval, items_id)}
      % endfor
      % endif
    </tr>
    % endfor
    % endfor
  </tbody>
</table>

% endif

<%def name="tds_kursus(test, aasta, kursus, len_kursused, len_tkorrad, tkorrad_ekk, tkorrad_aval, items_id)">
<%
  raportid = model.Statistikaraport.get_raportid(test.id, kursus, aasta)
  item_id = f"{test.id}-{aasta}-{kursus or ''}"
  if kursus:
      label = model.Klrida.get_str('KURSUS', kursus, ylem_kood=test.aine_kood)
  else:
      label = ''
  avalik = True
%>
      <td rowspan="${len_tkorrad}" ${len_kursused == 1 and 'colspan="2"' or ''}>
        <div>
        % if tkorrad_ekk:
            ${h.checkbox('item_id', item_id, onclick='toggle_add2()', 
            checked=item_id in items_id, class_='nosave item_id', label=label)}
        % else:
            ${label}
        % endif
        </div>

        
        % for raport in raportid:
        <div>
        ${h.str_from_date(raport.modified)}
        % if raport.format == 'pdf':
        ${h.pdflink_to(h.url('eksamistatistika_riikliktagasiside', test_id=test.id, aasta=aasta, kursus=kursus or '', pdf=1))}
        % else:
        ${h.filelink_to(h.url('eksamistatistika_riikliktagasiside', test_id=test.id, aasta=aasta, kursus=kursus or ''))}
        % endif

        <%
          if not raport.avalik:
             avalik = False
        %>
        </div>
        % endfor
        % if raportid:
          % if avalik:
          ${_("Avaldatud")}
          % elif tkorrad_aval and tkorrad_aval == tkorrad_ekk:
          ${h.btn_to(_("Avalda"), h.url_current('update', sub='avalda', id=item_id), method='post')}
          % endif
        % endif
      </td>
</%def>

<%def name="sboold(b, d)">
% if b and d:
${h.str_from_date(d)}
% else:
${h.sbool(b)}
% endif
</%def>
      
<script>
  function toggle_add()
  {
         var visible = ($('input:checked.kord_id').length > 0);
         $('#add').toggleClass('d-none', !visible);
  }
  function toggle_add2()
  {
         var visible = ($('input:checked.item_id').length > 0);
         $('#add2').toggleClass('d-none', !visible);
  }
  $(function(){
     toggle_add();
     toggle_add2();
  });
</script>
