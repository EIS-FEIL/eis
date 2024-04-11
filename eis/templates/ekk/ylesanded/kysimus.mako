% if c.in_iframe:
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" lang="et">
  ## include pole vajalik, kuna sisu tõstetakse ymber
  <body class="iframe">
    ${self.dlg_contents()}
  </body>
</html>
% else:
${h.not_top()}
${self.dlg_contents()}
% endif

<%def name="dlg_contents()">
<div class="content page" id="${h.page_id(self)}">
  ${h.help_for(h.page_id(self), model)}
  ${self.contents()}
</div>
</%def>

<%def name="contents()">
<% 
c.ylesanne = c.item.ylesanne
if c.lang and c.is_edit:
   # tõlkimise ajal on ainult tõlkeväljad kirjutatavad
   c.is_edit = False
   c.is_tr = True
elif not c.lang and c.is_edit and \
   not c.user.has_permission('ylesanded', const.BT_UPDATE,c.ylesanne):
   # toimetaja tohib ainult tekstivälju kirjutada
   c.is_edit = False
   c.is_tr = True

if c.ylesanne.lukus:
   c.is_edit_hm = c.is_edit and c.can_update_hm
   c.is_edit = False
else:
   c.is_edit_hm = c.is_edit

%>
% if not c.kysimus or not c.kysimus.id and not c.is_edit and c.item.tyyp != const.INTER_CROSSWORD:
${_("Uusi küsimusi lisada ei saa")}
% else:
% if c.item.tyyp == const.INTER_CROSSWORD:
${h.form_save(c.kysimus.id and c.kysimus.kood, form_name='form_dlg', multipart=True, target="form_dlg_target")}
% else:
${h.form_save(c.kysimus.id and c.kysimus.kood, form_name='form_dlg')}
% endif
${h.hidden('lang', c.lang)}
${h.hidden('is_tr', c.is_tr)}
<%include file="/common/message.mako" />
${h.rqexp()}
${c.item.ctrl.edit_kysimus(c.kysimus)}
% if c.updated:
## muudame ckeditori sees
    <script>
% if c.block.tyyp == const.INTER_INL_CHOICE:
      CKEDITOR.plugins.gaps.commands.gapchoice.gap_update();
% elif c.block.tyyp == const.INTER_GAP:
      CKEDITOR.plugins.gaps.commands.gapmatch.gap_update(false);
% elif c.block.tyyp == const.INTER_PUNKT and c.kood2:
      CKEDITOR.plugins.gaps.commands.gapmatch.gap_update(true);
% elif c.block.tyyp == const.INTER_INL_TEXT and c.tulemus.baastyyp == const.BASETYPE_MATH:
      CKEDITOR.plugins.gaps.commands.gapmath.gap_update();
% elif c.block.tyyp == const.INTER_INL_TEXT:
      CKEDITOR.plugins.gaps.commands.gaptext.gap_update();
% elif c.block.tyyp in (const.INTER_HOTTEXT, const.INTER_COLORTEXT):
      CKEDITOR.plugins.gaps.commands.gaphottext.gap_update();
% endif

## kui oleme dialoogis, mitte iframe sees, kus pole jqueryt
if(window.jQuery)
{
% if c.updated_url:
    dirty = false;
    window.location.href = "${c.updated_url}";
% else:
## sulgeme akna
    close_dialog();
% endif
}
    </script>
% endif
    
${h.end_form()}
    <div style="clear:both"></div>
    
% if request.method == 'GET' or c.block.tyyp == const.INTER_CROSSWORD:
    ${h.button(_("Tagasi"), onclick="close_dialog()", level=2)}
    % if c.is_edit_hm and c.block.tyyp == const.INTER_INL_TEXT and c.tulemus.baastyyp == const.BASETYPE_MATH and not c.is_tr:
    ${h.button(_("Kohanda nupuriba"), onclick="toggle_mathsetting(true)", class_="icons-default",
    style="float:right;display:%s;" % (c.kysimus.matriba and 'none' or 'block'), level=2)}
    % endif
    % if c.is_edit_hm or c.is_tr:
    % if c.block.tyyp == const.INTER_CROSSWORD:
    % if c.kysimus.id and c.is_edit:
    ${h.btn_remove(id=c.kysimus.id)}
    % endif
    ${h.button(_("Salvesta"), onclick="$('form#form_dlg').submit();")}
    % elif not (c.is_tr and c.block.tyyp in (const.INTER_GAP, const.INTER_MCHOICE)):
    ${h.ajax_submit_form(value=_("Salvesta"), ckeditor=True)}
    % endif
    % endif
% endif

% if c.block.tyyp == const.INTER_CROSSWORD:
    <div style="float:right">
      ${_("CSS klass")}
      <span class="brown">
        % if c.pos_x != '' and c.pos_y != '':
        cw-gap-${c.pos_y}-${c.pos_x}
        % else:
        cw-gap-${c.kysimus.pos_y}-${c.kysimus.pos_x}
        % endif
      </span>
    </div>

    <iframe name="form_dlg_target" width="0" height="0" onload="if(typeof(move_to_dlg)=='function') move_to_dlg(this)">
    </iframe>
% endif
% endif
</%def>
