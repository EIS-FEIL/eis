<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<% c.includes['subtabs'] = True %>
</%def>
<%def name="page_title()">
${_("Hindamine")} | ${c.toimumisaeg.testimiskord.test.nimi} ${c.toimumisaeg.millal}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"), h.url('hindamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, c.toimumisaeg.millal))} 
${h.crumb(_("Läbiviijate määramine"), h.url('hindamine_hindajad', toimumisaeg_id=c.toimumisaeg.id))}
${h.crumb(_("Ümbersuunamised"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'hindamised' %>
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'maaramine' %>
<%include file="tabs.mako"/>
</%def>

<%def name="draw_subtabs()">
<%include file="maaramine.tabs.mako"/>
</%def>

${h.form_search(url=h.url('hindamine_suunamised', toimumisaeg_id=c.toimumisaeg.id))}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Hindaja"),'hindaja_id')}
        ${h.select('hindaja_id', c.hindaja_id, c.hindajad_opt, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Hindamiskogum"),'hindamiskogum_id')}
        ${h.select('hindamiskogum_id', c.hindamiskogum_id, c.hindamiskogumid_opt, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
            ${h.checkbox('lykatud', 1, checked=c.lykatud, label=_("Ainult tagasilükatud hindamised"),
            onclick="if(!$(this).prop('checked')) $('#uusmaaramata').prop('checked',false)")}
            ${h.checkbox('uusmaaramata', 1, checked=c.lykatud, label=_("Ainult need, millel uus hindaja määramata"),
            onclick="if($(this).prop('checked')) $('#lykatud').prop('checked',true)")}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Probleemi liik"),'probleem')}
            <%
               opt_probleem = [(const.H_PROBLEEM_SISESTAMATA, _("Sisestamata")), (const.H_PROBLEEM_SISESTUSERINEVUS, _("Sisestusvead")), (const.H_PROBLEEM_HINDAMISERINEVUS, _("Hindamiserinevused"))]
            %>
            ${h.select('probleem', c.probleem, opt_probleem, empty=True)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.btn_search()}
        ${h.submit(_("CSV"), id='csv', level=2)}
      </div>
    </div>
  </div>

</div>
${h.end_form()}

${h.form_save(None, form_name="form_list")}
${h.hidden('sub', 'suunatagasi')}
${h.hidden('hliik', '')}
<div class="listdiv">
<%include file="maaramine.suunamised_list.mako"/>
</div>
<br/>

<script>
  function toggle_add(liik)
  {
     ## kõigi teist liiki hindamiste linnukesed eemaldada
     $('input:checked.hindamine1_id:not(.hindamine-'+liik+')').prop('checked', false);
     $('input#hliik').val(liik);

         var visible = ($('input:checked.hindamine1_id').length > 0);
         if(visible)
         { 
           $('span#add.invisible').removeClass('invisible');
         }
         else
         {
           $('span#add').filter(':not(.invisible)').addClass('invisible');
         }
  };
  function otsihindaja()
  {
     var plainurl="${h.url('hindamine_suunamised',toimumisaeg_id=c.toimumisaeg.id, sub='otsihindaja', partial=True, rid=True)}" + 
         '&liik=' + $('input#hliik').val() +
         '&list_url=' + encodeURIComponent($('input.list_url').val());
##         '&list_url=' + encodeURIComponent($('input.list_url').val() + '&page=' + $('div#listdiv a.paginate_act').text());
       
     open_dialog({'title': '${_("Uue hindaja määramine")}', 'url': plainurl, 'method': 'get'});
  };
</script>
<span id="add" class="invisible">
${h.submit(_("Suuna hindajale tagasi"), id='suunatagasi', level=2)}
${h.button(_("Määra uus hindaja"), onclick='otsihindaja()', level=2)}
</span>
${h.end_form()}
