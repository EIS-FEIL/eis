${h.form_search(h.url_current('index'))}

<div class="gray-legend p-3 filter-w">
  <div class="row filter">
    <div class="col-12 col-md-4 col-lg-3">
      <div class="form-group">
        ${h.flb(_("Kasutajaroll"))}
        ${h.select('grupp_id', c.grupp_id, c.opt_grupid, empty=True)}
      </div>
    </div>
    <div class="col-12 col-md-4 col-lg-3 d-flex justify-content-end align-items-end">
      <div class="form-group flex-grow-1">
        ${h.checkbox1('kehtiv', 1, checked=c.kehtiv, label=_("Ainult kehtivad rollid"))}
      </div>
    </div>
    <div class="col d-flex justify-content-end align-items-end">
      <div class="form-group">
        ${h.btn_search()}
        ${h.submit(_("Uuenda EHISest"), id="ehis", level=2)}

        % if c.can_roll:
        ${h.btn_to_dlg(_("Lisa kasutajaroll"),
        h.url('admin_koht_new_kasutaja', sub='roll', koht_id=c.koht.id), title=_("Kasutajaroll"),
        level=2, mdicls='mdi-plus')}
        % endif

       % if c.app_ekk:
        ${h.btn_to_dlg(_("Lisa pedagoogide andmed käsitsi failist"), h.url('admin_koht_new_kasutaja',
        koht_id=c.koht.id, sub='pedagoogfail'), title=_("Pedagoogid"), width=600, level=2, mdicls="mdi-plus")}
       % endif

      </div>
    </div>
  </div>
</div>
${h.end_form()}

<% c.antavad = [r[0] for r in c.opt.get_antav_kooligrupp(c.app_ekk)] %>

<div class="listdiv">
  <table width="100%" class="table table-striped tablesorter" >
    <thead>
      <tr>
        ${h.th(_("Nimi"))}
        ${h.th(_("EHISest saadud rollid"))}
        ${h.th(_("EISis antud rollid"))}
        ${h.th(_("Soorituskohaga seotud isik"))}
      </tr>
    </thead>
    <tbody>
      % for n, rcd in enumerate(c.items):
      <%
        k_id, ik, eesnimi, perenimi = rcd[0]
        nimi = f'{eesnimi} {perenimi}'
        ehis_rollid = rcd[1]
        eis_rollid = rcd[2]
        seotud = rcd[3]
      %>
      <tr>
        <td>
          % if c.app_ekk and k_id:
          ${h.link_to(nimi, h.url('admin_kasutaja', id=k_id))}
          % else:
          ${nimi}
          % endif
        </td>
        <td>
          % for rcd in ehis_rollid:
          ${self.roll(rcd, ik, nimi)}
          % endfor
        </td>
        <td>
          % for rcd in eis_rollid:
          ${self.roll(rcd, ik, nimi)}
          % endfor
        </td>
        <td>
          % for rcd in seotud:
          ${self.roll(rcd, ik, nimi)}
          % endfor
        </td>
      </tr>
      % endfor
    </tbody>
  </table>
</div>

<%def name="roll(rcd, ik, nimi)">            
          <div>
            <%
              if isinstance(rcd, model.Kasutajaroll):
                 title = rcd.kasutajagrupp.nimi
                 if rcd.kasutajagrupp_id == const.GRUPP_AINEOPETAJA:
                      title += ' (' + rcd.aine_nimi + ')'
                 kuni = rcd.kehtib_kuni_ui
              elif isinstance(rcd, model.Kasutajakoht):
                 title = _("Jah")
                 kuni = None
              elif isinstance(rcd, model.Pedagoog):
                 title = rcd.kasutajagrupp.nimi
                 koodid = set([r.ehis_aine_kood for r in rcd.ainepedagoogid])
                 nimed = [model.Klrida.get_str('EHIS_AINE', r) for r in koodid]
                 ained = sorted([r.lower() for r in nimed if r])
                 if ained:
                    title += ' (' + ', '.join(ained) + ')'
                 kuni = rcd.kehtib_kuni
            %>
            ${title}
            % if kuni:
            ${_("kuni {d}").format(d=h.str_from_date(kuni))}
            % endif
            % if isinstance(rcd, model.Kasutajaroll):
              % if c.can_roll and rcd.kasutajagrupp_id in c.antavad:
            ${h.btn_to_dlg('', h.url('admin_koht_edit_kasutaja', koht_id=c.koht.id, id=rcd.id, sub='roll'),
            title=_("Rolli kehtivuse muutmine"),  level=0, mdicls='mdi-file-edit')}
            ${h.remove(h.url('admin_koht_delete_kasutaja', koht_id=c.koht.id, id=rcd.id, sub='roll'),
            confirm_id="confirm_kr_%s" % rcd.id)}
            <span id="confirm_kr_${rcd.id}" style="display:none">
              ${_("Kas oled kindel, et soovid isikult {nimi} rolli ({roll}) ära võtta?").format(nimi=nimi, roll=title)}
            </span>
              % endif
           % elif isinstance(rcd, model.Kasutajakoht):
              % if c.can_edit:
            ${h.remove(h.url('admin_koht_delete_kasutaja', koht_id=c.koht.id, id=rcd.id, sub='kasutaja'),
            confirm_id="confirm_kk_%s" % rcd.id)}
            <span id="confirm_kk_${rcd.id}" style="display:none">
              ${_("Kas oled kindel, et soovid {nimi} eemaldada soorituskohaga seotud isikute seast?").format(nimi=nimi)}
            </span>
              % endif

            % elif isinstance(rcd, model.Pedagoog):
            % if c.can_edit and not rcd.on_ehisest:
            ${h.remove(h.url('admin_koht_delete_kasutaja', koht_id=c.koht.id, id=rcd.id, sub='pedagoog'),
            confirm_id="confirm_p_%s" % rcd.id)}
            <span id="confirm_p_${rcd.id}" style="display:none">
              ${_("Kas oled kindel, et soovid isikult {nimi} pedagoogi rolli ära võtta?").format(nimi=nimi)}
            </span>
            % endif
        
           % endif
          </div>
</%def>          
  
