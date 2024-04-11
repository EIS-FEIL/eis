<%include file="/common/message.mako"/>
% if c.items != '':
% if not c.items:
${_("Ükski ülesanne ei vasta otsingutingimustele")}
% else:
<div class="d-flex justify-content-end mb-2">
  ${h.button(_("Lisa töökogumikku"), class_="add_y", disabled=True, level=2)}
</div>

${h.pager(c.items,
          msg_not_found=_("Otsingu tingimustele vastavaid ülesandeid ei leitud"),
          msg_found_one=_("Leiti üks tingimustele vastav ülesanne"),
          msg_found_many=_("Leiti {n} tingimustele vastavat ülesannet"),
          listdiv='#listdiv',
          form='#yo_search',
          newline=True)}
% for rcd in c.items:
<%
  item_id = rcd.id
  itemid = 'yoy-%d' % item_id
  uniqid = f'y{rcd.id}'
  item_name = rcd.nimi
  label = '%s %s' % (_("Ülesanne"), item_id)
  url = h.url('ylesanded_lahendamine', id=item_id)
  c.tkitem = (itemid, uniqid, item_name, rcd.staatus_nimi, label, url)
%>
<%include file="tookogumik.otsing.item.mako"/>
% endfor
% endif
<script>
  init_drag_from_search($('#listdiv'));
</script>
% endif

