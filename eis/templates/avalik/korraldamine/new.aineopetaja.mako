## Isikute otsimine ja uute kasutajarollide lisamine soorituskohale

<%include file="/common/message.mako" />
## kui otsitakse uut isikut, siis kuvame otsinguvormi

<% is_otsi = c.sub == 'roll' or request.params.get('savesub') == 'roll' %>
<ul class="nav nav-tabs" role="tablist">
  <li class="nav-item">
    <a class="nav-link ${not is_otsi and 'active' or ''}"
       id="tab_v" data-toggle="tab" href="#search_v"
       role="tab" aria-selected="${is_otsi and 'false' or 'true'}">
      ${_("Vali oma koolist")}
    </a>
  </li>
  <li class="nav-item">
    <a class="nav-link ${is_otsi and 'active' or ''}"
       id="tab_v" data-toggle="tab" href="#search_i"
       role="tab" aria-selected="${is_otsi and 'true' or 'false'}">
      ${_("Otsi")}
    </a>
  </li>
</ul>
<div class="tab-content">
  <div id="search_v" class="tab-pane fade ${not is_otsi and 'show active' or ''}">
    ${self.search_v()}
  </div>
  <div id="search_i" class="tab-pane fade ${is_otsi and 'show active' or ''}">
    ${self.search_i()}
  </div>
</div>

<%def name="search_v()">
${h.form(url=h.url('korraldamine_aineopetajad', testikoht_id=c.testikoht.id), method='post')}
${h.hidden('sub', 'rollped')}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-8">
      <div class="form-group">
        ${h.flb(_("Õpetaja"),'pedagoog_id')}
        ${h.select2('pedagoog_id', c.pedagoog_id, c.opt_pedagoogid, multiple=True)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div>
        ${h.submit_dlg(container="$('div#dialog_div .modal-body')")}
      </div>
    </div>
  </div>
</div>
${h.end_form()}
</%def>

<%def name="search_i()">
${h.form_search(url=h.url('korraldamine_aineopetajaisikud', testikoht_id=c.testikoht.id))}
${h.hidden('savesub', 'roll')}
${h.hidden('partial','true')}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-8">
      <div class="form-group">
        ${h.flb(_("Isikukood"),'isikukood')}
        ${h.text('isikukood', c.isikukood)}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div>
      ${h.button(_("Otsi"), onclick="var url='%s?'+$(this.form).serialize();dialog_load(url);" % h.url('korraldamine_aineopetajaisikud', testikoht_id=c.testikoht.id))}
      </div>
    </div>
  </div>
</div>
${h.end_form()}

% if c.items != '' and not c.items:
${_("Otsingu tingimustele vastavaid isikuid ei leitud")}
% elif c.items:
${h.form(h.url('korraldamine_aineopetajad', testikoht_id=c.testikoht.id))}
${h.hidden('sub', 'roll')}
      <table border="0"  class="table table-borderless table-striped multipleselect tablesorter" id="table_isikud" width="100%">
        <thead>
          <tr>
            <th></th>
            ${h.th_sort('isikukood', _("Isikukood"))}
            ${h.th_sort('nimi', _("Nimi"))}
            <th></th>
          </tr>
        </thead>
        <tbody>
          % for rcd in c.items:
          <tr>
            <td>${h.checkbox('oigus', rcd.id, onclick="toggle_add()", class_="oigus")}
            </td>
            <td>${rcd.isikukood}</td>
            <td>${rcd.nimi}</td>
            <td>${rcd.epost or ''}</td>
          </tr>
          % endfor
        </tbody>
      </table>

<script>
  $(document).ready(function(){
     $('table#table_isikud').tablesorter();
  });
  function toggle_add()
  {
         var visible = ($('input:checked.oigus').length > 0);
         $('#add').toggleClass('invisible', !visible);
  };
</script>

${h.hidden('kasutajagrupp_id', const.GRUPP_AINEOPETAJA)}
${h.hidden('kehtib_kuni', '')}

<div id="add" class="invisible text-right">
  ${h.submit(_("Salvesta"), id='add_isik')}
</div>

${h.end_form()}

% endif
</%def>
