<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<% c.tab1 = 'tagasisideviis' %>
<%include file="tabs.mako"/>
</%def>
<%def name="draw_subtabs()">
<%include file="tagasiside.tabs.mako"/>
</%def>

<%def name="page_title()">
${_("Test")}: ${c.test.nimi or ''} | ${_("Tagasiside")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Testid"), h.url('testid'))} 
${h.crumb(c.test.nimi or _("Test"))} 
${h.crumb(_("Tagasiside"))}
</%def>
<%def name="require()">
<%
c.includes['subtabs'] = True
%>
</%def>
<%def name="active_menu()">
<% c.menu1 = 'testid' %>
</%def>

<% c.is_edit = c.user.has_permission('ekk-testid', const.BT_UPDATE, c.test) %>
${h.form_save(None)}
${h.hidden('lang', c.lang)}
${h.hidden('is_tr', c.is_tr)} 

<div class="form-wrapper mb-1">
  <div class="form-group row">
    ${h.flb3(_("Tagasiside mall"), 'mall')}
    <div class="col-md-9" id="mall">
      <%
        opt_tsmall = [('', _("Ilma tagasisideta"))] + [(str(k), v) for k, v in c.opt.tsmall]        
        current = c.test.tagasiside_mall
        if current is None:
           current = ''
      %>
      ${h.select_radio('f_tagasiside_mall', current, opt_tsmall, linebreak=True)}
    </div>
  </div>
  <div id="ajakulu" class="form-group row invisible">
    ${h.flb3(_("Ajakulu näitamine"), 'f_ajakulu_naitamine')}
    <div class="col-md-9">
      <%
        if len(c.test.testiosad) == 1:
            opt_an = ((str(const.AJAKULU_POLE), _("Ei näidata")),
                      (str(const.AJAKULU_OSA), _("Näidatakse")))
        else:
            opt_an = ((str(const.AJAKULU_POLE), _("Ei näidata")),
                      (str(const.AJAKULU_OSA), _("Ainult osade kaupa")),
                      (str(const.AJAKULU_TEST), _("Ainult testi koguaeg")),
                      (str(const.AJAKULU_KOIK), _("Testi koguaeg ja osade kaupa")))
      %>
      ${h.select_radio('f_ajakulu_naitamine', str(c.test.ajakulu_naitamine), opt_an, True)}
    </div>
  </div>
</div>

<script>
  $('#ajakulu').toggleClass('invisible', !$('input[name="f_tagasiside_mall"][value="${const.TSMALL_DIAG}"]').prop('checked'));  
  $('input[name="f_tagasiside_mall"]').change(function(){
    $('#ajakulu').toggleClass('invisible', !$('input[name="f_tagasiside_mall"][value="${const.TSMALL_DIAG}"]').prop('checked'));  
  });
</script>

% if c.is_edit:
${h.submit(_("Salvesta"))}
% endif

${h.end_form()}
