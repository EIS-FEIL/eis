## Testimiskorrata õpipädevustesti tulemused grupi kohta
<%inherit file="/common/formpage.mako"/>
<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

<%def name="page_title()">
${c.test.nimi or ''} | ${_("Hindamine")}
</%def>      
<%def name="breadcrumbs()">
##${h.crumb(_('Testid'), h.url('testid'))} 
${h.crumb(c.test.nimi or _('Test'))} 
${h.crumb(_('Hindamine'))}
</%def>

% if len(c.sooritused) > 0:
% if c.tagasiside_html:
% if c.nk_keeled and len(c.nk_keeled) > 1:
${self.lang_sel(c.test.lang, c.nk_keeled)}
% endif
${c.tagasiside_html}
<div style="text-align:right;">
  ${h.btn_to(_("PDF"), h.url_current('index', format='pdf', lang=c.lang))}
</div>
% endif
<br/>
${self.tbl_sooritajad()}
% endif

<%def name="tbl_sooritajad()">
<table class="table table-borderless table-striped tablesorter" width="100%" >
  <caption>${_("Sooritajad")}</caption>
  <thead>
    <tr>
      ${h.th(_('Sooritaja'))}
      ${h.th(_('Profiilileht'), sorter='false')}
    </tr>
  </thead>
  <tbody>
    % for rcd in c.sooritused:
    <% 
       tos, eesnimi, perenimi = rcd
       hkogumid = [hk for hk in tos.testiosa.hindamiskogumid if hk.staatus]
    %>
    <tr>
      <td>
        <!--${perenimi},${eesnimi}-->
        % if len(hkogumid) == 1:
        ${h.link_to(u'%s %s' % (eesnimi, perenimi),
        h.url('test_hindamine', test_id=c.test_id, testiruum_id=c.testiruum_id, hindamiskogum_id=hkogumid[0].id, id=tos.id))}
        % else:
        ${eesnimi} ${perenimi}
        % for hk in hkogumid:
        ${h.link_to(hk.nimi or hk.tahis,
        h.url('test_hindamine', test_id=c.test_id, testiruum_id=c.testiruum_id, hindamiskogum_id=hk.id, id=tos.id))}
        % endfor
        % endif
      </td>
      <td>
      % if len(tos.testiosa.normipunktid):
        ${h.link_to(_("Profiilileht"), h.url('testid_profiilileht_format', id=tos.id, test_id=c.test_id, testiruum_id=c.testiruum_id, format='pdf'))}
      % endif
      </td>
    </tr>
    % endfor
  </tbody>
</table>
</%def>

<%def name="lang_sel(pohikeel, keeled)">
<div align="right" width="100%" class="brown">
  % if len(keeled) == 1:
    ${model.Klrida.get_str('SOORKEEL', pohikeel)}
  % else:
    % for lang in keeled:
      % if lang == pohikeel:
       ${h.radio('lang', lang, checked=not(c.lang) or c.lang==lang, ronly=False, class_="nosave")}
       ${model.Klrida.get_str('SOORKEEL', lang)}
      % else:
       ${h.radio('lang', lang, checkedif=c.lang, ronly=False, class_="nosave")}
       ${model.Klrida.get_str('SOORKEEL', lang)}
      % endif
    % endfor
    <script>
    $(document).ready(function(){
    $('input[name=lang]').click(function(){
    var lang = $(this).val();
    var url = "${h.url_current(lang='__LANG__')}".replace("__LANG__", lang);
    window.location.replace(url);
    dirty = false;
    });
    });
    </script>
  % endif
</div>
</%def>
