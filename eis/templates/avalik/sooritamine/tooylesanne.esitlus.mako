<%inherit file="/avalik/lahendamine/esitlus.mako"/>

<%def name="gen_submit_url()">
<% c.submit_url = h.url_current('updatetask', yv_id=c.yv_id) %>
</%def>

<%def name="outside_contents()">
<div id="testtys1" style="display:none">
  ${self.ty_heading()}
  <%include file="/common/message.mako"/>
  % if c.read_only and c.correct_url:
  ${self.btn_correct()}
  % endif
  <div class="tools d-flex justify-content-end"></div>
</div>
% if c.read_only:
<script>
  $('.ifedit', $(parent.document)).hide();
  $('.ifshow', $(parent.document)).show();
</script>
% else:
<script>
  $('.ifedit', $(parent.document)).show();
  $('.ifshow', $(parent.document)).hide();
</script>
% endif

<div id="testtys2" style="display:none">
</div>
</%def>

<%def name="ty_heading()">
% if c.ylesanne.max_pallid and c.is_edit:
<div class="text-right">
  <b> ${_("max {p}p").format(p=h.fstr(c.ylesanne.max_pallid))} </b>
</div>
% endif
</%def>
