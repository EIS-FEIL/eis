<%inherit file="/common/formpage.mako"/>
<%def name="page_title()">
${_("Testi korraldamine")} | ${c.toimumisaeg.testimiskord.test.nimi} ${h.str_from_date(c.toimumisaeg.alates)}
</%def>      
<%def name="breadcrumbs()">
${h.crumb(_("Korraldamine"), h.url('korraldamised'))} 
${h.crumb('%s %s' % (c.toimumisaeg.testimiskord.test.nimi, h.str_from_date(c.toimumisaeg.alates)))} 
${h.crumb(_("Konsultatsiooninimekirjad"),h.url_current())}
</%def>
<%def name="active_menu()">
<% c.menu1 = 'korraldamised' %>
</%def>

<%def name="draw_before_tabs()">
<%include file="before_tabs.mako"/>
</%def>

<%def name="draw_tabs()">
<%include file="tabs.mako"/>
</%def>

${h.form_search(url=h.url('korraldamine_konsultatsiooninimekirjad', toimumisaeg_id=c.toimumisaeg.id))}
<table width="100%"  class="field">
  <tr>
    <td class="field_body">
      <table width="100%"  class="search2">
        <tr>
          <td class="fh" width="85">${_("Piirkond")}</td>
          <td>
            <%
               c.piirkond_id = c.piirkond_id
               c.piirkond_field = 'piirkond_id'
            %>
            <%include file="/admin/piirkonnavalik.mako"/>
          </td>
          <td class="field_body">
            ${h.btn_search()}        
          </td>
        </tr>
      </table>
    </td>
  </tr>
  <tr>
    <td class="field_body">
      <table width="100%" >
        <col width="300px"/>
        <col/>
        ${self.tr_check(_("Konsultatsiooni läbiviimise protokoll"),
        'konsprotokoll', checked=c.konsprotokoll)}
        ${self.tr_check(_("Konsultatsiooninimekiri"), 
        'konsnimekiri', checked=c.konsnimekiri)}
        <tr>
          <td colspan="2">
            ${h.submit(_("Loo väljatrüki fail"), id='materjal')}
          </td>
        </tr>
      </table>
      
    </td>
  </tr>
</table>
${h.end_form()}
<p>
% if c.piirkond_id:
${_("Konsultatsiooniga seotud testides on valitud piirkonnas kokku {n} konsultatsioonisooviga sooritajat.").format(n=c.cnt_total)}
% else:
${_("Konsultatsiooniga seotud testides on kokku {n} konsultatsioonisooviga sooritajat.").format(n=c.cnt_total)}                    
% endif
</p>

<div class="listdiv">
<%include file="konsultatsiooninimekirjad_list.mako"/>
</div>


<script>
    ## kui (nt page reload) korral on lehe laadimisel mõni dok liik valitud juba,
    ## siis teeme ka malli valiku nähtavaks
    $(document).ready(function(){
        $.each($('select[name$="_t"]'), function(n, item){
           var cb = $(item).closest('tr').find('input[type="checkbox"]')[0];
           $(item).closest('div').toggle(cb.checked);
        });

    });
</script>

<%def name="tr_check(title, name, checked)">
<% 
   ttype_name = name
   tname_name = '%s_t' % name
   opt_name = name
%>
        <tr>
          <td nowrap class="fh" valign="top">
            ${h.checkbox(ttype_name,1,label=title,checked=checked,
            onchange="$(this).closest('tr').find('div#opt').toggle(this.checked)")}
          </td>
          <td>
            <div id="opt">
            ${h.select(tname_name, c.pdf_default.get(name), c.pdf_templates.get(opt_name) or [])}
            </div>
          </td>
        </tr>
</%def>
