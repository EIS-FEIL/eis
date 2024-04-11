${h.form_search()}
${h.hidden('sub','otsihindaja')}
${h.hidden('partial','true')}
${h.hidden('liik', c.liik)}
<h2>
${_("Uue hindaja valik")}
</h2>

<table class="search2" width="100%" >
  <tr>
    <td class="fh">${_("Eesnimi")}</td>
    <td width="160px">${h.text('eesnimi', c.eesnimi)}</td>
    <td class="frh">${_("Perekonnanimi")}</td>
    <td width="160px">${h.text('perenimi', c.perenimi)}</td>
    <td>
      ${h.button(_("Otsi"), onclick="var url='%s?'+$(this.form).serialize();dialog_load(url);" % h.url_current('index'))}
    </td>
  </tr>
</table>
${h.end_form()}
<br/>

${h.form_save(None, form_name='form_otsihindaja')}

${h.hidden('sub', 'otsihindaja')}
${h.hidden('list_url', c.list_url)}
${h.hidden('hindamised_id', c.hindamised_id)}
<script>
  $(document).ready(function(){
    var f = $('input[name="hindamine1_id"]:checked');
    var buf = "";
    for(var i=0; i<f.length; i++) buf += ','+f.eq(i).val();
    $('input[name="hindamised_id"]').val(buf);
  });
</script>

<table width="100%"  class="table table-borderless table-striped">
  <tr>
    <th></th>
    ${h.th(_("Läbiviija"))}
    ${h.th(_("Hindamiskogum"))}
  </tr>
  % for rcd in c.items:
  <% lv_id, nimi, hk_tahis = rcd %>
  <tr>
    <td>
      ${h.submit(_("Vali"), id='lv_%s' % lv_id)}
    </td>
    <td>${nimi}</td>
    <td>${hk_tahis}</td>
  </tr>
  % endfor
</table>
${h.end_form()}

