<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Hindamiserinevusega tööd")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'otsing' %>
</%def>
<h1>${_("Hindamiserinevusega tööd")}</h1>
${h.form_search()}
<div class="gray-legend p-3">
  <div class="row filter">
    <div class="col-12 col-md-3 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Sisesta toimumisaja tähis"),'ta_tahised')}
        <div>
          ${h.text('ta_tahised', c.ta_tahised, size=15, onchange='clear_ta();this.form.submit()')}
          
          ${h.btn_search()}
          % if c.items:
          ${h.submit(_("Väljatrükk"), id='tryki', level=2)}
          ${h.submit(_("CSV"), id='csv', level=2)}
          % endif
        </div>
      </div>
    </div>
  </div>
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("või vali testsessioon"),'sessioon_id')}
        ${h.select('sessioon_id', c.sessioon_id,
        c.opt.testsessioon, empty=True, onchange='clear_ta();this.form.submit()')}</td>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("ja toimumisaeg"),'toimumisaeg_id')}
        ${h.select('toimumisaeg_id', c.toimumisaeg_id,
        c.opt_toimumisaeg, empty=True, onchange='clear_sk();this.form.submit()')}
      </div>
    </div>
    % if c.toimumisaeg_id and c.hindamiskogum_id:
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Hindamiskogum"),'hindamiskogum_id')}
        ${h.select('hindamiskogum_id', c.hindamiskogum_id,
        c.opt_hindamiskogum or [], onchange='this.form.submit()')}
      </div>
    </div>
    <div class="col-12 col-md-8 col-lg-6">
      <div class="form-group">    
        ${h.checkbox('jagamata', checked=c.jagamata, label=_("Ainult kolmandale hindajale jagamata tööd"))}
        ${h.checkbox('punktides', checked=c.punktides, label=_("Ära näita palle, vaid ainult toorpunkte"))}
      </div>
    </div>      
    % endif
  </div>
</div>
      <script>
        function clear_ta()
        {
        $('#toimumisaeg_id').val('');
        clear_sk();
        }
        function clear_sk()
        {
        $('#hindamiskogum_id').val('');
        }
      </script>
${h.end_form()}

<div class="listdiv">
<%include file="hindamiserinevused_list.mako"/>
</div>
