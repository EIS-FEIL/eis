## -*- coding: utf-8 -*- 
<% 
   testiruum = c.toimumisprotokoll.testiruum
   c.test = c.toimumisprotokoll.testimiskord.test
%>
<h1>${_("Testi toimumise protokoll")}</h1>

<div class="gray-legend d-flex p-3 my-2">
  <div class="item mr-5">
    ${h.flb(_("Test"),'test_nimi')}
    <div id="test_nimi">
      ${c.test.nimi}
    </div>
  </div>
  <div class="item mr-5">
    ${h.flb(_("Toimumisaeg"),'kohad_alates')}
    <div id="kohad_alates">
      % for testikoht in c.toimumisprotokoll.testikohad:
      ${h.str_from_date(testikoht.alates)}
      % endfor
    </div>
  </div>
  <div class="item mr-5">
    ${h.flb(_("Testikoht"),'koht_nimi')}
    <div id="koht_nimi">
      ${c.toimumisprotokoll.koht.nimi}
      % if testiruum:
      <% ruum = testiruum.ruum %>
      % if ruum:
      ${_("ruum")} ${testiruum.ruum.tahis}
      % endif
      % endif
    </div>
  </div>
  <div class="item mr-5">
    ${h.flb(_("Protokoll"),'protokoll_tahistus')}
    <div id="protokoll_tahistus">
      ${c.toimumisprotokoll.tahistus}
    </div>
  </div>
</div>

