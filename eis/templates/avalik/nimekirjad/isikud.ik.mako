${h.not_top()}
${h.form_search(url=h.url('nimekiri_isikud', testimiskord_id=c.testimiskord_id))}
${h.hidden('sub', 'ik')}

<div class="gray-legend p-3">
  <div class="row filter">
    <div class="col-md-4">
      ${h.flb(_("Isikukood"),'isikukood')}
      % if c.kasutaja:
      ${h.text('isikukood', c.kasutaja.isikukood)}
      % else:
      ${h.text('isikukood', c.isikukood)}
      % endif
    </div>
    <div class="col-md-4 d-flex justify-content-end align-items-end">
      <div>
        ${h.submit_dlg(_("Otsi"))}
      </div>
    </div>
  </div>
</div>

${h.end_form()}
<span id="progress"></span>
<%include file="/common/message.mako"/>
% if c.items:
${h.form(h.url('nimekiri_sooritajad', testimiskord_id=c.testimiskord_id), method='post')}

% for rcd in c.items:
<div class="p-2">
  <%
  ## rcd on opilane või kasutaja või NewItem(isikukood,eesnimi,perenimi)
  if not c.keel and isinstance(rcd,model.Opilane):
     c.keel = rcd.lang 
  %>
              ${rcd.eesnimi} ${rcd.perenimi}
              % if rcd.isikukood:
              (${rcd.isikukood})
              % else:
              (${h.str_from_date(rcd.synnikpv)})
              % endif
              ${h.hidden('ik', rcd.isikukood)}
</div>
% endfor

<div id="add" class="p-2">
  <div class="d-flex flex-wrap my-3 p-2">
    <% opt_keeled = c.testimiskord and c.testimiskord.opt_keeled or c.test.opt_keeled %>
    % if len(opt_keeled) > 0:
    <div class="mr-4">
    ${_("Soorituskeel")}:
      % if len(opt_keeled) > 1:
      ${h.select('keel', c.keel, opt_keeled, wide=False)}    
      % else:
      ${opt_keeled[0][1]}
      ${h.hidden('keel', opt_keeled[0][0])}
    % endif
    </div>
    % endif

    <% opt_kursused = c.test.opt_kursused %>
    % if len(opt_kursused):
    <div class="mr-4">
      ${_("Kursus")}:  ${h.select('kursus', None, opt_kursused, wide=False)}
    </div>
    % endif
  </div>
  <div class="text-right">
    ${h.submit(_("Salvesta"), id='add_isik', clicked=True)}
  </div>
</div>
${h.end_form()}

% endif
