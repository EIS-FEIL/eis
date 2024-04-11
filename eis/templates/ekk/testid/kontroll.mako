
<%include file="/common/message.mako" />

% if c.test.max_pallid is not None:
${_("Testiga on võimalik saada kokku {p} palli.").format(p=h.fstr(c.test.max_pallid))}<br/>
% else:
${_("Max pallide arv sõltub komplektist")}
% endif
% for r in c.test.testikursused:
% if r.kursus_kood and r.max_pallid is not None:
${_("Kursuse {s} sooritajatel on võimalik saada kokku {p} palli.").format(s=r.kursus_nimi, p=h.fstr(r.max_pallid))}<br/>
% endif
% endfor
% if c.test.yhisosa_max_pallid:
${_("Kursuste ühisosa on {p} palli.").format(p=h.fstr(c.test.yhisosa_max_pallid))}<br/>
% endif

% if len(c.test.testiosad) == 0:
${_("Testil pole ühtki testiosa.")}
<br/>
% else:
  % for testiosa in c.test.testiosad:
   % if len(testiosa.testiylesanded) == 0:
${_("Testiosas {s} pole ühtki testiülesannet.").format(s=testiosa.tahis or '')}
      <br/>
   % else:
      % for alatest in testiosa.alatestid:
         % if len(alatest.testiylesanded) == 0:
           ${_("Alatestis {s} pole ühtki testiülesannet.").format(s=alatest.nimi or '')}
           <br/>         
         % else:
              % for plokk in alatest.testiplokid:
                  % if len(plokk.testiylesanded) == 0:
                    ${_("Testiplokis {s} pole ühtki testiülesannet.").format(s=plokk.nimi or '')})
                  % endif
              % endfor
         % endif
      % endfor
   % endif
  % endfor
% endif

