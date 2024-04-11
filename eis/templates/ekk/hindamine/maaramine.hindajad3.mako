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
${h.crumb(_("Kolmas hindamine"))}
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

${h.form_search(url=h.url('hindamine_hindajad3', toimumisaeg_id=c.toimumisaeg.id))}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}

  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Hindamiskogum"),'hindamiskogum_id')}
        ${h.select('hindamiskogum_id', c.hindamiskogum_id, c.hindamiskogumid_opt, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Hindaja"),'hindaja_id')}
        ${h.select('hindaja_id', c.hindaja_id, c.hindajad_opt, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Soorituskeel"),'lang')}
        ${h.select('lang', c.lang, c.testimiskord.opt_keeled, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Soorituspiirkond"),'piirkond_id')}
        ${h.select('piirkond_id', c.piirkond_id, model.Piirkond.get_opt_prk(None), empty=True)}
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
% if c.esmanekokku is not None:
            <script>
              $('select#hindamiskogum_id,select#lang,select#piirkond_id').change(function(){
                $('span.kolmaspro').hide();
              });
            </script>
            <span class="kolmaspro">
              % if c.kolmasprotsent is None:
              ${_("Esmaselt hinnatud {n} tööd").format(n='<span class="brown">%s</span>' % c.esmanekokku)}
              % else:
              ${_("Täiendava hindamise tööde protsent")}
              <span class="brown">${h.fstr(c.kolmasprotsent)}%</span>
                % if not c.toimumisaeg.tulemus_kinnitatud:
                ${h.btn_to_dlg(_("Vali juhuslikult"),
                h.url('hindamine_new_kolmandaks', toimumisaeg_id=c.toimumisaeg.id,
                hindamiskogum_id=c.hindamiskogum_id, lang=c.lang, piirkond_id=c.piirkond_id),
                title=_("Vali juhuslikult"), width=400, level=2)}
                % endif
              % endif
            </span>
% endif          
${h.end_form()}

<div class="listdiv">
<%include file="maaramine.hindajad_list.mako"/>
</div>

${h.btn_to_dlg(_("Lisa III hindaja"), h.url('hindamine_new_hindaja3',
toimumisaeg_id=c.toimumisaeg.id, partial=True),
title=_("III hindaja lisamine"), width=650, level=2, mdicls='mdi-plus')}

% if c.testimiskord.sisaldab_valimit:
${h.btn_to_dlg(_("Lisa valimi III hindaja"), h.url('hindamine_new_hindaja3',
toimumisaeg_id=c.toimumisaeg.id, valimis=1, partial=True),
title=_("Valimi III hindaja lisamine"), width=650, level=2, mdicls='mdi-plus')}
% endif
