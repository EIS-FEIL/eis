% if c.items != '':
${h.pager(c.items)}
% endif
% if c.items:
${h.form_save(None)}
${h.hidden('suund', c.suund)}
${h.hidden('testikoht_tahis', c.testikoht_tahis)}

<table width="100%" class="table table-borderless table-striped tablesorter" border="0" >
  <thead>
    <tr>
      ${h.th(_('Piirkond'))}
      ${h.th(_('Keel'))}
      ${h.th(_('Soorituskoht'))}
      ${h.th(_('Suund'))}
      ${h.th(_('Koti nr'))}
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% kott, tkoht_tahis, koht_nimi, piirkond, lang = rcd %>
    <tr>
      <td>${piirkond and piirkond.get_nimi_ylematega() or ''}</td>
      <td>${model.Klrida.get_lang_nimi(lang)}</td>
      <td>${tkoht_tahis or ''} ${koht_nimi or ''} 
      </td>
      <td>${kott.suund_nimi}</td>
      ##<td>${kott.id}</td>
      <td>${h.posint10('kotinr_%s' % kott.id, kott.kotinr, class_='enternext')}</td>
    </tr>
    % endfor
  </tbody>
</table>
<br/>
${h.submit()}
${h.end_form()}
% endif
<script>
$(document).ready(function(){
 $('input.enternext').keypress(function(e){
## kui triipkoodilugeja vajutab sisestusväljal reavahetusele,
## siis viia fookus järgmisele sisestusväljale
   if(e.keyCode==13)
   {
     $(this).closest('tr').next('tr').find('input.enternext').focus();
     return false;
   }
   else
   {
     return true;
   }
 });
});
</script>
