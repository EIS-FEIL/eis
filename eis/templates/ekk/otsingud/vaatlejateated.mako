<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Vaatlejatele teadete väljastamine")}
</%def>      
<%def name="breadcrumbs()">
</%def>
<%def name="active_menu()">
<% c.menu1 = 'otsing' %>
</%def>
<h1>${_("Vaatlejatele teadete väljastamine")}</h1>

${h.form_search(url=h.url('otsing_vaatlejateated'))}
${h.hidden('op','')}
<div class="gray-legend p-3 filter-w">
  ##${h.toggle_filter()}
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Testsessioon"),'sessioon_id')}
        ${h.select('sessioon_id', c.sessioon_id,
        c.opt_sessioon, empty=True)}
            <script>
              $(document).ready(function(){
              $('select#sessioon_id').change(
              callback_select("${h.url('pub_formatted_valikud', kood='TOIMUMISAEG', format='json')}", 
              'sessioon_id', $('select#toimumisaeg_id'))
              );
              });
            </script>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Toimumisaeg"),'toimumisaeg_id')}
        ${h.select('toimumisaeg_id', c.toimumisaeg_id,
        c.opt_toimumisaeg, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Piirkond"),'piirkond_id')}
            <%
               c.piirkond_id = c.piirkond_id
               c.piirkond_field = 'piirkond_id'
               # c.piirkond_filtered on seatud handleris
            %>
            <%include file="/admin/piirkonnavalik.mako"/>
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
          ${h.flb(_("Isikukood"),'isikukood')}
          ${h.text('isikukood', c.isikukood, maxlength=50)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Eesnimi"),'eesnimi')}
        ${h.text('eesnimi', c.eesnimi)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Perekonnanimi"),'perenimi')}
        ${h.text('perenimi', c.perenimi)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("Koolitusaeg alates"),'koolitusaeg_alates')}
        ${h.date_field('koolitusaeg_alates', c.koolitusaeg_alates)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.flb(_("kuni"),'koolitusaeg_kuni')}
        ${h.date_field('koolitusaeg_kuni', c.koolitusaeg_kuni)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
            ${h.radio(u'ltyyp', model.Kiri.TYYP_LABIVIIJA_TEADE, 
            checked=c.ltyyp==model.Kiri.TYYP_LABIVIIJA_TEADE or not c.ltyyp, 
            disabled=c.piirkond_filtered,
            label=_("Vaatluskoha teade"))}
            <br/>
            ${h.radio(u'ltyyp', model.Kiri.TYYP_LABIVIIJA_MEELDE, 
            checkedif=c.ltyyp, label=_("Vaatluskoha meeldetuletus"))}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">    
        ${h.checkbox(u'kordus', 1, checked=c.kordus, label=_("Saada ka kordusteateid"))}
      </div>
    </div>
  </div>
  <div class="d-flex justify-content-end align-items-end">
    <div class="form-group">
    ${h.submit(_("Kontrolli teadete arvu"))}
    </div>
  </div>
</div>

% if c.arv != '':
<div class="data-box mb-5">
  <div class="form-group row">
    ${h.flb3(_("Täiendav info (lisatakse teatele)"), 'taiendavinfo')}
    <div class="col-md-9">
      ${h.textarea('taiendavinfo', c.taiendavinfo)}
    </div>
  </div>

  <div class="row">
    <div class="column col-md-2 fh">
      ${_("Teateid")}
    </div>
    <div class="column col-md-1">
      ${c.arv}
    </div>
    <div class="column col-md-9">
      % if c.arv:
      ${h.button(_("Väljasta e-postiga"), onclick="$('#op').val('epost');submit_post(this)", level=2)}
      ${h.button(_("Väljasta väljatrükid"), onclick="$('#op').val('tpost');submit_post(this)", level=2)}
      % endif
    </div>
  </div>
</div>
% endif
${h.end_form()}

<% 
  c.protsessid_no_empty = True
  c.url_refresh = h.url_current('index', sessioon_id=c.sessioon_id, sub='progress')
%>
<%include file="/common/arvutusprotsessid.mako"/>

