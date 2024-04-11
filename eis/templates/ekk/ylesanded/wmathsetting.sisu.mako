<div class="form-group row">
  <div class="col">
    ${h.checkbox('removeLinks', 1, checked=c.removeLinks, label=_("Nupuriba ilma linkideta"))}
    ${h.checkbox('detectHand', 1, checked=c.detectHand, label=_("Vabakäega kirjutamine"))}
  </div>
</div>

<div class="form-group row">
  ${h.flb3(_("Nupuriba"), 'toolbar')}
  <div class="col-md-9">
    <% opt_toolbar = (('', _("Isetehtud nupuriba")), "general", "quizzes", "chemistry", "evaluate", "PARCC_Grade3_5", "PARCC_Grade6_8", "PARCC_Grade9_12") %>
    ${h.select('toolbar', c.toolbar, opt_toolbar)}
  </div>
</div>

<div class="form-group row custom-toolbar">
  ${h.flb3(_("Ridade arv"), 'rows')}
  <div class="col-md-9 fh">
    ${h.select('rows', c.rows, (1,2), wide=False)}
  </div>
</div>

<div class="accordion" id="accordionWM">
% for iconset in c.opt_iconsets:
<% toolbar, tabname, tabtitle, icons = iconset %>
  <div class="accordion-card card parent-accordion-card card-tab-${toolbar}">
    <div class="card-header" id="headingWM_${tabname}">
      <div class="accordion-title">
        <button
          class="btn btn-link collapsed"
          type="button"
          data-toggle="collapse"
          data-target="#collapseWM_${tabname}"
          aria-expanded="true"
          aria-controls="collapseWM_${tabname}"
        >
          <span class="btn-label">
            <i class="mdi mdi-chevron-down"></i>
            % if toolbar == 'general':
            <span class="std-toolbar">${h.checkbox('tab', tabname, checkedif=c.tabs)}</span>
            % endif
            ${tabtitle}
          </span>
          ##<span class="accordion-note">05.11.2019<br />11:28 </span>
        </button>
      </div>
    </div>

    <div id="collapseWM_${tabname}" class="collapse" aria-labelledby="headingWM_${tabname}">
      <div class="card-body">
        <div class="content">
          % for iconid, icontitle in icons:
          <% if iconid[0] == '&': icontitle += ' ' + iconid %>
          ${h.checkbox('icon', f'{tabname}:{iconid}', checkedif=c.icons, label=icontitle)}
          % endfor
        </div>
      </div>
    </div>
  </div>
% endfor
</div>


<script>
function toggle(){
  var tb = $('#toolbar').val();
  if(tb){
    $('.custom-toolbar').hide();
    $('.std-toolbar').show();
    $('#accordionWM .card').hide();
    if(tb.startsWith('PARCC')) tb = 'PARCC';
    $('#accordionWM .card-tab-'+tb).show();
  } else {
    $('.custom-toolbar').show();
    $('.std-toolbar').hide();
    $('#accordionWM .card').show();
  }
}
function show_default(){
  var tb = $('#toolbar').val();
  if(tb){
    $('#accordionWM .card:not(:visible) input[name="tab"]').prop('checked', false);
    $('#accordionWM .card:not(:visible) input[name="icon"]').prop('checked', false);
    $('#accordionWM .card:visible input[name="tab"]').prop('checked', true);
    $('#accordionWM .card:visible input[name="icon"]').prop('checked', true);  
  } else {
    $('#accordionWM .card input[name="tab"]').prop('checked', false);  
    $('#accordionWM input[name="icon"]').prop('checked', false);
  }
}
$('#toolbar').change(function(){
   toggle();
   show_default();
});
$(toggle);
  
</script>
