<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${_("Turvakottide numbrite sisestamine")} | ${c.test.nimi} ${c.toimumisaeg.millal}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_('Turvakottide numbrite sisestamine'), h.url('sisestamine_turvakotid'))}
${h.crumb('%s %s' % (c.test.nimi, c.toimumisaeg.millal))}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'sisestamine' %>
</%def>


<table width="100%" class="table">
  <tr>
    <td class="fh">${_("Test")}</td>
    <td colspan="3">
      ${c.test.id}
      ${h.link_to(c.test.nimi, h.url('test_kord_toimumisaeg', test_id=c.test.id,
      kord_id=c.toimumisaeg.testimiskord_id, id=c.toimumisaeg.id))}
      ${c.toimumisaeg.tahised}
      ${c.toimumisaeg.testiosa.vastvorm_nimi}
    </td>
    <td class="frh">${_("Toimumise aeg")}</td>
    <td>${c.toimumisaeg.millal}</td>
  </tr>
</table>


${h.form_search(url=h.url('sisestamine_turvakotinumbrid', toimumisaeg_id=c.toimumisaeg.id))}
<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-md-5">
      ${h.radio('suund', 0, checkedif=c.suund, 
      label=_('Väljastus- ja  tagastuskotid'))}
      <br/>
      ${h.radio('suund', const.SUUND_VALJA, checkedif=c.suund, 
      label=_('Ainult testitööde väljastamise kotid'))}
      <br/>
      ${h.radio('suund', const.SUUND_TAGASI, checkedif=c.suund, 
      label=_('Ainult testitööde tagastamise kotid'))}
    </div>
    <div class="col-md-2">
      ${h.flb(_("Soorituskoht"),'testikoht_tahis')}
      ${h.text('testikoht_tahis', c.testikoht_tahis)}
    </div>
    <div class="col-md-2">
      ${h.flb(_("Koti number"),'kotinr')}
      ${h.text('kotinr', c.kotinr)}
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div>
        ${h.btn_search()}
      </div>
    </div>
  </div>
</div>

${h.end_form()}

<div class="listdiv">
<%include file="turvakotinumbrid.otsing_list.mako"/>
</div>
