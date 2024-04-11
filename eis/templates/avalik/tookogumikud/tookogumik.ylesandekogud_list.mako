<%include file="/common/message.mako"/>
% if c.items != '':
% if not c.items:
${_("Otsingu tingimustele vastavaid e-kogusid ei leitud")}
% else:
<div class="d-flex justify-content-end mb-2">
  ${h.button(_("Lisa töökogumikku"), class_="add_y", disabled=True, level=2)}
</div>
${h.pager(c.items,
          msg_not_found=_("Otsingu tingimustele vastavaid e-kogusid ei leitud"),
          msg_found_one=_("Leiti üks tingimustele vastav e-kogu"),
          msg_found_many=_("Leiti {n} tingimustele vastavat e-kogu"),
          listdiv='#listdiv_yk',
          form='#yk_search',
          newline=True)}

<div class="accordion" id="accordion_yk">
% for rcd in c.items:
<div class="d-flex align-items-start accordion-outer-wrapper yk-item">
  <% itemid = 'yk-%d' % rcd.id %>
  ${h.checkbox('v', itemid, label='', class_="v-yk", nohelp=True, disabled=True)}
  <div class="accordion-card card parent-accordion-card yk-all" id="ykcard_${rcd.id}">
    <div class="card-header" id="ch_yk_${rcd.id}">
      <div class="accordion-title">
        <button class="btn btn-link collapsed open-yk"
                type="button"
                style="white-space:normal"
                data-toggle="collapse"
                data-target="#collapse_yk_${rcd.id}"
                data-parent="#accordion_yk"
                aria-expanded="true"
                aria-controls="collapse_yk_${rcd.id}"
                href="${h.url('tookogumik_ylesandekogu', id=rcd.id)}"
                >
          <span class="btn-label">
            <i class="mdi mdi-chevron-down"></i>
            ${rcd.nimi}
          </span>
        </button>
      </div>
    </div>
    <div id="collapse_yk_${rcd.id}" class="collapse" aria-labelledby="ch_yk_${rcd.id}">
    </div>
  </div>
</div>
% endfor
</div>
% endif
% endif


