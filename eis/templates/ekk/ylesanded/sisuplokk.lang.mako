<% 
  c.ylesanne = c.ylesanne or c.item
  action = (c.is_edit or c.is_tr) and 'edit' or 'show'
%>
<div class="d-flex justify-content-end">
  % if len(c.ylesanne.keeled) > 1:
  <div class="m-2">
    % for lang in c.ylesanne.keeled:
    <span class="nowrap">
      % if lang == c.ylesanne.lang:
      <% label = '%s (%s)' % (c.ylesanne.lang_nimi, _("põhikeel")) %>
      ${h.radio('lang2', '', checked=not(c.lang), ronly=False, class_='nosave', label=label)}
      % else:
      ${h.radio('lang2', lang, checkedif=c.lang, ronly=False, class_='nosave',
      label=model.Klrida.get_str('SOORKEEL', lang))}
      % endif
    </span>
    % endfor
    <script>
      $(function(){
      $('input[name="lang2"]').click(function(){
      var lang = $(this).val();
      var url = "${h.url_current(action, lang='__LANG__')}".replace("__LANG__", lang);
      window.location.replace(url);
      });
      });
    </script>
  </div>
  % else:
    <span class="nowrap"> ${c.ylesanne.lang_nimi} (${_("põhikeel")})</span>
  % endif
</div>
