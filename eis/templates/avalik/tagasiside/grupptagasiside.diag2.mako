## vorm peab kirjeldama style .items_tbl
## peab olema c.items_tbl ja c.tts
## (aga c.tts võib olla None, kui testil see kirje puudub)

################# tagasiside bugzilla 624 formaadis

<p>
  ${c.tts and c.tts.tran(c.lang).sissejuhatus_opetajale or ''}
</p>
<p>
  Lõpetatud tööde arv:
  % if c.cnt_tehtud and (c.stat_valimis or c.stat_riiklik):
  ${c.cnt_tehtud}
  % elif c.cnt_tehtud:
  <u class="toggle-tehtud">${c.cnt_tehtud}</u>
  <ul class="tehtud" style="display:none">
    % for sooritaja in c.sooritajad:
    % if sooritaja.staatus == const.S_STAATUS_TEHTUD:
    <li>${sooritaja.nimi}</li>
    % endif
    % endfor
  </ul>
  % else:
  0
  % endif
</p>
% if not c.valimitagasiside:
<p>
  Alustamata tööde arv:
  % if c.cnt_alustamata and (c.stat_valimis or c.stat_riiklik):
  ${c.cnt_alustamata}
  % elif c.cnt_alustamata:
  <u class="toggle-alustamata">${c.cnt_alustamata}</u>
  <ul class="alustamata" style="display:none">
    % for sooritaja in c.sooritajad:
    % if sooritaja.staatus in (const.S_STAATUS_ALUSTAMATA, const.S_STAATUS_REGATUD):
    <li>${sooritaja.nimi}</li>
    % endif
    % endfor
  </ul>
  % else:
  0
  % endif
</p>
% endif
<script>
  % if not (c.stat_valimis or c.stat_riiklik):
  $('.toggle-tehtud').css('cursor','pointer').click(function(){ $('.tehtud').toggle(); });
  $('.toggle-alustamata').css('cursor','pointer').click(function(){ $('.alustamata').toggle(); });
  % endif
</script>
<p>
  % if c.avg_ajakulu or c.avg_osa_ajakulu:
  <%
    if not c.avg_osa_ajakulu:
       buf = _('{n} minutit').format(n=c.avg_ajakulu)
    elif len(c.test.testiosad) == 1:
       buf = _('{n} minutit').format(n=c.avg_osa_ajakulu[0][1])
    else:
       li = [osa_nimi + ' ' + _('{n} minutit').format(n=ajakulu) for (osa_nimi, ajakulu) in c.avg_osa_ajakulu]
       if c.avg_ajakulu:
          li.append(_('test kokku {n} minutit').format(n=c.avg_ajakulu))
       buf = ', '.join(li)
  %>
  ${_("Keskmine lahendamise aeg:")} ${buf} 
  % endif
</p>

<p>
  ${c.tts and c.tts.tran(c.lang).kokkuvote_opetajale or ''}
</p>


% if c.items_tbl:
% if c.stat_riiklik:
<h2>Riiklik tagasiside raport</h2>
% elif c.valimitagasiside:
<h2>Valimi (Eesti keskmine) tagasiside raport</h2>
% else:
<h2>Õpetaja tagasiside raport</h2>
% endif
<div style="max-width:900px">
% if not c.is_pdf:
  <div style="float:right">
  % if c.level_NG or c.level_YG:
  ${h.checkbox1('kompakt', 1, checked=c.tts and c.tts.kompaktvaade, label=_("Kompaktne vaade"), ronly=False)}
  % endif
  ${h.checkbox1('nullita', 1, checked=c.nullita, label=_("Peida read, kus õpilaste arv on 0"), ronly=False)}
  <br/>
  </div>
% endif
<table class="table table-borderless table-striped items-tbl ${c.tts and c.tts.kompaktvaade and 'compact' or ''}" style="clear:both;" width="100%" >
  <% cnt = 1 + (c.level_NG and 1 or 0) + (c.level_YG and 1 or 0) %>
  % if c.level_NG:
  <col width="225px"/>
  % endif
  % if c.level_YG:
  <col width="225px"/>
  % endif
  <col/>
  <col width="20px"/>
  <thead>
    <tr>
      % if c.level_YG or c.level_NG:
      ${h.th(_("Grupp"), colspan=c.level_YG and c.level_NG and 2 or 1)}      
      % endif
      ${h.th(_("Tagasiside"))}
      ${h.th(_("Õpilaste arv"))}
      % if c.tts and c.tts.ts_sugu:
      ${h.th(_("Poisid"))}
      ${h.th(_("Tüdrukud"))}
      % endif
    </tr>
  </thead>
  ${self.display_items_tbl(c.items_tbl)}
</table>

% endif

<script>
  <% c.init_kompakt = c.tts and c.tts.kompaktvaade %>      
  <%include file="tulemused.diag2.js"/>
</script>
</div>

<%def name="display_items_tbl(items)">
% for ylgrupp_id, yg_rowcnt, yg_items in items:
<%
  if c.level_YG and ylgrupp_id:
     ylgrupp = model.Ylesandegrupp.get(ylgrupp_id)
     ylgrupp_nimi = ylgrupp.tran(c.lang).nimi or ''
  else:
     ylgrupp_nimi = ''
%>
<tbody>
% for ind1, (nsgrupp_id, ng_rowcnt, ng_items) in enumerate(yg_items):
<%
  if c.level_NG and nsgrupp_id:
     nsgrupp = model.Nsgrupp.get(nsgrupp_id)
     nsgrupp_nimi = nsgrupp.tran(c.lang).nimi or ''
  else:
     nsgrupp_nimi = ''
%>
% for ind2, r in enumerate(ng_items):
<%
  ylgrupp_id, nsgrupp_id, np, tagasiside, cnt, cnt_m, cnt_n, sooritajad = r
%>
<tr class="compact-row">
  % if c.level_YG:
  % if ind1 == 0 and ind2 == 0:
  <td grupp_id="yg-${ylgrupp_id}" ${not c.level_NG and 'class="compactlink"' or ''} rowspan="${yg_rowcnt}">${ylgrupp_nimi}</td>
  % else:
  <td grupp_id="yg-${ylgrupp_id}" ${not c.level_NG and 'class="compactlink"' or ''} style="display:none">${ylgrupp_nimi}</td>
  % endif
  % endif
  % if c.level_NG:
  % if ind2 == 0:
  <td grupp_id="yg-${ylgrupp_id}-ng-${nsgrupp_id}" class="compactlink" rowspan="${ng_rowcnt}">${nsgrupp_nimi}</td>
  % else:
  <td grupp_id="yg-${ylgrupp_id}-ng-${nsgrupp_id}" class="compactlink" style="display:none">${nsgrupp_nimi}</td>
  % endif
  % endif  
  <td class="compact-data"><div class="data-wrapper">${tagasiside}</div></td>
  <td class="compact-data">
    <div class="data-wrapper">
      % if cnt and not c.is_pdf and not (c.stat_valimis or c.stat_riiklik):
      <div class="t_sooritajad_cnt">
        <% bubble_id = f"bbl_{ylgrupp_id or 0}_{ind1}_{ind2}" %>
        ${h.link_to_bubble(cnt, None, bubble_id=bubble_id)}
      </div>
      <div id="${bubble_id}" style="display:none">
        ${self.display_sooritajad(sooritajad, np)}
      </div>
      % elif not cnt:
      <div class="nulliga">${cnt}</div>
      % else:
      <div>
        ${cnt}
        % if c.cnt_tehtud and (c.stat_valimis or c.stat_riiklik):
        (${h.fstr(cnt*100/c.cnt_tehtud,0)}%)
        % endif
      </div>
      % endif
    </div>
  </td>
  % if c.tts and c.tts.ts_sugu:
  <td class="compact-data">
    <div class="data-wrapper">${cnt_m}
        % if c.cnt_tehtud and (c.stat_valimis or c.stat_riiklik):
        (${h.fstr(cnt_m*100/c.cnt_tehtud,0)}%)
        % endif      
    </div>
  </td>
  <td class="compact-data">
    <div class="data-wrapper">${cnt_n}
        % if c.cnt_tehtud and (c.stat_valimis or c.stat_riiklik):
        (${h.fstr(cnt_n*100/c.cnt_tehtud,0)}%)
      % endif
    </div>
  </td>  
  % endif
</tr>
% endfor
% endfor
</tbody>
% endfor
</%def>

<%def name="display_sooritajad(sooritajad, np)">
% for r in sooritajad:
<%
    eesnimi, perenimi, j_id, tos_id, tkord_id, kursus = r[:6]
    nimi = '%s %s' % (eesnimi, perenimi)
    if c.ekk_preview_rnd or not request.is_ext() or c.test.salastatud:
       url = None
    elif c.app_eis and c.controller == 'tagasiside': # Testid > Test > Tulemused
       url = h.url('test_tagasiside', test_id=c.test.id, testiruum_id=c.testiruum_id or 0, id=j_id)
    elif c.app_eis and tkord_id and c.controller == 'koolis': # Tsentraalsed testid > Tulemused (vana)
       if c.ylesanded_avaldet: 
          url = h.url('koolitulemused', id=tos_id, test_id=c.test.id, klass_id=c.klass_id or '0')
       else:
          url = h.url('koolitulemused_diagtulemus', kord_id=tkord_id, klass_id=c.klass_id or '0', id=j_id)
    elif c.app_eis and tkord_id: # Tsentraalsed testid > Tulemused
       url = h.url('ktulemused_opilasetulemus', test_id=c.test.id, testimiskord_id=tkord_id, kursus=kursus or '', id=j_id)
    elif c.app_ekk:
       # tagasiside eelvaade EKK vaates
       url = None
    else:
       url = h.url('test_labiviimine_sooritus', test_id=c.test.id, testiruum_id=c.testiruum_id or 0, id=tos_id)
  %>
  % if url:
  ${h.link_to(nimi, url)}
  % else:
  ${nimi}
  % endif
  <br/>
% endfor
</%def>
