<%include file="/common/message.mako"/>
${h.form_search(url=h.url('test_nimekiri_otsisooritajad', test_id=c.test_id, nimekiri_id=c.nimekiri_id))}
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
% if c.items:
${h.form(h.url('test_nimekiri_sooritajad', test_id=c.test_id, nimekiri_id=c.nimekiri_id), method='post')}
      <table border="0" class="table table-borderless table-striped" id="table_isikud" width="100%">

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
              ${h.hidden('k_id', rcd.id)}
</div>
% endfor

<div id="add">
  <div class="d-flex flex-wrap my-3 p-2">
    <% opt_keeled = c.testimiskord and c.testimiskord.opt_keeled or c.test.opt_keeled %>
    % if len(opt_keeled) > 0:
    <div class="mr-4">
    ${_("Soorituskeel:")}
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
    ${_("Kursus:")}  ${h.select('kursus', None, opt_kursused, wide=False)}    
    </div>
    % endif
    
    % if c.test.testiliik_kood in (const.TESTILIIK_KOOLIPSYH, const.TESTILIIK_LOGOPEED):
    <div class="mr-4">
    ${h.checkbox('vanem_nous', 1, label=_('Vanema nõusolek'))}
    </div>
    % endif
  </div>
  <div class="text-right">
    ${h.submit(_('Salvesta'), id='add_isik')}
  </div>
</div>

${h.end_form()}

% endif
