
${h.form_search(url=h.url('ylesanne_isikud', ylesanne_id=c.ylesanne_id))}
${h.rqexp(True, _("Palun sisesta vähemalt isikukood või perekonnanimi"))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4">
      <div class="form-group">
        ${h.flb(_("Isikukood"),'isikukood')}
        ${h.text('isikukood', c.isikukood)}
      </div>
    </div>
    <div class="col-12 col-md-4">
      <div class="form-group">
        ${h.flb(_("Eesnimi"),'eesnimi')}
        ${h.text('eesnimi', c.eesnimi)}
      </div>
    </div>
    <div class="col-12 col-md-4">
      <div class="form-group">
        ${h.flb(_("Perekonnanimi"),'perenimi')}
        ${h.text('perenimi', c.perenimi)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div>
        ${h.submit_dlg(_('Otsi'))}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

<%include file="/common/message.mako"/>
% if c.items:
${h.form(h.url('ylesanne_isikud', ylesanne_id=c.ylesanne_id), method='post')}
      <table border="0"  class="table table-borderless table-striped multipleselect tablesorter" id="table_isikud" width="100%">
        <thead>
          <tr>
            <th sorter="false" width="20px"></th>
            ${h.th_sort('nimi', _("Nimi"))}
            ${h.th_sort('epost', _("E-post"))}
          </tr>
        </thead>
        <tbody>
          % for rcd in c.items:
          <tr>
            <td>${h.checkbox('oigus', rcd.id, onclick="toggle_add()", title=_("Vali rida"))}</td>
            <td>${rcd.nimi}</td>
            <td>${rcd.epost or ''}</td>
          </tr>
          % endfor
        </tbody>
      </table>

      <script>
  $(function(){
     $('table#table_isikud').tablesorter();
  });
  function toggle_add()
  {
     var visible = ($('input:checked[name="oigus"]').length > 0);
     $('.add').toggleClass('invisible', !visible);
  };
      </script>

      <div class="text-right">
        <span class="add invisible">
          ${h.submit_dlg()}
        </span>
      </div>

${h.end_form()}
% endif
