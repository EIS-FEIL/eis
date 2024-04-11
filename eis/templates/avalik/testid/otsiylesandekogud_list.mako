% if c.items != '':
% if not c.items:
${_("Otsingu tingimustele vastavaid e-kogusid ei leitud")}
% else:
% for rcd in c.items:
<div class="yk">
  <div class="yk-title" href="${h.url('test_otsiylesandekogu', test_id=c.test.id, testiruum_id=c.testiruum_id, id=rcd.id)}">
    <span class="glyphicon glyphicon-folder-close"> </span>
    ${rcd.nimi}
  </div>
  <div class="yk-items"></div>
</div>
% endfor
<span id="add" class="invisible">
${h.submit(_('Salvesta'))}
</span>
% endif
% endif

