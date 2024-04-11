<div class="question-status d-flex mb-3">
  <div class="item mr-5">
    ${_("Õppeasutus")}
    <b>${c.user.koht_nimi}</b>
  </div>

  % if c.testimiskord:
  <div class="item mr-5">
    ${_("Test")}
    <b>
      ${c.test.nimi}
    </b>
  </div>
  <div class="item mr-5">
    ${_("Testimiskord")}
    <b>${c.testimiskord.tahised}</b>
  </div>
  % else:
  <div class="item mr-5">
    ${_("Test")}
    <b>
      % if c.user.has_permission('testid', const.BT_SHOW, c.test):
      ${h.link_to(c.test.nimi, h.url('test', id=c.test.id))}
      % else:
      ${c.test.nimi}
      % endif
    </b>
  </div>
  % endif

  <% eeltest = c.test.eeltest %>
  % if eeltest:
  <div class="item mr-5">
    ${_("Eeltestimisel alates")}
    <b>${h.str_from_date(c.test.avalik_alates)}</b>
  </div>
  <div class="item mr-5">
    ${_("Eeltestimisel kuni")}
    <b>${h.str_from_date(c.test.avalik_kuni)}</b>
  </div>
  % endif
</div>

% if eeltest and eeltest.markus_korraldajatele:
<div class="row">
  ${h.flb3(_("Koostaja märkus"), 'kmarkus', 'text-right')}
  <div class="col-md-9" id="kmarkus">
      ${eeltest.markus_korraldajatele or ''}
  </div>
</div>
% endif

