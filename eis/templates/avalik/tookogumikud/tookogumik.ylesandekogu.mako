% for res in c.itemdata:
<%
  group_name, items, group_id = res[:3]
%>
<div class="card-body">
        <div class="accordion-content pl-0 p-0">
          <div class="accordion" id="acc_${group_id}">
            <div class="d-flex align-items-start accordion-outer-wrapper pl-2">

              <div class="accordion-card card ykg">
                <div class="card-header" id="heading_${group_id}">
                  <div class="accordion-title">
                    <button class="btn btn-link collapsed"
                            style="white-space:normal"
                            type="button"
                            data-toggle="collapse"
                            data-target="#collapse_${group_id}"
                            aria-expanded="true"
                            aria-controls="collapse_${group_id}"
                            >
                      <span class="btn-label">
                        <i class="mdi mdi-chevron-down"></i>
                        ${group_name} (${len(items)})
                      </span>
                    </button>
                    ${h.hidden('jrk_args', c.jrk_args)}
                  </div>
                </div>

                <% c.is_tk_edit = True %>
                <div id="collapse_${group_id}" class="collapse" aria-labelledby="heading_${group_id}" data-parent="#acc_${group_id}">
                  <div class="card-body">
                    <div class="content px-0 p-0 pb-1">
                      % for itemid, uniqid, item_id, item_name, staatus_nimi in items:
                      <%
                        if itemid.startswith('yky'):
                           url = h.url('ylesanded_lahendamine', id=item_id)
                           label = '%s %s' % (_("Ülesanne"), item_id)
                        else:
                           url = h.url('test', id=item_id)
                           label = '%s %s' % (_("Test"), item_id)

                        c.tkitem = (itemid, uniqid, item_name, staatus_nimi, label, url)
                      %>
                      <%include file="tookogumik.otsing.item.mako"/>
                      % endfor
                    </div>
                  </div>
                </div>

              </div>
            </div>
          </div>
        </div>
</div>
% endfor
