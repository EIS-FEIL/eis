## otsingu tulemuste loetelus üks ülesanne või test, mida saab lohistada töökogumikku
<%
  itemid, uniqid, nimi, staatus_nimi, label, url = c.tkitem
  typecls = uniqid.startswith('y') and 'tkitem-y' or 'tkitem-t'
%>
  <div class="tkitem-drag">
    <div class="d-flex tkitem-search" data-uniqid="${uniqid}">
      <div style="width:30px" class="show-in-search mt-2">
        ${h.checkbox('v', itemid, label='', nohelp=True, ronly=False)}
      </div>
      <div class="flex-grow-1">
        <a href="${url}" class="LISTPOST card card-is-link px-3 py-4 mb-1"
           target="_blank" style="width:100%;z-index:10" id="dr_${itemid}">
          <div class="card-body p-0">
            <div class="d-flex align-items-center">
              <i class="mdi mdi-drag-vertical mdi-24px gray-300" aria-hidden="true"></i>
              <p class="card-text my-0 ml-4">
                <div>
                  <div><strong>${label}</strong></div>
                  <div>${nimi}</div>
                  % if staatus_nimi:
                  <div>(${staatus_nimi})</div>
                  % endif
                </div>
              </p>
            </div>
          </div>
        </a>
      </div>
      <div style="width:30px;display:none" class="p-2 show-in-tk" aria-hidden="true">
        ${h.checkbox('w', uniqid, label='', nohelp=True, class_=typecls, ronly=False, title=_("Märgi jagamiseks"))}
        ${h.hidden('itemid', itemid, fixvalue=itemid, id='itemid%s' % itemid)}
        ${h.button('', mdicls='mdi-delete', level=0, class_="tk-remove", title=_("Eemalda töökogumikust"))}
      </div>
    </div>
  </div>
