## Testile registreeritud erivajadustega sooritajad, kelle seast valitakse
## antud komplekti sooritajad

${h.form_save(None, h.url('test_komplekt_erisooritused',
test_id=c.test.id, komplekt_id=c.komplekt.id))}

<table class="table borderless tablesorter">
  <thead>
  <tr>
    ${h.th('')}
    ${h.th(_("Testisooritaja"))}
    ${h.th(_("Soorituskoht"))}
    ${h.th(_("Testsessioon"))}
    ${h.th(_("Eritingimused"))}
  </tr>
  </thead>
  <tbody>
  % for rcd in c.items:
  ## rcd on sooritus
  <%
    kasutaja = rcd.sooritaja.kasutaja
    testikoht = rcd.testikoht
    testimiskord = rcd.toimumisaeg.testimiskord
    testsessioon = testimiskord.testsessioon
  %>
  <tr>
    <td>
      ${h.checkbox('valik_id', rcd.id, onclick="toggle_add()", class_="valik_id")}
    </td>
    <td>
      ${kasutaja.isikukood}
      ${kasutaja.nimi}
    </td>
    <td>
      ${testikoht and testikoht.koht.nimi or ''}
    </td>
    <td>
      ${testsessioon and testsessioon.nimi or ''}
    </td>
    <td>
      <%
         vajadused = []
         for p in rcd.erivajadused:
             if p.kinnitus:
                buf = p.erivajadus_nimi or ''
                if p.kinnitus_markus:
                    buf += ' (%s)' % p.kinnitus_markus
                vajadused.append(buf)
         str_vajadused = ', '.join(vajadused) or '-'
      %>
      ${h.link_to(str_vajadused, h.url('regamine_erivajadus',id=rcd.id))}
    </td>
  </tr>
  % endfor
  </tbody>
</table>

<script>
  function toggle_add()
  {
         var visible = ($('input:checked.valik_id').length > 0);
         if(visible)
         { 
           $('div#add.invisible').removeClass('invisible');
         }
         else
         {
           $('div#add').filter(':not(.invisible)').addClass('invisible');
         }
  }
  $(document).ready(function(){
     toggle_saada();
  });
</script>

<div id="add" class="invisible">
${h.submit(_("Salvesta"))}
</div>
${h.end_form()}
