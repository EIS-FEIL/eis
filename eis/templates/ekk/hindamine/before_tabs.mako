<% 
c.testimiskord = c.toimumisaeg.testimiskord
c.test = c.testimiskord.test
c.testiosa = c.toimumisaeg.testiosa
%>
<div class="data-box mb-5">
  <div class="row">
    <div class="column col-12 col-md-2 fh">
      ${_("Test")}
    </div>
    <div class="column col-12 col-md-6">
      % if c.user.has_permission('testimiskorrad', const.BT_SHOW, test_id=c.test.id):
      ${h.link_to2(c.test.nimi, h.url('test_kord_toimumisaeg', test_id=c.test.id,
      kord_id=c.testimiskord.id, id=c.toimumisaeg.id))}
      % else:
      ${c.test.nimi}
      % endif
      ${c.toimumisaeg.tahised}
      ${c.test.aine_nimi}
    </div>
    <div class="column col-12 col-md-4">
      % if c.user.has_permission('testimiskorrad', const.BT_SHOW, test_id=c.test.id):      
      ${h.link_to2(_("Korraldamine"), h.url('korraldamine_soorituskohad',
      toimumisaeg_id=c.toimumisaeg.id))}
      % endif
    </div>
  </div>
  <div class="row">
    <div class="column col-12 col-md-2 fh">
      ${_("Toimumise aeg")}
    </div>
    <div class="column col-12 col-md-4">
      ${c.toimumisaeg.millal}
    </div>
    <div class="column col-12 col-md-2 fh">
      ${_("Vastamise vorm")}
    </div>
    <div class="column col-12 col-md-4">
      ${c.testiosa.vastvorm_nimi}
    </div>
  </div>
  <div class="row">    
    <div class="column col-12 col-md-2 fh">
      ${_("Soorituskeeled")}
    </div>
    <div class="column col-12 col-md-4">
      ${', '.join([model.Klrida.get_lang_nimi(lang) for lang in c.testimiskord.get_keeled()])}
    </div>
  </div>
  % if c.testikoht:
  <div class="row">
    <div class="column col-12 col-md-2 fh">
      ${_("Soorituskoht")}
    </div>
    <div class="column col-12 col-md-10">
      ${c.testikoht.koht.nimi}
    </div>
  </div>
  % endif
</div>

