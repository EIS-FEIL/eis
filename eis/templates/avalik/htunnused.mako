## -*- coding: utf-8 -*- 
## Hinnatavad tunnused tagasisidevormil (vormile viidatakse tagasisidevormidelt)
<%inherit file="/common/page.mako"/>
<%def name="page_title()">
${c.aine and c.aine.nimi}
</%def>
% if c.aine and c.klass and c.htunnused:

<h1>${c.aine.nimi}, ${c.klass}. klass</h1>

    % for kood, kirjeldus, kirjeldus_t in c.htunnused:
<p>
  <h2>${kood} - ${kirjeldus}</h2>
  ${kirjeldus_t.replace('\n', '<br/>\n')}
</p>
    % endfor

% endif
