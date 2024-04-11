${h.form_search(url=h.url('korraldamine_koht_otsilabikohad',
toimumisaeg_id=c.toimumisaeg.id, testikoht_id=c.testikoht_id))}

<table width="100%" class="search" >
  <tr>
    <td class="frh" width="85">${_("Piirkond")}</td>
    <td colspan="2">
            <%
               c.piirkond_id = c.piirkond_id
               c.piirkond_field = 'piirkond_id'
            %>
            <%include file="/admin/piirkonnavalik.mako"/>
    </td>
  </tr>
  <tr>
    <td class="frh" width="85">${_("Maakond")}</td>
    <td>
      ${h.select('maakond_kood', c.maakond_kood, model.Aadresskomponent.get_opt(None), empty=True)}
    </td>
    <td class="field-header" width="85">
      ${h.button(_("Otsi"), onclick="var url='%s?'+$(this.form).serialize();dialog_load(url);" % h.url('korraldamine_koht_otsilabikohad',toimumisaeg_id=c.toimumisaeg.id,testikoht_id=c.testikoht_id))}
    </td>
  </tr>
</table>

${h.end_form()}
<br/>
<%include file="/common/message.mako"/>
% if c.items != '' and not c.items:
${_("Soorituskohti ei leitud")}
% elif c.items:
${h.form(h.url('korraldamine_koht_labiviijad', toimumisaeg_id=c.toimumisaeg.id,testikoht_id=c.testikoht_id), method='post')}
${h.hidden('sub','suunamine')}
${h.hidden('labiviijad_id', c.labiviijad_id)}
<script>
  $(document).ready(function(){
    var f = $('input.labiviija_id:checked');
    var buf = "";
    for(var i=0; i<f.length; i++) buf += ','+f.eq(i).val();
    $('#labiviijad_id').val(buf);
  });
</script>

<div class="listdiv">
      <table border="0"  class="table table-borderless table-striped tablesorter" id="table_isikud" width="100%">
        <thead>
          <tr>
            <td></td>
            ${h.th(_("Soorituskoht"))}
            ${h.th(_("Asukoht"))}
            ${h.th(_("Ruum"))}
            ${h.th(_("Läbiviija määramata"))}
          </tr>
        </thead>
        <tbody>
          % for n, rcd in enumerate(c.items):
          <% testiruum, koht, ruum = rcd %>
          <tr>
            <td>
              ${h.submit(_("Vali"),id='valik_id_%d' % testiruum.id)}
            </td>
            <td>${koht.nimi}</td>
            <td>
              ${koht.tais_aadress}
            </td>
            <td>${ruum and ruum.tahis or _("Määramata")}</td>
            <td>
              ## läbiviijad määramata
              <% 
                 maaramata = model.Labiviija.query.filter(model.Labiviija.testiruum_id==testiruum.id).filter(model.Labiviija.kasutaja_id==None).count() 
              %>
              ${maaramata or ''}
            </td>
          </tr>
          % endfor
        </tbody>
      </table>
<script>
  $(document).ready(function(){
     $('table#table_isikud').tablesorter();
  });
</script>
</div>

${h.end_form()}

% endif

