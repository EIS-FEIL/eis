${h.form_search(url=h.url('korraldamine_koht_otsisooritajad',
toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht.id))}

<div class="gray-legend p-3">
  <div class="row">
    <div class="col-md-4">
      <div class="form-group">
        ${h.flb(_("Isikukood"), 'isikukood')}
        ${h.text('isikukood', c.isikukood, maxlength=50)}
      </div>
    </div>
    <div class="col-md-4">
      <div class="form-group">
        ${h.flb(_("Soovitud piirkond"),'piirkond_id')} 
        <div>
          <%
            c.piirkond_id = c.piirkond_id
            c.piirkond_field = 'piirkond_id'
          %>
          <%include file="/admin/piirkonnavalik.mako"/>
        </div>
      </div>
    </div>
    <div class="col-md-4 d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.submit_dlg(_("Otsi"))}
      </div>
    </div>
  </div>
</div>

${h.end_form()}

<%include file="/common/message.mako"/>
% if c.items:
${h.form(h.url('korraldamine_koht_sooritajad', toimumisaeg_id=c.toimumisaeg.id,testikoht_id=c.testikoht.id), method='post')}

<%
   kuva_reg_url = c.user.has_permission('regamine', const.BT_SHOW)
%>

<div class="listdiv">
      <table border="0"  class="table table-borderless table-striped tablesorter" id="table_isikud" width="100%">
        <col width="20px"/>
        <thead>
          <tr>
            <th sorter="false">${h.checkbox1('all',1, title=_("Vali kõik"))}</th>
            ${h.th(_("Testisooritaja"))}
            ${h.th(_("Õppeasutus"))}
            ${h.th(_("Soovitud piirkond"))}
            ${h.th(_("Soorituskeel"))}
          </tr>
        </thead>
        <tbody>
          % for n, rcd in enumerate(c.items):
          <% tos, s, k = rcd %>
          <tr>
            <td>
              ${h.checkbox('valik_id', s.id, class_="valik_id", onclick="toggle_add()", title=_("Vali rida {s}").format(s=k.isikukood))}
            </td>
            <td>
              ${k.isikukood}
              % if kuva_reg_url:
              ${h.link_to(k.nimi, h.url('regamine', id=s.id), target='_blank')}
              % else:
              ${k.nimi}
              % endif
            </td>
            <td>
              ${s.koolinimi and s.koolinimi.nimi or s.kool_koht and s.kool_koht.nimi or k.kool_nimi or ''}
            </td>
            <td>${s.piirkond_nimi}</td>
            <td>${model.Klrida.get_lang_nimi(s.lang)}</td>
          </tr>
          % endfor
        </tbody>
      </table>
<script>
  $(function(){
     $('table#table_isikud').tablesorter();
  });
  function toggle_add(){
    $('span#add').toggle($('input.valik_id:checked').length > 0);
  }
  $('input#all').click(function(){
    $('input.valik_id').prop('checked', this.checked); toggle_add();
  });
</script>
<span id="add" style="display:none">
  ${h.submit(_("Salvesta"), id='add_isik')}
</span>
</div>

${h.end_form()}

% endif

