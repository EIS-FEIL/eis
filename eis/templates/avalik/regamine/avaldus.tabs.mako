<%namespace name="tab" file='/common/tab.mako'/>
## formpage-body on selleks, et being_clicked_args ei annaks klikkimisel lahkumise hoiatust 
<div class="formpage-body d-flex">
<%
  try:
      step = ('testivalik','isikuandmed','kinnitamine').index(c.tab1)
  except ValueError:
      step = 0
%>
% if c.testiliik:
${tab.draw('testivalik', h.url('regamine_avaldus_testid_testiliik', testiliik=c.testiliik), _('Testi valik'), c.tab1)}
% else:
${tab.draw('testivalik', h.url_current(), _('Testi valik'), c.tab1)}
% endif

${tab.draw('isikuandmed', h.url('regamine_avaldus_isikuandmed', testiliik=c.testiliik),
_('Andmed'), c.tab1, disabled=step < 1 and 'notcurrent')}
${tab.draw('kinnitamine', h.url('regamine_avaldus_kinnitamine', testiliik=c.testiliik),
_('Kinnitamine'), c.tab1, disabled=step < 2 and 'notcurrent')}
</div>
