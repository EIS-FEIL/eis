<% 
   c.testikoht = c.protokoll.testipakett.testikoht
   c.toimumisaeg = c.testikoht.toimumisaeg
   c.testimiskord = c.toimumisaeg.testimiskord
   c.test = c.testimiskord.test
   c.testiruum = c.protokoll.testiruum
%>
<div class="question-status d-flex flex-wrap justify-content-between mb-2 bg-gray-50">
  <div class="item mr-5">
    ${h.flb(_("Test"))}
    <div>
      ${c.test.nimi}
      ${c.toimumisaeg.tahised}
    </div>
  </div>
  <div class="item mr-5">
    ${h.flb(_("Toimumise aeg"))}
    <div>
      ${h.str_from_date(c.testiruum.algus)}
    </div>
  </div>
  % if c.hindamise_liik:
  <div class="item mr-5">
    ${h.flb(_("Hindamise liik"))}
    <div>${c.hindamise_liik}</div>
  </div>
  % endif
  % if c.solek:
  <div class="item mr-5">
    ${h.flb(_("Sisestuskogum"))}
    <div>
      ${model.Sisestuskogum.get(c.solek.sisestuskogum_id).tahis}
    </div>
  </div>
  % endif
  <div class="item mr-5">
    ${h.flb(_("Soorituskoht"))}
    <div>
      ${c.testikoht.tahised}
      % if c.testimiskord.sisestus_isikukoodiga:
        % if c.testiruum.ruum and c.testiruum.ruum.tahis:
        ${c.testikoht.koht.nimi}, ruum ${c.testiruum.ruum.tahis}
        % else:
        ${c.testikoht.koht.nimi}
        % endif
      % endif
    </div>
  </div>
  % if c.hindamisprotokoll:
  <div class="item mr-5">
    ${h.flb(_("Hindamisprotokoll"))}
    <div>
      ${c.hindamisprotokoll.get_short_tahised()}
      <!--hpr${c.hindamisprotokoll.id} tpr${c.hindamisprotokoll.testiprotokoll_id}-->
    </div>
  </div>
  % else:
  <div class="item mr-5">
    ${h.flb(_("Protokollirühm"))}
    <div>
      ${c.protokoll.tahis}<!--tpr${c.protokoll.id}-->
    </div>
  </div>
  % endif

  % if str(c.sisestus) == '1':
  <div class="item mr-5">
    ${h.flb(_("Sisestus"))}
    <div>
      1 
      % if c.hindamisprotokoll:
      (${c.hindamisprotokoll.staatus1_nimi})
      % endif
      % if c.solek:
      (${c.solek.staatus1_nimi})
      % endif
    </div>
  </div>
  % elif str(c.sisestus) == '2':
  <div class="item mr-5">
    ${h.flb(_("Sisestus"))}
    <div>2 
      % if c.hindamisprotokoll:
      (${c.hindamisprotokoll.staatus2_nimi})
      % endif
      % if c.solek:
      (${c.solek.staatus2_nimi})
      % endif
    </div>
  </div>
  % elif c.sisestus == 'p':
  <div class="item mr-5">
    ${h.flb(_("Sisestuste parandamine"))}
    <div>
      % if c.hindamisprotokoll:
      (${c.hindamisprotokoll.staatus_nimi})
      % endif
      % if c.solek:
      (${c.solek.staatus_nimi})
      % endif
    </div>
  </div>
  % endif
</div>
