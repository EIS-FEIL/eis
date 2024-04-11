% if c.items != '':
<%include file="/common/message.mako"/>
% if not c.items:
${_("Otsingu tingimustele vastavaid teste ei leitud")}
% else:
<div class="d-flex justify-content-end mb-2">
  ${h.button(_("Lisa töökogumikku"), class_="add_y", disabled=True, level=2)}
</div>
${h.pager(c.items,
          msg_not_found=_("Otsingu tingimustele vastavaid teste ei leitud"),
          msg_found_one=_("Leiti üks tingimustele vastav test"),
          msg_found_many=_("Leiti {n} tingimustele vastavat testi"),
          listdiv='#listdiv_t',
          form='#t_search',
          newline=True)}

% for rcd in c.items:
<%
  item_id = rcd.id
  itemid = 'tot-%d' % item_id
  uniqid = f't{rcd.id}'
  item_name = rcd.nimi
  label = '%s %s' % (rcd.on_jagatudtoo and _("Töö") or _("Test"), item_id)
  url = h.url('test', id=item_id)
  c.tkitem = (itemid, uniqid, item_name, None, label, url)
%>
<%include file="tookogumik.otsing.item.mako"/>
% endfor
% endif
<script>
  init_drag_from_search($('#listdiv_t'));
</script>
% endif

