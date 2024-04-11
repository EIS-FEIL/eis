## -*- coding: utf-8 -*- 
<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Testi korraldamine")} | ${c.toimumisaeg.testimiskord.test.nimi} ${h.str_from_date(c.toimumisaeg.alates)}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Tsentraalsed testid"))}
${h.crumb(_("Testi läbiviimise korraldamine"), h.url('korraldamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, c.toimumisaeg.tahised))}
${h.crumb(_("Materjalid"), h.url('korraldamine_materjalid', testikoht_id=c.testikoht.id))}
</%def>

<%def name="active_menu()">
<% c.menu1 = 'ekktestid' %>
</%def>

<%def name="draw_before_tabs()">
<h1>${_("Testi läbiviimise korraldamine")}</h1>
</%def>

<%def name="draw_tabs()">
<% c.tab1 = 'materjalid' %>
<%include file="tabs.mako"/>
</%def>

${h.form_save(None, h.url('korraldamine_materjalid',testikoht_id=c.testikoht.id))}

<%
  peidus = c.toimumisaeg.testimiskord.sooritajad_peidus
  on_paketid = c.toimumisaeg.on_paketid
%>
<div class="my-2">
  % if on_paketid:
  ${self.tr_check(_("Saatekirjad"), 'saatekiri', disabled=not c.toimumisaeg.on_hindamisprotokollid)}
  % endif
  ${self.tr_check(_("Testitööde avamise protokoll"), 'avamisprotokoll')}
  ${self.tr_check(_("Testi toimumise protokoll"), 'toimumisprotokoll', disabled=peidus)}
  ${self.tr_check(_("Testitööde üleandmise protokoll"), 'yleandmisprotokoll', disabled=peidus)}
  ${self.tr_check(_("Hindamise protokoll"), 'hindamisprotokoll', disabled=not c.toimumisaeg.on_hindamisprotokollid)}
  ${self.tr_check(_("Testisooritajate nimekiri"), 'nimekiri', disabled=peidus)}
  ${self.tr_check(_("Testisooritajate nimekiri rühmade kaupa"), 'ryhmanimekiri', disabled=peidus)}
</div>
<script>
    $(function(){
        ## kui (nt page reload) korral on lehe laadimisel mõni dok liik valitud juba,
        ## siis teeme ka malli valiku nähtavaks
        $.each($('select[name$="_t"]'), function(n, item){
           var cb = $(item).closest('.row').find('input.tr-check');
           $(item).closest('div').toggle(cb.is(':checked'));
        });
        ## märkeruudu valiku muutmisel peita/kuvada malli valikväli
        $('input.tr-check').change(function(){
           $(this).closest('.row').find('div.opt').toggle(this.checked);
        });
    });
</script>
<div class="py-3">
  ${h.submit(_("Loo väljatrüki fail"))}
</div>
${h.end_form()}

<%def name="tr_check(title, name, disabled=False)">
<% 
   ttype_name = name
   tname_name = '%s_t' % name
   opt_name = name
   md_width = 8
   lg_width = 9
   tmpl_cls = f"col-md-{md_width} col-lg-{lg_width}"
%>
  <div class="form-group row">
    <div class="col-md-4 col-lg-3">
      ${h.checkbox(ttype_name, 1, label=title,
      checked=not disabled and c.__getattr__(ttype_name),
      disabled=disabled,
      class_="tr-check")}
    </div>
    <div class="${tmpl_cls}">
      <div class="opt">
        ${h.select(tname_name, c.__getattr__(tname_name), c.pdf_templates.get(opt_name) or [], disabled=disabled)}
      </div>
    </div>
  </div>
</%def>
