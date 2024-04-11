% if c.user.has_permission('omanimekirjad', const.BT_CREATE):
<div id="addnk" style="display:none;" href="${h.url('test_tknimekiri')}">
  <div id="choose_t">
    ${h.button(_('Suuna test sooritamiseks'), clicked=True, level=2, id="usetest")}
  </div>
  <div id="choose_y">
    <span class="p-3 rounded" style="background-color:#fff">
      ${_("Valitud {n} ülesannet").format(n='<span class="cnt"></span>')}
    </span>
    <div>
      ${h.button(_('Suuna sooritamiseks testina'), clicked=True, level=2, id="lisatest")}
    </div>
    <div>
      ${h.button(_('Suuna sooritamiseks ülesannetena'), clicked=True, level=2, id="lisatoo")}
    </div>
  </div>
</div>
% endif

${self.tbl_jagamised(c.jagamised_lahendamisel, _('Lahendamisel jagamised'), 'lahendamisel')}
${self.tbl_jagamised(c.jagamised_moodunud, _('Möödunud jagamised'), 'moodunud')}

<%def name="tbl_jagamised(jagamised, title, jcls)">
% if jagamised:
<%
  c.jagamised = jagamised
  c.jcls = jcls
%>
<div style="padding-top:5px;clear:both">
  <h2 class="mb-1">${title}</h2>
  <div class="jagamised-${jcls}">
  <%include file="tookogumik.jagamised_list.mako"/>
  </div>
</div>
% endif
<br/>
</%def>
