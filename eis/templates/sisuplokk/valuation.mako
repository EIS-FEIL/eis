## kysimuste hindamine
## kutsub *.esitlus.mako
<%
  kysimused = []
  for k in c.block.kysimused:
     t = k.tulemus
     if t:
         kysimused.append(k)
%>
% if c.block.tyyp == const.INTER_INL_TEXT:
  % for kysimus in kysimused:
  ${self.div_kysimused([kysimus])}
  % endfor
% else:
  ${self.div_kysimused(kysimused)}
% endif

<%def name="div_kysimused(kysimused)">
% if kysimused:
<div class="hinded" id="b${c.block.id}q${kysimused[0].id}" 
     data-name="b${c.block.id}k${kysimused[0].kood}">
## Hindajale ei kuva arvutihinnatavaid kysimusi (ES-1748)
## Eksperdi vaates aspektidega ylesandes kuvatakse ainult arvutihinnatavad kysimused
## Eksperdi vaates aspektideta ylesandes kuvatakse kõik kysimused
% if not c.on_kriteeriumid and not (c.on_aspektid and not c.eksperdivaade):
<%
  if not c.eksperdivaade:
     t_kysimused = [k for k in kysimused if not k.tulemus.arvutihinnatav]
  elif c.on_aspektid:
     t_kysimused = [k for k in kysimused if k.tulemus.arvutihinnatav]
  else:
     t_kysimused = kysimused
%>

% if t_kysimused:
  ${self.tbl_kysimused(t_kysimused)}
% endif
% endif

## teatud tyypi sisuplokkidel kuvame siin ka õige vastuse
<% len_k = len(kysimused) %>
% for kysimus in kysimused:
    % if c.block.tyyp in (const.INTER_TEXT, const.INTER_EXT_TEXT, const.INTER_INL_TEXT, const.INTER_MATH):
    <%
       # lahendaja vastused
       vastused = []
       if c.block.tyyp == const.INTER_INL_TEXT and len_k > 1:
          kv = c.responses.get(kysimus.kood)
          if kv:
              vastused = [ks.sisu for ks in kv.kvsisud]

       # õiged vastused
       cvastused = []
       kv = c.correct_responses.get(kysimus.kood)
       if kv:
          cvastused = [ks.sisu for ks in kv.kvsisud]
    %>
      % if c.block.tyyp == const.INTER_EXT_TEXT and kysimus.hindaja_markused:
      ${self.kysimus_mcomment(kysimus, cvastused)}
      % endif
    ${self.kysimus_correct(kysimus, cvastused, vastused)}
    % elif c.block.tyyp in (const.INTER_DRAW, const.INTER_AUDIO, const.INTER_UPLOAD, const.INTER_GEOGEBRA, const.INTER_DESMOS, const.INTER_KRATT):
    ${self.kysimus_correct(kysimus, [], [])}  

    % endif
% endfor
</div>
<br/>
% endif
</%def>

<%def name="kysimus_mcomment(kysimus, vastused)">
<%
  hindamine = c.hindamine
  if c.on_hindamine and not c.hindamine and c.give_hindamine and c.hindamiskogum:
     # yhe ylesande kaupa korraga mitme sooritaja hindamine (omaylesanded.py)
     hindamine = c.give_hindamine(c.sooritus, c.hindamiskogum)
%>
% if hindamine:
<span id="is_mcommentable_k${kysimus.id}" class="is_mcommentable" data-h_id="${hindamine.id}" data-author="${c.user.eesnimi} ${c.user.perenimi}"></span>
% endif
</%def>

<%def name="tbl_kysimused(kysimused)">
## kysimuste hindamine
<% td_qcode = len(kysimused) > 1 %>
  <table class="table hinded">
    <caption>
      % if td_qcode:
      ${_("Küsimuste vastuste hindamine")}
      % else:
      ${_("Küsimuse {s} vastuse hindamine").format(s=kysimused[0].kood)}
      % endif
    </caption>
    <thead>
    <tr>
      % if td_qcode:
      <th>${_("Küsimus")}</th>
      % endif
      % if c.eksperdivaade:
      <th>${_("Liik")}</th>
      <th>${_("Hindaja")}</th>
      % endif
      <th>${_("Toorpunktid")}</th>
      <th nowrap>${_("Max")}</th>
      % if c.eksperdivaade:
      <th nowrap>${_("Koefitsient")}</th>
      % endif
% if c.testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP) or c.test.aine_kood in c.opt.nullipained:
      <th nowrap>${_("Null punkti põhjus")}</th>
% endif      
    </tr>
    </thead>
    <tbody>
    % for kysimus in kysimused:
    <%
       max_vastus = kysimus.max_vastus or 1
       sisestus = 1
       tulemus = kysimus.tulemus
       k_prefix = None
       ## c.q_counter=='' on siis, kui on ty.arvutihinnatav
       ## (kui seejuures tulemus pole arvutihinnatav, siis on vigane test)

       kv = c.ylesandevastus and c.ylesandevastus.get_kysimusevastus(kysimus.id, sisestus)
       kv_arvutihinnatud = tulemus.arvutihinnatav or kv and kv.arvutihinnatud
       #if not tulemus.arvutihinnatav and c.q_counter != '':
       if not kv_arvutihinnatud and c.q_counter != '':      
          k_prefix = '%s.k-%d' % (c.val_prefix, c.q_counter)
          c.q_counter += 1
       max_pallid = tulemus.get_max_pallid()
       if max_pallid is None:
          max_pallid = c.block.ylesanne.max_pallid
    %>
    <!--k=${kysimus.id} kv=${kv and kv.id}-->
    % if kv_arvutihinnatud:
      ${self.kysimus_arvuti(kysimus, tulemus, kv, max_pallid, td_qcode)}
    % elif c.eksperdivaade and k_prefix:
      ${self.kysimus_expert(kysimus, tulemus, kv, max_pallid, td_qcode, k_prefix)}
    % elif k_prefix:
      ${self.kysimus_hindaja(kysimus, tulemus, kv, max_pallid, td_qcode, k_prefix)}
    % endif
    % endfor
    </tbody>
  </table>
</%def>

<%def name="kysimus_arvuti(kysimus, tulemus, kv, max_pallid, td_qcode)">
## arvutihinnatav kysimus
<tr>
      % if td_qcode:
      <td>
        ${h.qcode(kysimus, ah=True)}<!--kv${kv and kv.id} -->
      </td>
      % endif
      % if c.eksperdivaade:
      <td>${_("Automaat")}</td>
      <td>${_("Arvuti")}</td>
      % endif
      <td><span>${h.fstr(kv and kv.toorpunktid)}</span></td>
      <td class="fh"><span>${h.fstr(max_pallid)}</span></td>
      % if c.eksperdivaade:
      <td class="fh">${h.fstr(c.vy.koefitsient)}</td>
      % endif
##      <td colspan="2"></td>
    </tr>
</%def>

<%def name="kysimus_hindaja(kysimus, tulemus, kv, max_pallid, td_qcode, k_prefix)">
## Tavalise hindaja jaoks 
## kysimuste hindamise väljad sisuploki all
## iga kysimuse kohta on yks rida
## kui on arvutihinnatav kysimus, siis kuvatakse arvuti hinnatud toorpunktid
## (kysimusevastus.toorpunktid)
## kui on käsitsi hinnatav kysimus, siis kuvatakse käsitsi toorpunktide
## sisestamise väli (kysimusehinne.toorpunktid)
 <%
   khinne = kv and c.yhinne and c.yhinne.get_kysimusehinne(kv) or None
 %>
    <tr>
      % if td_qcode:
      <td>
        ${h.qcode(kysimus, ah=True)}
      </td>
      % endif
      <td>
        % if tulemus.arvutihinnatav or c.q_counter == '':
           <span class="val-tp">${h.fstr(kv and kv.toorpunktid)}</span>
        % else:
           ${h.float5('%s.toorpunktid' % (k_prefix), 
                      khinne and khinne.toorpunktid, 
                      maxvalue=max_pallid, data_pintervall=tulemus.pintervall, class_='val-tp')}
           ${h.hidden('%s.k_id' % k_prefix, kysimus.id)}
        % endif
        <!--k${kysimus.id} kv${kv and kv.id} kh${khinne and khinne.id} -->         
      </td>
      <td class="fh">${h.fstr(max_pallid)}</td>
      % if c.eksperdivaade:
      <td>${h.fstr(c.vy.koefitsient)}</td>
      % endif
% if c.testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP) or c.test.aine_kood in c.opt.nullipained:
      <td>
        % if not tulemus.arvutihinnatav and c.q_counter != '':
         <%
           bit = c.testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP) and const.NULLIP_BIT_P or const.NULLIP_BIT_E
           defval = khinne and khinne.nullipohj_kood
           opt_nullipohj = c.opt.klread_kood('NULLIPOHJ', empty=True, vaikimisi=defval, bit=bit)
         %>

        ${h.select('%s.nullipohj_kood' % k_prefix,
         khinne and khinne.nullipohj_kood, 
         opt_nullipohj, wide=True,
         disabled=not khinne or not khinne.toorpunktid==0)}

        % endif
      </td>
% endif      
    </tr>
</%def>

<%def name="kysimus_expert(kysimus, tulemus, kv, max_pallid, td_qcode, k_prefix)">
## Eksperthindaja jaoks (kuvatakse ka kõik tehtud hindamised)
## kysimuste hindamise väljad sisuploki all
## iga kysimuse kohta on yks rida
## kui on arvutihinnatav kysimus, siis kuvatakse arvuti hinnatud toorpunktid
## (kysimusevastus.toorpunktid)
## kui on käsitsi hinnatav kysimus, siis kuvatakse käsitsi toorpunktide
## sisestamise väli (kysimusehinne.toorpunktid)

% for (hindamine, yhinne) in c.yhindamised:
    <%
       kasutaja = hindamine.hindaja_kasutaja
       khinne = kv and yhinne and yhinne.get_kysimusehinne(kv) or None
    %>
    <tr>
      % if td_qcode:
      <td>
        ${h.qcode(kysimus, ah=True)}<!--kv${kv and kv.id}-->
      </td>
      % endif
      <td>${hindamine.liik_nimi}</td>
      <td>
         ${kasutaja and kasutaja.nimi} 
         ${h.str_from_datetime(yhinne and yhinne.modified)}
         % if hindamine.staatus != const.H_STAATUS_HINNATUD:
         (${hindamine.staatus_nimi.lower()})
         % endif
      </td>       
      <td>
        ${h.fstr(khinne and khinne.toorpunktid)}
        <!--k${kysimus.id} kv${kv and kv.id} kh${khinne and khinne.id} -->        
      </td>
      <td class="fh">${h.fstr(max_pallid)}</td>
      % if c.eksperdivaade:
      <td class="fh">${h.fstr(c.vy.koefitsient)}</td>
      % endif
      % if c.testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP) or c.test.aine_kood in c.opt.nullipained:
      <td>
        ${h.fstr(khinne and khinne.nullipohj_nimi)}
      </td>
      % endif
    </tr>
% endfor

## kehtiv tulemus
% if kv and kv.toorpunktid is not None:
    <tr>
      % if td_qcode:
      <td>
        ${h.qcode(kysimus, ah=True)}
      </td>
      % endif
      <td colspan="2"><b>${_("Kehtiv tulemus")}</b></td>
      <td>
        ${h.fstr(kv.toorpunktid)}
      </td>
      <td class="fh">${h.fstr(max_pallid)}</td>
      % if c.eksperdivaade:      
      <td class="fh">${h.fstr(c.vy.koefitsient)}</td>
      % endif
      <td></td>
    </tr>
% endif

% if c.hindamine and c.q_counter != '' and (c.olen_ekspert or c.ettepanek or c.olen_hindaja6):
## minu eksperthindamine IV hindamisena
## või vaide korral hindamise ettepanek 
     <%
        kasutaja = c.user.get_kasutaja()
        khinne = kv and c.yhinne and c.yhinne.get_kysimusehinne(kv) or None
     %>
    <tr>
      % if td_qcode:
      <td>
        ${h.qcode(kysimus, ah=True)}
      </td>
      % endif
       <td>${c.hindamine.liik_nimi} </td>
       <td>
         ${kasutaja.nimi} 
         ${h.str_from_datetime(c.yhinne and c.yhinne.modified)}
       </td>
       <td>            
         ${h.float5('%s.toorpunktid' % (k_prefix), 
                   khinne and khinne.toorpunktid, class_="val-tp",
                   maxvalue=max_pallid)}
         ${h.hidden('%s.k_id' % k_prefix, kysimus.id)}
       </td>
       <td class="fh">${h.fstr(max_pallid)}</td>
      % if c.eksperdivaade:
      <td class="fh">${h.fstr(c.vy.koefitsient)}</td>
      % endif
       % if c.testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP) or c.test.aine_kood in c.opt.nullipained:
       <td>
         <%
           bit = c.testiosa.vastvorm_kood in (const.VASTVORM_KP, const.VASTVORM_SP) and const.NULLIP_BIT_P or const.NULLIP_BIT_E
           defval = khinne and khinne.nullipohj_kood
           opt_nullipohj = c.opt.klread_kood('NULLIPOHJ', empty=True, vaikimisi=defval, bit=bit)
         %>
         ${h.select('%s.nullipohj_kood' % k_prefix,
         khinne and khinne.nullipohj_kood, 
         opt_nullipohj, wide=True,
         disabled=not khinne or not khinne.toorpunktid==0)}
       </td>
       % endif
     </tr>
% endif
</%def>

<%def name="kysimus_correct(kysimus, cvastused, vastused)">
## kysimuse õige vastuse kuvamine hindajale hindamistabeli all
<%
   tulemus = kysimus.tulemus
   naidisvastus = tulemus and tulemus.tran(c.lang).naidisvastus
%>
% if vastused or cvastused:
<table width="100%" class="correct-response mb-2">
  <col width="160px"/>
  % for r in vastused:
  <tr>
    <td>${_("Lahendaja vastus")}</td>
    <td class="fb">
      % if tulemus and tulemus.baastyyp == const.BASETYPE_MATH:
      <div class="math-view">
        ${r}
      </div>
      % else:
      ${r}
      % endif
    </td>
  </tr>
  % endfor
  
  % for r in cvastused:
  <tr>
    <td>${_("Õige vastus")}</td>
    <td class="fc">
      % if tulemus and tulemus.baastyyp == const.BASETYPE_MATH:
      <div class="math-view">
        ${r}
      </div>
      % else:
      ${r}
      % endif
    </td>
  </tr>
  % endfor
</table>
% endif
</%def>
