<% sooritaja = c.sooritus.sooritaja %>
<div class="question-status d-flex flex-wrap mb-3">
  <div class="item mr-5">
    ${h.flb(_("Sooritaja kood"))}
    <h1>
      % if c.is_debug or c.is_devel:
      <a href="${h.url('otsing_testisooritus', id=sooritaja.id)}">${c.sooritus.tahised}</a>
      % else:
      ${c.sooritus.tahised}
      % endif
    </h1><!--${c.sooritus.id}-->
  </div>
  <div class="item mr-5">
    ${h.flb(_("Soorituskeel"))}
    <br/>
    ${model.Klrida.get_lang_nimi(sooritaja.lang)}
  </div>

  % if c.test.on_kursused:
  <div class="item mr-5">
    ${h.flb(_("Kursus"))}
    <br/>
    ${sooritaja.kursus_nimi}
  </div>
  % endif
    
  % if c.hindamiskogum:
  <div class="item mr-5">
    ${h.flb(_("Hindamiskogum"))}
    <br/>
    ${c.hindamiskogum.tahis}
  </div>
  <div class="item mr-5">
    ${h.link_to(_("Hindamiskogumid"), h.url('hindamine_ekspert_kogum',
    toimumisaeg_id=c.toimumisaeg.id, id=c.sooritus.id))}
  </div>
  <div class="item mr-5">
    ${h.flb(_("Ülesandekomplekt"))}
    <br/>
    <% holek = c.sooritus.get_hindamisolek(c.hindamiskogum) %>
    ${holek and holek.komplekt and holek.komplekt.tahis}
  </div>
  % endif

  <% erivajadused = c.sooritus.get_str_erivajadused() %>
  % if erivajadused:
  <div class="item mr-5">
    ${h.flb(_("Eritingimused"))}
    <br/>
    ${erivajadused}
  </div>
  % endif

</div>
