% if not c.data:
${_("Tagasiside puudub")}
% else:
% if c.ts_pohikeel:
${self.lang_sel(c.ts_pohikeel, c.ts_keeled)}
% endif
<table class="table table-borderless table-striped" width="100%" >
  <thead>
    <tr>
      <th>${_("Vahemik")}</th>
      <th>${_("Tagasiside")}</th>
      <th>${_("Õpilaste arv")}</th>
    </tr>
  </thead>
  <tbody>
% for nts_id, vahemik, msg, sooritajad, visible in c.data:
    <tr class="ts" ${not visible and 'style="display:none"' or ''}>
      <td>${vahemik}</td>
      <td>${msg}</td>
      <td>
        <% cnt = len(sooritajad) %>
        <div class="data-wrapper">
          % if cnt:
          <div class="t_sooritajad_cnt">
            <% bubble_id = 'bbl%d' % nts_id %>
            ${h.link_to_bubble(cnt, None, bubble_id=bubble_id)}
          </div>
          <div id="${bubble_id}" style="display:none">
            ${self.display_sooritajad(sooritajad)}
          </div>
          % else:
          <div>${cnt}</div>
          % endif
        </div>
      </td>
    </tr>
% endfor
  </tbody>
</table>
<div style="float:right;padding-top:3px;">
  ${h.button(_('Koondtulemus'), onclick="$('tr.ts').show();$(this).hide();")}
</div>
% endif

<%def name="display_sooritajad(sooritajad)">
        % for j_id, eesnimi, perenimi in sooritajad:
        <% nimi = '%s %s' % (eesnimi, perenimi) %>
        ${nimi}
        <br/>
        % endfor
</%def>

<%def name="lang_sel(pohikeel, keeled)">
<div align="right" width="100%" class="brown">
  % if len(keeled) > 1:
    % for lang in keeled:
      % if lang == pohikeel:
       ${h.radio('lang', '', checked=not(c.lang), ronly=False, class_="nosave")}
       ${model.Klrida.get_str('SOORKEEL', lang)} (põhikeel)
      % else:
       ${h.radio('lang', lang, checkedif=c.lang, ronly=False, class_="nosave")}
       ${model.Klrida.get_str('SOORKEEL', lang)}
      % endif
    % endfor
    <script>
    $(document).ready(function(){
    $('input[name=lang]').click(function(){
    var lang = $(this).val();
    var url = "${h.url('test_tootulemus', sub='ty', id=c.sooritaja_id, test_id=c.test.id, testiruum_id=c.testiruum_id, ty_id=c.ty_id, lang='__LANG__')}".replace("__LANG__", lang);
    dialog_load(url, "", 'GET', $('div#dialog_div'));
    dirty = false;
    });
    });
    </script>
  % endif
</div>
</%def>
