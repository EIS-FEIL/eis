<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

<%def name="require()">
<%
c.includes['ckeditor'] = True
%>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'ylesanded' %>
</%def>

<%def name="page_headers()">
<style>
  .glyphicon {
  color: #dd7f26;
  }
</style>
</%def>

<%def name="page_title()">
${c.ylesanne.nimi} | ${_("Tagasiside")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Ülesandepank"), h.url('ylesanded'))} 
${h.crumb(c.ylesanne.nimi or c.ylesanne.id, h.url('ylesanne', id=c.ylesanne.id))} 
${h.crumb(_("Tagasiside"))}
</%def>
<%
  c.can_edit = c.user.has_permission('ylesanded', const.BT_UPDATE,c.ylesanne)
  if c.is_edit:
    if c.lang and c.user.has_permission('ylesanded-tolkimine', const.BT_UPDATE, c.ylesanne):
        # tõlkimise ajal on ainult tõlkeväljad kirjutatavad
        c.is_edit = False
        c.is_tr = True
    elif not c.lang and \
            not c.user.has_permission('ylesanded',const.BT_UPDATE, c.ylesanne) and \
            c.user.has_permission('ylesanded-toimetamine', const.BT_UPDATE,c.ylesanne):
        # toimetaja tohib ainult tekstivälju kirjutada
        c.is_edit = False
        c.is_tr = True
%>
<div width="100%" align="right" class="brown">
     % if len(c.ylesanne.keeled) > 1:
       % for lang in c.ylesanne.keeled:
         % if lang == c.ylesanne.lang:
            ${h.radio('lang', '', checked=not(c.lang), ronly=False, class_='nosave', label='%s (%s)' % (c.ylesanne.lang_nimi, _("põhikeel")))}
         % else:
            ${h.radio('lang', lang, checkedif=c.lang, ronly=False, class_='nosave', label=model.Klrida.get_str('SOORKEEL', lang))}
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
     % else:
         ${c.ylesanne.lang_nimi} (${_("põhikeel")})      
     % endif
</div>
<%include file="tagasiside.mako"/>
