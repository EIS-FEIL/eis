## -*- coding: utf-8 -*- 
## Põhikeele ja tõlkekeelte sisestamine/vaatamine ülesande ja testi juures
% if not c.pohikeeleta:
  <tr>
    <td class="fh">${_("Põhikeel")}</td>
    <td>${h.select('f_lang', c.item.lang, c.opt.klread_kood('SOORKEEL', vaikimisi=c.item.lang))}</td>
    <td colspan="4">
    % if c.lang_tr_konesyntees:
      ${h.checkbox('f_konesyntees', 1, checked=c.item.konesyntees, label=_("Kõnesüntees"))}
    % endif
    </td>
  </tr>
% endif
  <tr>
    <td class="fh">${_("Tõlkekeeled")}</td>
    <td colspan="5">
      <% keeled = c.item.keeled %>
      % for (value, lang_name, value_id) in c.opt.SOORKEEL:
      ${h.checkbox('skeel', value=value, checked=value in keeled, label=lang_name)}
% if c.lang_tr_del:
      ${h.hidden('f_lang_%s_del' % value, '')}
% endif
      % endfor
% if c.is_edit:
      <script>
      $(document).ready(function(){
        lang_choice();
        $('#f_lang').change(lang_choice);
      });
      function lang_choice()
      {
        var lang = $('#f_lang').val();
        $('input[name="skeel"]').removeAttr('disabled');
        ## deaktiveerime soorituskeele
        $('input[name="skeel"][value="'+lang+'"]').attr('disabled','disabled');
      }
% if c.lang_tr_del:
      $('input[name="skeel"]').change(function(){
         if($(this).prop('checked')==false)
         {
            var d = $('input[name="f_lang_' + $(this).val() + '_del"]');
            if(confirm('${_("Kas lisaks keele peitmisele kustutada ka tõlketekstid?")}'))
               d.val('1');
            else
               d.val('');
         }
      });
% endif
      </script>
% endif
    </td>
  </tr>
