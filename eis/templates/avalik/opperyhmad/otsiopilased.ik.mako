<%include file="/common/message.mako"/>
${h.form_search(url=h.url_current('index', opperyhm_id=c.opperyhm.id))}
${h.hidden('sub', 'ik')}
<div class="gray-legend p-3">
  <div class="row filter">
    <div class="col-md-6">
      ${h.flb(_("Isikukood"),'isikukood')}
      ${h.text('isikukood', c.isikukood)}
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      ${h.submit_dlg(_('Otsi'))}
    </div>
  </div>
</div>

${h.end_form()}

<span id="progress"></span>
<%include file="/common/message.mako"/>
% if c.items:
${h.form(h.url_current('create', opperyhm_id=c.opperyhm.id), method='post')}
      <table border="0" class="table table-borderless table-striped" id="table_isikud" width="100%">
        <thead>
          <tr>
            ${h.th_sort('isikukood', 'Isikukood')}
            ${h.th_sort('eesnimi,perenimi', 'Nimi')}
          </tr>
        </thead>
        <tbody>
          % for rcd in c.items:
          <tr>
            <td>${rcd.isikukood}</td>
            <td>
              ${rcd.eesnimi} ${rcd.perenimi}
              ${h.hidden('oigus', rcd.isikukood)}
            </td>
          </tr>
          % endfor
        </tbody>
      </table>

<p>
<span id="add">
  ${h.submit(_('Salvesta'), id='add_isik')}
</span>
</p>

${h.end_form()}

% endif
