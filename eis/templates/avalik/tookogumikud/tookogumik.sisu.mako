${h.form_save(c.item.id, form_name=f'fs_{c.item.id}', class_="form-nosave")}
${h.hidden('f_nimi', c.item.nimi)}
% for tkosa in c.item.tkosad or [c.new_item()]:
<div class="tkosa ${c.is_edit and 'sortable' or ''}">
  <div class="not-draggable">
  </div>
  <%
      items = sorted(list(tkosa.tkylesanded) + list(tkosa.tktestid),
                     key=lambda r: r.seq)
      c.is_tk_edit = c.is_edit
  %>
  % for r in items:
  <%
      if isinstance(r, model.Tkylesanne):
        ylesanne = r.ylesanne
        url = h.url('ylesanded_lahendamine', id=ylesanne.id)
        label = '%s %s' % (_("Ülesanne"), ylesanne.id)
        nimi = ylesanne.nimi
        staatus_nimi = ylesanne.staatus_nimi
        itemid = 'tky-%s' % r.id
        uniqid = f'y{ylesanne.id}'
        acls = 'LISTPOST'
        typecls = 'tkitem-y'
      else:
        test = r.test
        if test.testityyp == const.TESTITYYP_EKK:
           url = h.url('test', id=test.id)
           if not c.user.has_permission('testid', const.BT_SHOW, obj=test):
               url = None
        else:
           url = h.url('testid_struktuur', id=test.id, testiruum_id=0)
        label = '%s %s' % (_("Test"), test.id)
        nimi = test.nimi
        staatus_nimi = ''
        itemid = 'tkt-%s' % r.id
        uniqid = f't{test.id}'
        acls = ''
        typecls = 'tkitem-t'
      c.tkitem = (itemid, item_id, label, nimi, staatus_nimi, url)
  %>
  <div class="tkitem d-flex mb-0" data-uniqid="${uniqid}">
    <div class="flex-grow-1">
      <a ${url and f'href="{url}"' or ''}
         class="card card-is-link px-3 py-4 mb-1 ${acls}"
         target="_blank" style="width:100%">
        <div class="card-body p-0">
          <div class="d-flex align-items-center">
            % if c.is_tk_edit:
            <i class="mdi mdi-drag-vertical mdi-24px gray-300" aria-hidden="true"></i>
            % endif
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
    <div style="width:30px" class="p-2">
      ${h.checkbox('w', uniqid, label='', nohelp=True, class_=typecls, ronly=False, title=_("Märgi jagamiseks"))}
      % if c.is_tk_edit:
      ${h.hidden('itemid', itemid, fixvalue=itemid, id='itemid%s' % itemid)}
      ${h.button('', mdicls='mdi-delete', level=0, class_="tk-remove", title=_("Eemalda töökogumikust"))}
      % endif
    </div>
  </div>
  % endfor
</div>
% endfor
${h.end_form()}
