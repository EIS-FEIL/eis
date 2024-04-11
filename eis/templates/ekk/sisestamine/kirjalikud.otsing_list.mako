% if c.items != '':
${h.pager(c.items, msg_not_found=_('Protokolle ei leitud'), msg_found_one=_('Leiti 1 protokoll'), msg_found_many=('Leiti {n} protokolli'))}
% endif
% if c.items:

<%
   c.olen_parandaja = c.user.has_permission('parandamine', const.BT_UPDATE) # const.GRUPP_PARANDAJA
   tk = c.toimumisaeg.testimiskord
%>
<table width="100%" class="table table-borderless table-striped" border="0" >
  <thead>
    <tr>
      ${h.th(_('Toimumisaeg'))}
      % if tk.sisestus_isikukoodiga:
      ${h.th_sort('koht.nimi', _('Soorituskoht'))}
      % endif
      ${h.th_sort('testiprotokoll.tahised sisestuskogum.tahis', _('Hindamisprotokoll'))}
      ${h.th_sort('hindamisprotokoll.liik', _('Hindamise liik'))}
      ${h.th_sort('sisestuskogum.tahis', _('Sisestuskogum'))}
      ${h.th_sort('hindamisprotokoll.staatus1', _('I sisestamine'))}
      % if c.toimumisaeg.kahekordne_sisestamine:
      ${h.th_sort('hindamisprotokoll.staatus2', _('II sisestamine'))}
      % endif
      % if c.olen_parandaja:
      ${h.th_sort('hindamisprotokoll.staatus', _('Parandamine'))}      
      % endif
    </tr>
  </thead>
  <tbody>
    % for n, rcd in enumerate(c.items):
    <% 
       hpr, tpr_tahised, tkoht_tahised, sk_tahis, sk_nimi, k_nimi, r_tahis = rcd 
       hpr_tahised = '%s-%s' % (tpr_tahised, sk_tahis)
       li_tahised = hpr_tahised.split('-')
       # toimumisaja tähis
       ta_tahised = '-'.join(li_tahised[:3])
       # hindamisprotokolli tähis ilma toimumisajata
       tahis = '-'.join(li_tahised[3:])
    %>
    <tr>
      <td>${ta_tahised}</td>
      % if tk.sisestus_isikukoodiga:
      <td>
        % if r_tahis:
        ${k_nimi}, ruum ${r_tahis}
        % else:
        ${k_nimi}
        % endif
      </td>
      % endif
      <td>${tahis} <!--hpr ${hpr.id}--></td>
      <td>${c.opt.HINDAJA.get(hpr.liik)}</td>
      <td>
        ${sk_tahis}
        ${sk_nimi}
      </td>

      <td>
        ## avada saan siis, kui olen ise I sisestaja 
        ## või seda veel pole ja ma pole II sisestaja
        % if hpr.can_sis1(c.user.id):
        ${h.link_to(hpr.staatus1_nimi, h.url('sisestamine_kirjalikud_hindamised',
        hindamisprotokoll_id=hpr.id, sisestus='1'))}
        % else:
        ${hpr.staatus1_nimi}
        % endif
      </td>
      % if c.toimumisaeg.kahekordne_sisestamine:
      <td>
        % if hpr.can_sis2(c.user.id):
        ${h.link_to(hpr.staatus2_nimi, h.url('sisestamine_kirjalikud_hindamised',
        hindamisprotokoll_id=hpr.id, sisestus='2'))}
        % else:
        ${hpr.staatus2_nimi}
        % endif
      </td>
      % endif
      % if c.olen_parandaja:
      <td>
        % if hpr.staatus1 or hpr.staatus2:
        ## avada saan siis, kui mul on sisestuste parandamise õigus
        ${h.link_to(hpr.staatus_nimi,h.url('sisestamine_kirjalikud_hindamised',
        hindamisprotokoll_id=hpr.id, sisestus='p'),
        style=hpr.staatus==const.H_STAATUS_POOLELI and "color:red" or None)}
        % else:
        ${hpr.staatus_nimi}
        % endif
      </td>
      % endif
    </tr>
    % endfor
  </tbody>
</table>
% endif
