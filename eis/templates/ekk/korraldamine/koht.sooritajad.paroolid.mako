${h.form_save(None, form_name="form_save_pwd")}
${h.hidden('sub', 'parool')}
<table width="100%" class="table table-borderless table-striped tablesorter" >
  <thead>
    <tr>
      <th sorter="false">${h.checkbox('all', '', checked=True, title=_("Vali kõik"))}</th>
      <th>${_("Isikukood")}</th>
      <th>${_("Eesnimi")}</th>
      <th>${_("Perekonnanimi")}</th>
      <th>${_("Testiparooli omistamine")}</th>
    </tr>
  </thead>
  <tbody>
  % for rcd in c.items:
  <%
    sooritaja = rcd.sooritaja
    kasutaja = sooritaja.kasutaja
  %>
  <tr>
    <td>
      ##% if not kasutaja.on_kehtiv_ametnik and not kasutaja.on_labiviija:
        ${h.checkbox('pwd_id', rcd.id, checked=True, onclick="toggle_add()", title=_("Vali rida {s}").format(s=kasutaja.isikukood))}
      ##% endif
    </td>
    <td>${kasutaja.isikukood}</td>
    <td>${sooritaja.eesnimi}</td>
    <td>${sooritaja.perenimi}</td>
    <td>
         <% 
           item = None
           for r in sooritaja.testiparoolilogid:
              item = r
              break
         %>
         % if item:
              ${h.str_from_datetime(item.modified)} ${c.opt.kasutaja_nimi(item.creator)}
         % else:
            <i>${_("Testiparooli pole omistatud")}</i>
         % endif
   </td>
  </tr>
  % endfor
  </tbody>
</table>
<br/>
<script>
  $(document).ready(function(){
     $('table#table_isikud').tablesorter();
     $('input[name="all"]').click(function(){
        $('input[name="pwd_id"]').prop('checked', $(this).prop('checked'));
        toggle_add();
     });
     toggle_add();
  });
  function toggle_add(){   
     $('input[id="genereeri"]').toggle($('input[name="pwd_id"]:checked').length > 0);
  }
</script>
${h.submit_dlg(_("Genereeri testiparoolid"), id="genereeri")}
${h.end_form()}
