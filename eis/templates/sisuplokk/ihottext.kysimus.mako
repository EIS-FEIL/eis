## -*- coding: utf-8 -*- 
## See mall on kasutusel hottext ja colortext jaoks
<%inherit file="baasplokk.mako"/>
<!-- ${self.name} -->
<%namespace name="choiceutils" file="choiceutils.mako"/>
<%def name="block_edit()">
<% f_toggle_ckeditor = None %>

<span id="gapserror"></span>
${h.hidden('am1.kysimus_id', '')}
${h.hidden('am1.min_pallid', '')}
${h.hidden('am1.max_pallid', '')}

<table width="100%">
  <tr>
    <td class="fh">${_("Küsimuse ID")}</td>
    <td>
      ${h.text('am1.kood', c.kysimus.kood, onkeypress="keypress_identifier(event)", ronly=not c.is_edit and not c.is_tr)}
    </td>
  </tr>
  <tr>
    <td class="fh" nowrap="nowrap">${_("Tekstiosa ID")}</td>
    <td>
      ${h.text('vkood', c.valik.kood, onkeypress="keypress_identifier(event)",
      ronly=not c.is_edit and not c.is_tr)}
    </td>
  </tr>
  <tr>
    <td class="fh">${_("Tekstiosa")}</td>
    <td>
      <% nimi = c.lang and c.valik.tran(c.lang).nimi or c.valik.nimi %>
      ${h.text('vnimi', nimi, onchange="set_desc(this)",
      ronly=not c.is_edit and not c.is_tr)}
    </td>
  </tr>
  % if not c.is_tr:
  <tr>
    <td class="fh">${_("Selgitus")}</td>
    <td>
      ${h.text('vselgitus', c.valik.selgitus, maxlength=255, class_='selgitus')}
    </td>
  </tr>
  % endif
  <tr>
    <td class="fh" colspan="2">
      ${h.checkbox('vuitype', 'checkbox', checked=c.valik.uitype=='checkbox', label=_("Lahendajale kuvatakse märkeruut või raadionupp"), ronly=not c.is_edit and not c.is_tr)}
    </td>
  </tr>
</table>
<p/>
<script>
function set_desc(fld)
{
   var fdesc = $('input.selgitus');
   if(fdesc.val()=='')
   {
     var val = $(fld).val();
     fdesc.val(val.substr(0,255));
   }
}
</script>
</%def>
