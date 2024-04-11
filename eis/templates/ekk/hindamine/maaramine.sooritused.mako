<%inherit file="/common/formpage.mako"/>
<%def name="require()">
<% c.includes['subtabs'] = True %>
</%def>
<%def name="page_title()">
${_("Hinnatavad sooritused")} | ${c.hindaja.kasutaja.nimi}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Hindamine"), h.url('hindamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, c.toimumisaeg.millal))} 
${h.crumb(_("Läbiviijate määramine"), h.url('hindamine_hindajad', toimumisaeg_id=c.toimumisaeg.id))}
% if c.hindaja.liik == const.HINDAJA3:
${h.crumb(_("III hindamine"), h.url('hindamine_hindajad3', toimumisaeg_id=c.toimumisaeg.id))}
% else:
${h.crumb(_("Esmane (I ja II) hindamine"), h.url('hindamine_hindajad', toimumisaeg_id=c.toimumisaeg.id))}
% endif
${h.crumb(c.hindaja.kasutaja.nimi)}
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
<%
  c.tab2 = c.hindaja.liik == const.HINDAJA3 and 'hindajad3' or 'hindajad'
%>
<%include file="maaramine.tabs.mako"/>
</%def>

<h3>
  <% hk = c.hindaja.hindamiskogum %>
  % if hk:
  ${_("Hindaja {s1} ({s2}) poolt hinnatavad testisooritused hindamiskogumis {s3}").format(s1=c.hindaja.kasutaja.nimi, s2=c.hindaja.tahis, s3=hk.tahis)}
  % else:
  ## suulises p-testis pole hindamiskogumit
  ${_("Hindaja {s1} ({s2}) poolt hinnatavad testisooritused").format(s1=c.hindaja.kasutaja.nimi, s2=c.hindaja.tahis)}  
  % endif
</h3>

${h.form_search(url=h.url('hindamine_sooritused', toimumisaeg_id=c.toimumisaeg.id, hindaja_id=c.hindaja.id))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    ${h.flb3(_("Hindamise olek"),'staatus')}
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
            <%
               staatused = [const.H_STAATUS_POOLELI, const.H_STAATUS_SUUNATUD, const.H_STAATUS_LYKATUD, const.H_STAATUS_HINNATUD]
               opt_staatused = [(st, c.opt.H_STAATUS.get(st)) for st in staatused]
            %>
            ${h.select('staatus', c.staatus, opt_staatused, empty=True)}
      </div>
    </div>
    <div class="col">
      <div class="form-group">
        ${h.btn_search()}
      </div>
    </div>
  </div>
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Hinnatud"), 'hinnatud')}
        <span class="brown" id="hinnatud">${c.hindaja.hinnatud_toode_arv or 0}</span>
      </div>
    </div>
    <div class="col">
      <div class="form-group">
        ${h.submit(_("Arvuta üle"), id='arvutauuesti', level=2)}
        % if not c.hindaja.testiruum_id:
        ## hindaja eelvaadet pole kooli määratud suulisel hindajal
        ## (avalikus vaates kuvatakse hindajale tema ruumi sooritajate nimekiri, kust valib, keda hinnata)
        ${h.btn_to(_("Hindaja eelvaade"),
        h.url('hindamine_hindajavaade_vastajad', toimumisaeg_id=c.toimumisaeg.id, hindaja_id=c.hindaja.id), level=2)}
        % endif
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<div class="listdiv">
<%include file="maaramine.sooritused_list.mako"/>
</div>
<br/>

% if c.hindaja.liik == const.HINDAJA3:
${h.btn_to(_("Lisa hindamised"), h.url('hindamine_sooritused',
toimumisaeg_id=c.toimumisaeg.id, hindaja_id=c.hindaja.id), method='post', level=2, mdicls='mdi-plus')}

% if c.toimumisaeg.testiosa.vastvorm_kood == const.VASTVORM_KP:
${h.btn_to(_("Väljasta hindamisprotokollid"), h.url('hindamine_sooritused', sub='protokoll',
toimumisaeg_id=c.toimumisaeg.id, hindaja_id=c.hindaja.id), method='get', level=2)}
% endif
% endif
