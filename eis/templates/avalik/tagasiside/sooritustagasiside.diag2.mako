<%
    if c.sooritaja:
       test = c.sooritaja.test
       lang = c.sooritaja.lang
    else:
       # eelvaade
       test = c.test
       lang = c.lang
    tts = test.testitagasiside
    cols = c.diag_data and len(c.diag_data[0]) or 0
%>

<table width="100%" class="table" style="max-width:900px"> 
  % if c.diag_data:
  <% cnt = len(c.diag_data[0]) %>
  % if cnt > 1:
  <col width="225px"/>
  % for n in range(1, cnt):
  <col width="${75/(cnt-1)}%"/>
  % endfor
  % endif
  % endif
  % if tts and tts.sissejuhatus_opilasele:
  <tr>
    <td colspan="${cols}" style="padding-top:12px;padding-bottom:12px;" class="body16">
      ${tts.tran(lang).sissejuhatus_opilasele}
    </td>
  </tr>
  % endif
  % for row in c.diag_data:
  <tr>
    % for cell in row:
    % if isinstance(cell, list):
    <td>
      <table width="100%"  class="table">
        % if cell:
        <% cnt = len(cell[0]) %>
        % for n in range(cnt):
        <col width="${100/cnt}%"/>
        % endfor
        % endif

        % for row2 in cell:
        <tr>
          % for cell2 in row2:
          <td style="vertical-align:top; ${cell2.is_cellh and 'background-color:#fafafa"' or ''}" class="body16">${cell2.value}</td>
          % endfor
        </tr>
        % endfor
      </table>
    </td>
    % else:
    <td style="vertical-align:top; ${cell.is_cellh and 'background-color:#fafafa"' or ''}" class="body16">${cell.value}</td>    
    % endif
    % endfor
  </tr>
  % endfor
  % if tts and tts.kokkuvote_opilasele:
  <tr>
    <td colspan="${cols}" style="padding-top:12px;padding-bottom:12px;" class="body16">
      ${tts.tran(lang).kokkuvote_opilasele}
    </td>
  </tr>
  % endif
</table>

