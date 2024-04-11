% if c.jagamised:
  <table width="100%" class="table table-striped" >
    <col/>
    <col/>
    <col width="30%"/>    
    <thead>
      <tr>
        ${h.th(_('Nimetus'))}
        ${h.th(_('Tähtaeg'))}
        ${h.th(_('Lõpetanud'))}
      </tr>
    </thead>
    <tbody>
      % for nimekiri, test, testiruum_id, total, tehtud in c.jagamised:
      <%
        testiruum_id = testiruum_id or 0
        if c.user.has_permission('testid', const.BT_SHOW, test):
           if test.testityyp == const.TESTITYYP_EKK:
              url_test = h.url('testid_yldandmed', id=test.id, testiruum_id=testiruum_id)
           else:
              url_test = h.url('testid_struktuur', id=test.id, testiruum_id=testiruum_id)
        elif c.user.has_permission('omanimekirjad', const.BT_SHOW, nimekiri):
           url_test = h.url('test_tulemused', test_id=test.id, testiruum_id=testiruum_id)
        else:
           url_test = None
        label = f'{test.nimi} ({nimekiri.nimi})'
      %>
      <tr>
        <td>
          % if url_test:
          ${h.link_to(label, url_test)}
          % else:
          ${label}
          % endif
        </td>
        <td>
          <%
            if test.avalik_kuni and nimekiri.kuni:
               kuni = min(test.avalik_kuni, nimekiri.kuni)
            else:
               kuni = test.avalik_kuni or nimekiri.kuni
          %>
          ${h.str_from_date(kuni)}
        </td>
        <td>
          % if total:
          <% percent = int(round(tehtud * 100. / total)) %>
          ${h.progress(percent, _("Lõpetanute osakaal"))}
          % else:
          ${_("Jagamata")}
          % endif
        </td>
      </tr>
      % endfor
    </tbody>
  </table>
% endif
% if c.MAX_PAGE and len(c.jagamised) == c.MAX_PAGE:
  <a href="${h.url('tookogumik_jagamised', sub=c.jcls)}" style="float:right" onclick="dialog_load($(this).attr('href'), '', 'GET', $('div.jagamised-${c.jcls}'));return false;">
    <i class="mdi mdi-arrow-expand-down"></i>
    ${_("Näita rohkem")}
  </a>
% elif c.MAX_PAGE and len(c.jagamised) > c.MAX_PAGE:
  <a href="${h.url('tookogumik_jagamised', sub=c.jcls, max_limit=True)}" style="float:right" onclick="dialog_load($(this).attr('href'), '', 'GET', $('div.jagamised-${c.jcls}'));return false;">
    <i class="mdi mdi-arrow-collapse-up"></i>    
    ${_("Näita vähem")}
  </a>
% endif
