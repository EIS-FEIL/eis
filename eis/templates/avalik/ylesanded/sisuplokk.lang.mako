## -*- coding: utf-8 -*- 
<% 
  c.ylesanne = c.ylesanne or c.item
  action = (c.is_edit or c.is_tr) and 'edit' or 'show'
%>
<div width="100%" align="right" class="brown">
    % if len(c.ylesanne.keeled) > 1:
       % for lang in c.ylesanne.keeled:
        <span class="nowrap">
         % if lang == c.ylesanne.lang:
            ${h.radio('lang2', '', checked=not(c.lang), ronly=False, class_='nosave')} ${c.ylesanne.lang_nimi} (${_("põhikeel")})
         % else:
            ${h.radio('lang2', lang, checkedif=c.lang, ronly=False, class_='nosave')}
              ${model.Klrida.get_str('SOORKEEL', lang)}
         % endif
        </span>
       % endfor
            <script>
              $(document).ready(function(){
                 $('input[name="lang2"]').click(function(){
                 var lang = $(this).val();
                 var url = "${h.url_current(action, lang='__LANG__')}".replace("__LANG__", lang);
                 window.location.replace(url);
                 });
              });
            </script>
     % else:
        <span class="nowrap"> ${c.ylesanne.lang_nimi} (${_("põhikeel")})</span>
     % endif
</div>
