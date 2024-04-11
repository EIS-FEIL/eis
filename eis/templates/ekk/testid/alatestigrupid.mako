<%def name="row_alatestigrupp(item, prefix)">
    <tr>
      <td>
        ${h.posint5('%s.seq' % prefix, item.seq)}
      </td>
      <td>
        ${h.text('%s.nimi' % prefix, item.nimi)}
      </td>
      <td>
        % if c.is_edit:
        ${h.grid_remove()}
        % endif
        ${h.hidden('%s.id' % prefix, item.id)}
      </td>
    </tr>
</%def>
      
<% prefix = 'atg' %>

<table id="tbl_${prefix}" width="100%" border="0" class="table" > 
  <col width="70px"/>
  <col/>
  <col width="50px"/>
  <thead>
    <tr>
      <td>${_("Jrk")}</td>
      <td>${_("Nimi")}</td>
      <td>
      % if c.is_edit:
      ${h.button(_("Lisa"), onclick="grid_addrow('tbl_atg')")}
      % endif
      </td>
    </tr>
  </thead>
  <tbody>
  % if c._arrayindexes != '':
## valideerimisvigade korral
  %   for cnt in c._arrayindexes.get(prefix) or [0]:
        ${self.row_alatestigrupp(c.new_item(),'%s-%s' % (prefix, cnt))}
  %   endfor
  % else:
## tavaline kuva
  %   for cnt,item in enumerate(c.testiosa.alatestigrupid):
        ${self.row_alatestigrupp(item, '%s-%s' % (prefix, cnt))}
  %   endfor
  % endif
  </tbody>
</table>
% if c.is_edit:
<div id="sample_tbl_${prefix}" class="invisible">
<!--
   ${self.row_alatestigrupp(c.new_item(),'%s__cnt__' % prefix)}
-->
</div>
% endif
      
