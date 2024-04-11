<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>
<%def name="require()">
<%
c.includes['subtabs'] = True
%>
</%def>
<%def name="page_title()">
${c.test.nimi or ''} | ${_("Testi kirjeldus")}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_('Tulemused'), h.url('ktulemused'))}
${h.crumb(c.test.nimi, h.url('ktulemused_kirjeldus', test_id=c.test.id, testimiskord_id=c.testimiskord.id, kursus=c.kursus or ''))}
</%def>

<%def name="draw_before_tabs()">
<%include file="before.mako"/>
</%def>

<%def name="page_headers()">
<style>
  ## vormi alamosad vahelduva taustaga
  .fbrpart:nth-child(even) { background: #f2f2f2; }
  .fbrpart { padding:10px; }
  ## rohkem näitamiseks olev osa on algselt peidus
  .fbrtextmore {display: none}
  <%include file="/avalik/tagasiside/tagasiside.css"/>
</style>
</%def>

<div class="fbwrapper" url="${h.url_current(None, getargs=True)}">
  ${c.tagasiside_html}
</div>

${h.form_search(h.url_current('index'))}
<div class="d-flex flex-wrap mt-2">
  <div class="flex-grow-1">
    ${h.submit(_("PDF"), id="pdf", level=2)}
  </div>
  ${h.mdi_icon('mdi-chevron-up-circle-outline', size=24, title=_("Lehekülje algusse"), id='scrolltop', style="display:none")}
</div>
${h.end_form()}

<script>
## näita rohkem
$('.fbrtextless').prepend('${h.link_to(_("Näita rohkem"), mdicls='mdi-chevron-down', class_='showmore m-2')}');
$('.showmore').click(function(){
  $(this).hide();
  $(this).closest('.fbrtextless').find('.fbrtextmore').show();
  return false;
});
## näita vähem
$('.fbrtextmore').append('<div>${h.link_to(_("Näita vähem"), mdicls='mdi-chevron-up', class_='showless m-2')}</div>');
$('.showless').click(function(){
  $(this).closest('.fbrtextless').find('.fbrtextmore').hide();
  $(this).closest('.fbrtextless').find('.showmore').show();
  return false;
});
## lehekülje algusse
$('#scrolltop').click(function(){
  window.scrollTo(0,0);
});
$(function(){
$('#scrolltop').toggle($("body").height() > $(window).height());
});
</script>
