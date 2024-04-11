<%
  test = c.sooritaja.test
  ch = h.colHelper('col-md-3 col-sm-4', 'col-md-3 col-sm-8')
  chr = h.colHelper('col-md-3 col-sm-4 text-md-right', 'col-md-3 col-sm-8')
%>   
<div class="form-wrapper-lineborder">
  <div class="form-group row">
    ${ch.flb(_("Testisooritaja"), 'sooritaja_nimi')}
    <div class="col" id="sooritaja_nimi">
% if c.app_ekk and c.user.has_permission('eksaminandid', const.BT_SHOW):
      ${h.link_to(c.sooritaja.nimi, h.url('admin_eksaminand', id=c.kasutaja.id))}
% else:
      ${c.sooritaja.nimi}
% endif
% if c.kasutaja.isikukood:
      ${c.kasutaja.isikukood}
% else:
      ${h.str_from_date(c.kasutaja.synnikpv)}
% endif
% if c.sooritaja.vabastet_kirjalikust:      
      (65a ja vanem kodakondsuse taotleja)
% endif
    </div>
  </div>
% if not c.regi_isikuandmeteta:
  <div class="form-group row">
    ${ch.flb(_("Postiaadress"),'aadress')}
    <div class="col" id="aadress">
      ${c.kasutaja.tais_aadress}
      ${c.kasutaja.postiindeks}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Telefon"),'telefon')}
    <div class="${ch.col2}" id="telefon">
      ${c.kasutaja.telefon}
    </div>
    ${chr.flb(_("E-post"), 'epost')}
    <div class="${ch.col2}" id="epost">
      ${c.kasutaja.epost}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Õppevorm"), 'oppevorm')}
    <div class="${ch.col2}" id="oppevorm">
      ${c.sooritaja.oppevorm_nimi}
    </div>
    ${chr.flb(_("Klass"), 'klass')}
    <div class="${ch.col2}" id="klass">
      ${c.sooritaja.klass}
    </div>
  </div>
% endif  
  <div class="form-group row">
    ${ch.flb(_("Õppeasutus"), 'kool_nimi')}
    <div class="${ch.col2}" id="kool_nimi">
      % if c.sooritaja.koolinimi:
      ${c.sooritaja.koolinimi.nimi}
      % elif c.sooritaja.kool_koht:
      ${c.sooritaja.kool_koht.nimi}
      % endif
    </div>
    ${chr.flb(_("Õppekeel"), 'oppekeel')}
    <div class="${ch.col2}" id="oppekeel">
      ${const.EHIS_LANG_NIMI.get(c.sooritaja.oppekeel)}
    </div>
  </div>

% if not c.regi_isikuandmeteta:      
  % if c.kasutaja.lopetamisaasta:
  <div class="form-group row">
    ${ch.flb(_("Lõpetamise aasta"), 'lopetamisaasta')}
    <div class="${ch.col2}">
      <span class="pr-3" id="lopetamisaasta">${c.kasutaja.lopetamisaasta}</span>
      ${h.checkbox1('lopetanud', 1, checked=c.kasutaja.lopetanud, label=_("Lõpetanud"))}
      ${h.checkbox1('lopetanud_kasitsi', 1, checked=c.kasutaja.lopetanud_kasitsi, label=_("Lõpetanud (käsitsi)"))}
    </div>
    ${chr.flb(_("Põhjus"), 'pohjus')}
    <div class="${ch.col2}" id="pohjus">
      ${c.kasutaja.lopetanud_pohjus}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Haridust tõendav dokument"), 'tunnistus_nr')}
    <div class="${ch.col2}" id="tunnistus_nr">
      ${c.kasutaja.tunnistus_nr}
    </div>
    ${chr.flb(_("väljastamise kuupäev"), 'tunnistus_kp')}
    <div class="${ch.col2}" id="tunnistus_kp">
      ${h.str_from_date(c.kasutaja.tunnistus_kp)}
    </div>
  </div>
  % endif
% endif  
  <div class="form-group row">
    ${ch.flb(_("Test"), 'dtest_id')}
    <div class="col d-flex flex-wrap">
      <div class="flex-grow-1" id="dtest_id">
      ${c.sooritaja.test_id}
      ${test.nimi}
      (${test.testiliik_nimi}
      ${test.aine_nimi})
      </div>
% if not c.regi_isikuandmeteta and c.sooritaja.soovib_konsultatsiooni:        
      <div>
        ${h.checkbox1('soovib_konsultatsiooni', 1, checked=c.sooritaja.soovib_konsultatsiooni, label=_("Soovib konsultatsiooni"))}
      </div>
% endif    
    </div>
  </div>
</div>

########################## testiosad
<div>
  ${self.tbl_sooritused()}
</div>

<div class="form-wrapper-lineborder">  
  <div class="form-group row">
    ${ch.flb(_("Soorituskeel"), 'soorituskeel')}
    <div class="${ch.col2}" id="soorituskeel">
      ${model.Klrida.get_lang_nimi(c.item.lang)}
    </div>
% if not c.regi_isikuandmeteta:      
    ${chr.flb(_("Soovitav soorituspiirkond"), 'piirkond_nimi')}
    <div class="${ch.col2}" id="piirkond_nimi">
      ${c.item.piirkond_nimi or ''}
    </div>
% endif    
  </div>
% if not c.regi_isikuandmeteta:      
  % if c.item.kursus_kood:
  <div class="form-group row">
    ${ch.flb(_("Kursus"), 'kursus')}
    <div class="col" id="kursus">
      ${c.item.kursus_nimi}
    </div>
  </div>
  % endif
% endif
  % if test.testiliik_kood in (const.TESTILIIK_KOOLIPSYH, const.TESTILIIK_LOGOPEED):
  <div class="form-group row">
    ${ch.flb(_("Lapsevanema nõusolek"), 'vanem_nous')}
    <div class="col" id="vanem_nous">
      ${h.sbool(c.item.vanem_nous)}
    </div>
  </div>
  % endif

  <div class="form-group row">
    ${ch.flb(_("Registreerimise seisund"), 'staatus_nimi')}
    <div class="${ch.col2}" id="staatus_nimi">
      ${c.item.staatus_nimi}
    </div>
% if not c.regi_isikuandmeteta:        
    ${chr.flb(_("Tasu summa"), 'tasu')}
    <div class="${ch.col2}" id="tasu">
      % if c.item.tasu:
      ${h.fstr(c.item.tasu)} &euro;
        % if c.item.tasutud:
        (${_("tasutud")})
        % else:
        (${_("tasumata")})
        % endif
      % endif
    </div>
% endif    
  </div>
% if not c.regi_isikuandmeteta:          
  <div class="form-group row">
    ${ch.flb(_("Registreerimise teade"), 'regteateaeg')}
    <div class="col" id="regteateaeg">
      ${h.str_from_datetime(c.sooritaja.regteateaeg)}
    </div>
  </div>
  % if c.item.tasu:
  <div class="form-group row">
    ${ch.flb(_("Viimane meeldetuletus"), 'meeldetuletusaeg')}
    <div class="col" id="meeldetuletusaeg">
      ${h.str_from_datetime(c.sooritaja.meeldetuletusaeg)}
    </div>
  </div>
  % endif
% endif
  <div class="form-group row">
    ${ch.flb(_("Registreerimise viis"), 'regviis')}
    <div class="${ch.col2}" id="regviis">
      ${c.item.regviis_nimi}
      % if c.item.muutmatu == const.MUUTMATU_MUUTMATU:
      (${_("kool ei saa muuta")})
      % elif c.item.muutmatu:
      (${_("kool ei saa tühistada")})      
      % endif
    </div>
    ${chr.flb(_("Registreerija"), 'esitaja_nimi')}
    <div class="${ch.col2}" id="esitaja_nimi">
      ${c.item.esitaja_kasutaja.nimi}
      % if c.item.esitaja_koht:
      ${c.item.esitaja_koht.nimi}
      % endif
      ${h.str_from_datetime(c.item.reg_aeg)}
    </div>
  </div>
  % if test.testiliik_kood == const.TESTILIIK_SISSE:
  <div class="form-group row">
    ${ch.flb(_("Õppeasutused, millele avaldatakse testitulemused"))}
    <div class="col">
      % for r in c.item.kandideerimiskohad:
      <div>${r.koht.nimi}</div>
      % endfor
    </div>
  </div>
  % endif
  
% if not c.regi_isikuandmeteta:        
  <div class="form-group row">
    ${ch.flb(_("Märkused"), 'markus')}
    <div class="col" id="markus">
      ${c.item.markus}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Sooritaja märkused"), 'reg_markus')}
    <div class="col" id="reg_markus">
      ${c.item.reg_markus}
    </div>
  </div>
% endif  
</div>

% if not c.regi_isikuandmeteta:        
<%include file="rahvusvaheline_eksam.mako"/>

<div class="form-wrapper-lineborder my-1">
  <div class="form-group row">
    ${ch.flb(_("Töövaldkond"), 'tvaldkond')}
    <div class="${ch.col2}" id="tvaldkond">
      ${c.item.tvaldkond_nimi}
    </div>
    ${chr.flb(_("Amet"), 'amet')}
    <div class="${ch.col2}" id="amet">
      ${c.item.amet_nimi or c.item.amet_muu}
    </div>
  </div>
  <div class="form-group row">
    ${ch.flb(_("Haridus"), 'haridus')}
    <div class="${ch.col2}" id="haridus">
      ${c.item.haridus_nimi}
    </div>
    ${chr.flb(_("Kodakondsus"), 'kodakondsus')}
    <div class="${ch.col2}" id="kodakondsus">
      ${c.item.kodakond_nimi}
    </div>
  </div>
  % if c.item.isikukaart_id:
  ${self.isikukaart()}
  % endif
  % if c.kasutaja.lisatingimused:
  <div class="form-group row">
    ${ch.flb(_("Lisatingimused"), 'lisat')}
    <div class="col" id="lisat">
      ${c.kasutaja.lisatingimused}
    </div>
  </div>
  % endif
</div>
% endif

% if c.app_ekk:
${self.sooritajalogid()}
${self.soorituslogi_acc()}
% endif    

<%def name="isikukaart()">
<%
  ch = h.colHelper('col-md-3 col-sm-4', 'col-md-3 col-sm-8')
  kaart = model.Isikukaart.get(c.item.isikukaart_id)
%>
% if kaart:
<div class="form-group row">
  ${ch.flb(_("Haridustöötaja andmed"))}
  <div class="col">
    % for too in kaart.isikukaart_tood:
    <div>
    ${too.oppeasutus} ${too.ametikoht}
    <% ained = [r.oppeaine for r in too.isikukaart_too_oppeained] %>
    % if ained:
    (${', '.join(list(set(ained)))})
    % endif
    </div>
    % endfor
  </div>
</div>
% endif
</%def>

<%def name="tbl_sooritused()">
<%
  sooritused = list(c.item.sooritused)
  mitu = len(sooritused) > 1
%>
    <table  width="100%" class="table table-borderless table-striped my-1">
        <thead>
          <tr>
            % if c.item.testimiskord_id:
            ${h.th(_("Toimumisaeg"))}
            ${h.th(_("Vastamise vorm"))}
            % elif mitu:
            ${h.th(_("Testiosa"))}
            % endif
            ${h.th(_("Soorituskoht"))}
            % if c.item.testimiskord_id:
            ${h.th(_("Soorituse tähis"))}
            % endif
            ${h.th(_("Olek"))}
            ${h.th(_("Algus"))}
            ${h.th(_("Märkus"))}
          </tr>
        </thead>
        <tbody>
          % for tos in sooritused:
          <tr>
            <% 
               testiosa = tos.testiosa 
               toimumisaeg = tos.toimumisaeg
            %>
            % if c.item.testimiskord_id:
            <td>
              % if toimumisaeg:
              ${toimumisaeg.tahised}
              % endif
            </td>
            <td>${testiosa.vastvorm_nimi}</td>
            % elif mitu:
            <td>${testiosa.nimi}</td>
            % endif
            <td>
              <%
                testikoht = tos.testikoht
                koht = testikoht and testikoht.koht
              %>
              % if koht:
              ${koht.nimi}
              % else:
              ${_("Määramata")}
              % endif
            </td>
            % if c.item.testimiskord_id:            
            <td>${tos.tahised}</td>
            % endif
            <td>${tos.staatus_nimi}</td>
            <td>
              <%
                testiruum = tos.testiruum
                testiprotokoll = tos.testiprotokoll                
                algus = tos.kavaaeg or testiprotokoll and testiprotokoll.algus or testiruum and testiruum.algus
                if not algus:
                   toimumispaev = tos.reg_toimumispaev
                   if toimumispaev:
                       algus = toimumispaev.aeg
              %>
              % if algus and algus.hour:
              ${algus.strftime('%d.%m.%Y %H.%M')}
              % elif algus:
              ${algus.strftime('%d.%m.%Y')}
              % elif ta:
              ${ta.millal}
              % endif
            </td>
            <td>
% if not c.regi_isikuandmeteta:      
              <%
                 if c.app_ekk:
                    eri_url = h.url('regamine_erivajadus', id=tos.id)
                 else:
                    eri_url = h.url('nimekiri_erivajadus', id=tos.id)
              %>
              ${h.link_to(_("Eritingimused"), eri_url, mdicls2=tos.on_erivajadused and 'mdi-check' or None)}
% endif
              <% tugik = tos.tugiisik_kasutaja %>
              % if tugik:
              <div>${_("Tugiisik")}: ${tugik.nimi}</div>
              % endif
            </td>
          </tr>
          % endfor
        </tbody>
      </table>
    % for tos in sooritused:
    % if tos.on_rikkumine:
      <% 
      if mitu:
         buf = _("Rikkumise tõttu on testiosa {s} hinnatud 0 punktiga.").format(s=tos.testiosa.tahis)
      else:
         buf = _("Rikkumise tõttu on töö hinnatud 0 punktiga.")
      buf += '<br/>' + tos.rikkumiskirjeldus
      %>
      ${h.alert_warning(buf, False)}
    % endif
    % endfor
</%def>

<%def name="sooritajalogid()">
<table  class="table mt-1">
  <% prev_staatus = None %>
  % for r in c.item.sooritajalogid:
##  % if prev_staatus is not None and prev_staatus != r.staatus:
  <tr>
    <td>
      % if r.staatus == const.S_STAATUS_TYHISTATUD:
      ${_("Tühistatud")}
      % elif prev_staatus == const.S_STAATUS_TYHISTATUD and r.staatus <= const.S_STAATUS_REGATUD:
      ${_("Taastatud")}
      % else:
      ${r.staatus_nimi}
      % endif
      % if r.pohjus:
      (${r.pohjus})
      % endif
    </td>
    <td>${h.str_from_datetime(r.created, True)}</td>
    <td>${model.Kasutaja.get_name_by_creator(r.creator) or r.creator}</td>
    <td>
      % if r.staatus != const.S_STAATUS_REGAMATA:
      <%
        data = [model.Klrida.get_str('SOORKEEL', r.lang) or r.lang,
                r.kursus_kood and 'kursus %s' % r.kursus_kood or '',
                r.pallid is not None and '%sp' % h.fstr(r.pallid) or '',
                r.hinne is not None and 'hinne %s' % r.hinne or '',
               ]
      %>
      ${', '.join([v for v in data if v])}
      % endif
    </td>
  </tr>
##  % endif
  <% prev_staatus = r.staatus %>
  % endfor
</table>
</%def>

<%def name="soorituslogi_acc()">
<div class="accordion mb-2" id="soorituslogi_acc">
  <div class="accordion-card card parent-accordion-card">
    <div class="card-header" id="heading_log1">
      <div class="accordion-title" style="background-color:transparent">
        <button class="btn btn-link collapsed" type="button"
                data-toggle="collapse"
                data-target="#collapseosalog"
                aria-controls="collapseosalog"
                aria-expanded="true"
                style="background-color:transparent">
          <span class="btn-label"><i class="mdi mdi-chevron-down"></i>
            ${_("Testiosasoorituste logi")}
          </span>
        </button>
      </div>
    </div>
    <div id="collapseosalog" class="collapse" aria-labelledby="headingosalog">
      <div class="card-body">
        <div class="content" id="osalog_content">
          ${self.soorituslogid()}
        </div>
      </div>
    </div>
  </div>
</div>
</%def>

<%def name="soorituslogid()">
% for tos in c.item.sooritused:
<h2 class="h3">
  ${_("Testiosa")}: ${tos.testiosa.nimi}
  <span class="small">(${tos.id})</span>
</h2>
<table  class="table">
  % for r in tos.soorituslogid:
  <tr>
    <td>${r.staatus_nimi}
      % if r.stpohjus:
      (${r.stpohjus})
      % endif
    </td>
    <td>${r.hindamine_staatus_nimi}</td>
    <td>
      % if r.pallid is not None:
      ${h.fstr(r.pallid)}p
      % endif
    </td>
    <td>
      % if r.tulemus_protsent is not None:
      ${h.fstr(r.tulemus_protsent)}%
      % endif
    </td>
    <td>${r.testiarvuti_id}</td>
    <td>${h.str_from_datetime(r.created, True)}</td>
    <td>${r.creator}</td>
    <td>${model.Kasutaja.get_name_by_creator(r.creator)}</td>
    <td>
      ${r.tahised}
      % if r.testikoht_id:
      <% testikoht = r.testikoht %>
      koht ${testikoht and testikoht.tahis or ''}
      <span class="small">(${r.testikoht_id})</span>
      % endif
      % if r.testiruum_id:
      <% testiruum = r.testiruum %>
      ruum ${testiruum and testiruum.tahis or ''}
      <span class="small">(${r.testiruum_id})</span>
      % endif
      % if r.kavaaeg:
      ${h.str_from_datetime(r.kavaaeg)}
      % endif
    </td>
  </tr>
  % endfor
</table>
${self.alatestisoorituslogid(tos)}
% endfor
</%def>

<%def name="alatestisoorituslogid(tos)">
% for atos in tos.alatestisooritused:
<h3 class="h4">Alatest: ${atos.alatest.nimi}
  <span class="small">(${atos.id})</span>
</h3>
<table  class="table">
  % for r in atos.alatestisoorituslogid:
  <tr>
    <td>${r.staatus_nimi}</td>
    <td>
      % if r.pallid is not None:
      ${h.fstr(r.pallid)}p
      % endif
    </td>
    <td>${h.str_from_datetime(r.created, True)}</td>
    <td>${model.Kasutaja.get_name_by_creator(r.creator) or r.creator}</td>
  </tr>
  % endfor
</table>
% endfor
</%def>
