
<%include file="translating.mako"/>
<div style="float:right" class="brown">
  % if len(c.test.keeled) == 1:
  ${model.Klrida.get_str('SOORKEEL', c.test.lang)}
  % else:
  % for lang in c.test.keeled:
  % if lang == c.test.lang:
  ${h.radio('lang', '', checked=not(c.lang), ronly=False, class_="nosave", label='%s (%s)' % (c.test.lang_nimi, _("põhikeel")))}
  % else:
  ${h.radio('lang', lang, checkedif=c.lang, ronly=False, class_="nosave", label=model.Klrida.get_str('SOORKEEL', lang))}
  % endif
  % endfor
  <script>
    $(document).ready(function(){
    $('input[name=lang]').click(function(){
    var lang = $(this).val();
    var url = "${h.url_current(lang='__LANG__')}".replace("__LANG__", lang);
    window.location.replace(url);
    });
    });
  </script>
  % endif
</div>
