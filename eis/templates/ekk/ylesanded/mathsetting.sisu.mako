<script>
  function set_icon()
  {
% if c.is_edit:
  div = $(this);
  div.toggleClass('active');
  div.find('input[name="icon"]').prop('checked', div.hasClass('active'));
% endif
  }
  $(function(){
    var me = new MathEditor($('#emptymath')[0]);
    var polygon = $('div#polygon');
    me.all_buttons.forEach(function(key){
        var b = me.button_meta[key];
        var icon = polygon.find('.icon-setting[id="' + key + '"]');
        if(icon.length)
        {
           var mview = icon.find('.math-icon');
           mview.text(b.icon);
           MathQuill.getInterface(2).StaticMath(mview[0]);
           icon.attr('title', eis_textjs.matheditor[key.toLowerCase()]);
           icon.click(set_icon);
        }
  });
  });
</script>
% if c.is_edit:
<p>
${_("Vali hiirega klikkides nupud, mis kuvatakse lahendajale")}
</p>
% endif
<div class="border">
  <div style="display:none">
    <div id="emptymath"></div>
  </div>
  <div id="polygon" class="matheditor-wrapper-x">
    <%
      # vt matheditor.js, Nastja: lisatud indint, angle
      all_buttons = ["fraction","square_root","cube_root", "root",'square','superscript','subscript','plus','minus',
      'multiplication','division','plus_minus','minus_plus','percent','approx','equal','not_equal','greater_equal',
      'less_equal','greater_than','less_than','angle','degree','indint','int','intersect','union',
      'emptyset','in','notin',
      'infty','overrightarrow','sin','cos','tan','arcsin','arccos','arctan','comma',
      'absolute','parentheses','par_frac','par_frac_sup','text',
      'alpha','beta','gamma','delta','epsilon','zeta','eta','theta','iota','kappa','lambda','mu','nu',
      'xi','pi','rho','sigma','tau','upsilon','phi','chi','psi','omega', 'Gamma','Delta','Theta','Lambda','Xi','Pi','Sigma','Upsilon','Phi','Psi','Omega']
      selected_icons = c.ylesanne.get_math_icons(c.kysimus and c.kysimus.matriba)
    %>
    % for icon in all_buttons:
    <%
      active = icon in selected_icons
      style = "padding:0;margin:auto;height:38px;text-align:center;"
      if icon in ('fraction', 'square_root','cube_root','root','indint', 'int','absolute','parentheses'):
          style += 'font-size:80%;'
      elif icon in ('par_frac','par_frac_sup'):
          style += 'font-size:60%;'
    %>
    <div class="icon-setting ${active and 'active' or ''}" id="${icon}" style="width:50px;height:43px;">
      <div class="matheditor-btn-span" style="${style}">
        <div class="math-icon"></div>
      </div>
      ${h.checkbox('icon', icon, checked=active, display=False, title=icon)}
    </div>
    % endfor
  </div>
</div>
