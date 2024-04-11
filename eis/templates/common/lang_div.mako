## Põhikeele ja tõlkekeelte sisestamine/vaatamine ülesande ja testi juures
<% ch = c.lang_ch or h.colHelper('col-lg-3', 'col-lg-8') %>
% if not c.pohikeeleta:
  <div class="form-group row">
    ${ch.flb(_("Põhikeel"), 'f_lang')}
    <div class="col">
      ${h.select('f_lang', c.item.lang, c.opt.klread_kood('SOORKEEL', vaikimisi=c.item.lang))}
    </div>
    % if c.lang_tr_konesyntees or c.lang_asendatav:
    <div class="col-lg-12">
      % if c.lang_tr_konesyntees:
      ${h.checkbox('f_konesyntees', 1, checked=c.item.konesyntees, label=_("Kõnesüntees"))}
      % endif
      % if c.lang_asendatav:
      <div class="lang_switch" style="display:none">
        ${h.checkbox('lang_switch', 1, label=_("Vaheta omavahel põhikeele tekstid ja tõlkekeele tekstid"))}
      </div>
      % endif
    </div>
    % endif
  </div>
% endif
  <div class="row">
    ${ch.flb(_("Tõlkekeeled"), 'skeel')}
    <div class="col">        
      <% keeled = c.item.keeled %>
      % for (value, lang_name) in [r[:2] for r in c.opt.SOORKEEL]:
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
      % if c.lang_asendatav:
      if((lang != '${c.item.lang}') && (${h.json.dumps(keeled)}.indexOf(lang) > -1))
      {
         $('.lang_switch').show();
      }
      else
      {
         $('.lang_switch').hide(); $('#lang_switch').prop('checked', false);      
      }
      % endif
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
    </div>
  </div>
