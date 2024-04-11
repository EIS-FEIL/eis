<%include file="translating.mako"/>

${h.form_save(c.item.id)}
${h.hidden('lang', c.lang)}
${h.hidden('is_tr', c.is_tr)}
${h.hidden('f_alatest_id', c.item.alatest_id)}
${h.rqexp()}
<div class="form-wrapper mb-3">
  % if c.item.id:
  <div class="row">
    ${h.flb3(_("Ploki jrk nr"))}
    <div class="col">
      ${c.item.seq}
    </div>
  </div>
  % endif
  <div class="row">
    ${h.flb3(_("Ploki nimetus"), rq=True)}
    <div class="col">
            % if c.lang:
              ${h.lang_orig(c.item.nimi)}<br/>
              ${h.lang_tag()}
              ${h.text('f_nimi', c.item.tran(c.lang).nimi, size=30, ronly=not c.is_tr)}
            % else:
              ${h.text('f_nimi', c.item.nimi, size=30, ronly=not c.is_tr and not c.is_edit)}
            % endif
    </div>
  </div>
  % if c.item.id:
  <div class="row">
    ${h.flb3(_("Hindepallide suurim arv"))}
    <div class="col">${h.fstr(c.item.max_pallid)}</div>
  </div>
  <div class="row">
    ${h.flb3(_("Testi ülesannete arv"))}
    <div class="col">${c.item.ylesannete_arv}</div>
  </div>
  % endif
</div>
<div class="text-right">
  ${h.submit_dlg(clicked=True)}
  <span id="progress"></span>
</div>
${h.end_form()}
