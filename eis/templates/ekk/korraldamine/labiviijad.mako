<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Testi korraldamine")} | ${c.test.nimi} ${h.str_from_date(c.toimumisaeg.alates)}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Korraldamine"), h.url('korraldamised'))} 
${h.crumb('%s %s' % (c.test.nimi, h.str_from_date(c.toimumisaeg.alates)))} 
${h.crumb(_("Läbiviijate määramine"))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'korraldamised' %>
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

${h.form_search(url=h.url('korraldamine_labiviijad', toimumisaeg_id=c.toimumisaeg.id))}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Läbiviija roll"),'roll_id')}
        ${h.select('roll_id', c.roll_id,
        c.toimumisaeg.get_labiviijagrupid_opt(), empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">        
        ${h.flb(_("Soorituskoha nimetus"),'nimi')}
        ${h.text('nimi', c.nimi)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">        
        ${h.flb(_("Piirkond"),'piirkond_id')}
            <%
               c.piirkond_id = c.piirkond_id
               c.piirkond_field = 'piirkond_id'
            %>
            <%include file="/admin/piirkonnavalik.mako"/>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">        
        ${h.flb(_("Maakond"),'maakond_kood')}
        ${h.select('maakond_kood', c.maakond_kood, 
            model.Aadresskomponent.get_opt(None),empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">        
        ${h.flb(_("Kuupäev"),'kuupaev')}
        ${h.select('kuupaev', h.str_from_date(c.kuupaev), c.opt_kuupaev, empty=True)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">    
      <div class="form-group">
        ${h.btn_search()}
        ${h.submit(_("CSV"), id='csv', class_="filter", level=2)}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

${h.form_save(None, h.url('korraldamine_labiviijad', toimumisaeg_id=c.toimumisaeg.id))}
<div class="listdiv">
<%include file="labiviijad_list.mako"/>
</div>
<br/>

<script>
  function toggle_viija()
  {
         var visible = ($('input:checked.labiviija_id').length > 0);
         if(visible)
         { 
           $('span#viija.invisible').removeClass('invisible');
         }
         else
         {
           $('span#viija').filter(':not(.invisible)').addClass('invisible');
         }
  }
  $(document).ready(function(){
     toggle_viija();
  });
</script>

<% c.can_update = c.user.has_permission('korraldamine', const.BT_UPDATE, obj=c.test) %>
% if c.can_update:

${h.submit()}

${h.button(_("Vali kõik"), onclick="$('input.labiviija_id').prop('checked', true);toggle_viija();", level=2)}
${h.button(_("Tühista valik"), onclick="$('input.labiviija_id').prop('checked', false);toggle_viija();", level=2)}

<span id="viija" class="invisible">
${h.btn_to_dlg(_("Saada teade"), h.url('korraldamine_new_labiviija', sub='mail',
toimumisaeg_id=c.toimumisaeg.id, partial=True), title=_("Teate saatmine"),
width=600, height=450, level=2)}
</span>
% endif

${h.end_form()}


% if c.dialog_mail:
<div id="div_dialog_mail">
  <%include file="labiviijad.mail.mako"/>
</div>
<script>
  $(function(){
    open_dialog({'contents_elem': $('#div_dialog_mail'), 'title':'${_("Teate saatmine")}'});
  });
</script>
% endif
