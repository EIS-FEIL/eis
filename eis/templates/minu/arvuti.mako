<%inherit file="/common/pagenw.mako"/>
<%def name="page_title()">
${_("Arvuti registreerimine")}
</%def>      
<% c.is_edit = True %>
${h.form(h.url('arvuti'))}    

<h1 class="mb-5">${_("Arvuti registreerimine")}</h1>
    ${h.form(h.url('arvuti'))}
    <div class="row filter">
      <div class="col-12 col-md-4 col-lg-3">
        <div class="form-group">
          <label class="font-weight-bold" for="parool">
            ${_("Testiruumi parool")}
          </label>
          ${h.password('parool', style="width:100%", ronly=False, autocomplete='off')}
        </div>
      </div>
    </div>
    <div class="d-flex justify-content-right">
      ${h.submit(_("Registreeri"), clicked=1000)}
    </div>
    ${h.end_form()}

    <% testiarvutid = model.Testiarvuti.get_reg(request) %>
    % if testiarvutid:
    <table class="table my-3">
      <thead>
        <th>${_("Arvuti registreeringu ruum")}</th>
        <th>${_("Kehtivus")}</th>
        <th>${_("Aegub")}</th>
      </thead>
      <tbody>
        % for arvuti in testiarvutid:
        <tr>
          <td>${arvuti.info()}</td>
          <td>
            % if arvuti.staatus==const.B_STAATUS_KEHTIV:
            ${_("Kehtiv")}
            % else:
            ${_("Kehtetu")}
            % endif
          </td>
          <td>${h.str_from_datetime(arvuti.kehtib_kuni)}</td>
        </tr>
        % endfor
      </tbody>
    </table>
    % endif
