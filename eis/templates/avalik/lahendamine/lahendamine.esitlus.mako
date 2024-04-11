<%inherit file="/avalik/lahendamine/esitlus.mako"/>

<%def name="gen_submit_url()">
<% c.submit_url = h.url_current('updatetask', yv_id=c.yv_id, kl_id=c.klaster_id) %>
</%def>

<%def name="outside_contents()">
<div id="testtys1" style="display:none">
  <%include file="/common/message.mako"/>
</div>
% if c.read_only:
<script>
$(function(){
  $('.ifedit', $(parent.document)).hide();
  $('.ifshow', $(parent.document)).show();
});
</script>
% endif
<div id="testtys2" style="display:none">
  % if c.read_only:
  % if c.vastus:
  <div class="mt-4">
    <h2>${_("Antud vastused")}</h2>
    ${h.literal(c.vastus)}
  </div>
  % endif
  
  % if c.calculation:
  <div class="mt-4">
    <h2>${_("Arvutuskäik")}</h2>
    ${h.literal(c.calculation)}
  </div>
  % endif
  % endif
</div>
</%def>
