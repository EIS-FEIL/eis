## Vajalikud .js ja .css failid
<%
   # min_js - kas kasutada js ja css faile minimeeritud kujul
   min_js = True
   #min_js = False
   if c.is_test and request.params.get('debugsrc'): min_js = False
   c.min_js = min_js or not c.is_devel
   locale_name = request.locale_name
%>
${h.javascript_link('/static/eis/textjs/%s.js' % locale_name, src=not min_js)}

% if c.on_esitlus:
${self.include_esitlus(min_js, locale_name)}
% else:
${self.include_page(min_js, locale_name)}
% endif

## kireva teksti toimeti

% if c.includes.get('ckeditor'):
% if min_js:
  ${h.javascript_link('/static/lib/ckeditor/release/ckeditor/ckeditor.js')}
  <script>CKEDITOR.timestamp='${h.eis.__cktimestamp__}'</script>
% else:  
  ${h.javascript_link('/static/lib/ckeditor/src/ckeditor.js')}
  <script>CKEDITOR.timestamp='${h.eis.__cktimestamp__}${h.rnd()}'</script>
% endif
  ${h.javascript_link('/static/lib/ckeditor/adapters/jquery.js')}
% endif

## mp3 mängija
% if c.includes.get('jplayer'):
  ${h.stylesheet_link('/static/lib/jPlayer-2.9.2/skin/blue.monday/css/jplayer.blue.monday.min.css')}
  ${h.javascript_link('/static/lib/jPlayer-2.9.2/jplayer/jquery.jplayer.min.js')}
% endif
% if c.includes.get('geogebra'):
  <script src="https://www.geogebra.org/apps/deployggb.js"></script>
% endif
% if c.includes.get('desmos'):
  <% desmos_key = request.registry.settings.get('desmos.key') %>
  % if desmos_key:
  <script src="https://www.desmos.com/api/v1.5/calculator.js?apiKey=${desmos_key}"></script>
  % else:
  ${h.request.handler.error(_("Desmos ei ole paigaldatud"))}
  % endif
% endif
% if c.includes.get('wiris'):
  <script type="text/javascript" src="https://www.wiris.net/demo/editor/editor"></script>
  % if min_js:
  ${h.javascript_link('/static/eis/wmath.min.js')}
  % else:
  ${h.javascript_link('/static/eis/source/wmath.js', src=True)}
  % endif
% endif
% if c.includes.get('sortablejs'):
  ${h.javascript_link('/modules/sortablejs/Sortable.min.js')}
## Sortablejs vaja ver 1.10.2, sest ver 1.12 touch lohistamisel ghost on vales kohas
% endif  
% if c.includes.get('spectrum'):
% if min_js:
${h.stylesheet_link('/modules/spectrum-colorpicker/spectrum.min.css')}
${h.javascript_link('/modules/spectrum-colorpicker/spectrum.min.js')}
% else:
${h.stylesheet_link('/modules/spectrum-colorpicker/spectrum.css')}
${h.javascript_link('/modules/spectrum-colorpicker/spectrum.js', src=True)}
% endif
% if locale_name == 'et':
${h.javascript_link('/static/lib/spectrum_i18n/jquery.spectrum-%s.js' % locale_name)}
% endif
% endif

% if c.includes.get('googlecharts'):
  <script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>
  <script type="text/javascript">
  <%
    packages = []
    #mapsApiKey = None
    if c.includes.get('googlecharts.corechart'):
       packages.append('corechart')
    if c.includes.get('googlecharts.geochart'):
       packages.append('geochart')     
    options = {'packages': packages,
               'language': locale_name,
              }
  %>
    google.charts.load('current', ${model.json.dumps(options)})
  </script>
% endif

% if c.includes.get('audiorecorder'):
  % if min_js:
  ${h.javascript_link('/static/lib/web-audio-recorder-app/js/recorder.min.js')}
  % else:
  ${h.javascript_link('/static/lib/web-audio-recorder-app/js/WebAudioRecorder.js', src=True)}
  ${h.javascript_link('/static/lib/web-audio-recorder-app/js/app.js', src=True)}  
  % endif
% endif
  
<%def name="include_page(min_js, locale_name)">
## EISi rakenduse põhiakna stiil
% if not c.includes.get('no_style'):
% if min_js:
  ${h.stylesheet_link('/modules/hds/dist/css/hds-styles.min.css')}
  ${h.stylesheet_link('/static/eis/style.css')}
% else:
  ${h.stylesheet_link('/modules/hds/dist/css/hds-styles.css', src=True)}
  ${h.stylesheet_link('/static/eis/source/style.css', src=True)}
  ${h.stylesheet_link('/static/eis/source/ylesandesisu.css')}
% endif
  ${h.stylesheet_link('/modules/jquery-ui-dist/jquery-ui.min.css')}
  ${h.stylesheet_link('/modules/jquery-ui-dist/jquery-ui.structure.min.css')}
  ${h.stylesheet_link('/modules/jquery-ui-dist/jquery-ui.theme.min.css')}
% endif


## läbivalt vajalik javascript
% if min_js:
  ${h.javascript_link('/modules/jquery/dist/jquery.min.js')}
% else:
  ${h.javascript_link('/modules/jquery/dist/jquery.js')}
% endif

  ${h.javascript_link('/modules/jquery-ui-dist/jquery-ui.min.js')}
<script>$.widget.bridge('uitooltip', $.ui.tooltip);</script>
  ${h.javascript_link('/modules/bootstrap/dist/js/bootstrap.bundle.min.js')}
% if min_js:
  ${h.javascript_link('/static/eis/main.js')}
% else:
  ${h.javascript_link('/static/eis/source/window.js', src=True)}
  ${h.javascript_link('/static/lib/jquery.example.js', src=True)}
  ${h.javascript_link('/static/lib/tablesorter/jquery.tablesorter.js', src=True)}
% endif
  ${h.javascript_link('/modules/jquery-form/dist/jquery.form.min.js')}
% if c.includes.get('math') or c.includes.get('ckeditor'):
${self.include_math(min_js)}
% endif

% if min_js:
${h.stylesheet_link('/modules/select2/dist/css/select2.min.css')}
${h.javascript_link('/modules/select2/dist/js/select2.min.js')}
% else:
${h.stylesheet_link('/modules/select2/dist/css/select2.css')}
${h.javascript_link('/modules/select2/dist/js/select2.js', src=True)}
% endif
${h.javascript_link('/modules/select2/dist/js/i18n/%s.js' % locale_name)}

% if c.includes.get('masonry'):
  ${h.javascript_link('/static/lib/masonry.pkgd.min.js')}
% endif

% if c.includes.get('dropzone'):
% if min_js:
${h.javascript_link('/static/lib/dropzone.min.js')}
% else:
${h.javascript_link('/static/lib/dropzone-5.5.0.js', src=True)}
% endif
<script>
  Dropzone.autoDiscover = false;
</script>
% endif
% if c.includes.get('fancybox') or c.includes.get('test'):
% if min_js:
  ${h.stylesheet_link('/static/lib/fancybox-3.5.7/jquery.fancybox.min.css')}
  ${h.javascript_link('/static/lib/fancybox-3.5.7/jquery.fancybox.min.js')}
% else:
  ${h.stylesheet_link('/static/lib/fancybox-3.5.7/jquery.fancybox.css', src=True)}
  ${h.javascript_link('/static/lib/fancybox-3.5.7/jquery.fancybox.js', src=True)}
% endif
% endif

% if min_js:
${h.stylesheet_link('/modules/flatpickr/dist/flatpickr.min.css')}
${h.javascript_link('/modules/flatpickr/dist/flatpickr.min.js')}
% else:
${h.stylesheet_link('/modules/flatpickr/dist/flatpickr.css')}
${h.javascript_link('/modules/flatpickr/dist/flatpickr.js')}
% endif

% if locale_name != 'en':
${h.javascript_link(f'/modules/flatpickr/dist/l10n/{locale_name}.js')}
% endif

## ylesande koostamine
% if c.includes.get('gapedit') or c.includes.get('igap') or c.includes.get('raphael'):
% if min_js:
  ${h.javascript_link('/static/eis/ylesannemain.js')}
% else:
  ${h.javascript_link('/static/eis/source/igap_edit.js')}
  ${h.javascript_link('/static/lib/raphael-2.3.0/raphael.js', src=True)}
  ${h.javascript_link('/static/lib/jscolor.js', src=False)}
  ${h.javascript_link('/static/eis/source/sketchpad.js')}
  ${h.javascript_link('/static/eis/source/ylesanne.js')}
  ${h.javascript_link('/static/eis/source/media.js')}
% endif
% endif

## testid
% if c.includes.get('test') or c.includes.get('countdown'):
% if min_js:
  ${h.javascript_link('/static/eis/testmain.js')}
% else:
  ${h.javascript_link('/static/eis/source/test.js', src=True)}
% endif
% endif

## soorituspiirkondade puu
% if c.includes.get('jstree'):
  ${h.stylesheet_link('/static/lib/jstree-3.3.7/themes/default/style.min.css')}
  ${h.javascript_link('/static/lib/jstree-3.3.7/jstree.min.js')}
% endif

## digiallkirjastamine
% if c.includes.get('idcard'):
  ${h.javascript_link("/static/eis/idcard/hwcrypto.min.js")}
% if min_js:
  ${h.javascript_link("/static/eis/idcard/startsign.min.js")}
% else:
  ${h.javascript_link("/static/eis/idcard/startsign.js", src=True)}
% endif
% endif

% if c.includes.get('plotly'):
  ${h.javascript_link("/static/lib/plotly-2.6.3.min.js")}
% endif

<!--[if IE & (lt IE 9)]>
<style>
.iew40p {width: 40%;}
</style>
${h.javascript_link('/static/util/iemenu.js')}
<![endif]-->
</%def>

<%def name="include_esitlus(min_js, locale_name)">
% if min_js:
  ${h.stylesheet_link('/modules/hds/dist/css/hds-styles.min.css')}
  ${h.stylesheet_link('/static/eis/style.css')}
% else:
  ${h.stylesheet_link('/modules/hds/dist/css/hds-styles.css', src=True)}
  ${h.stylesheet_link('/static/eis/source/style.css', src=True)}
% endif

## ylesannete iframe stiil
  ${h.stylesheet_link('/modules/jquery-ui-dist/jquery-ui.min.css')}
  ${h.stylesheet_link('/modules/jquery-ui-dist/jquery-ui.structure.min.css')}
  ${h.stylesheet_link('/modules/jquery-ui-dist/jquery-ui.theme.min.css')}
## läbivalt vajalik stiil
% if min_js:
  % if c.disain_ver == const.DISAIN_EIS1:
  ${h.stylesheet_link('/static/eis/ylesanne.eis1.css')}
  % else:
  ${h.stylesheet_link('/static/eis/ylesanne.css')}
  % endif
% else:
  ${h.stylesheet_link('/static/eis/source/ylesanne.css')}
  ${h.stylesheet_link('/static/eis/source/ylesandesisu.css')}
  % if c.disain_ver == const.DISAIN_EIS1:
  ${h.stylesheet_link('/static/eis/source/ylesanne.eis1.css')}
  % else:
  ${h.stylesheet_link('/static/eis/source/ylesanne.hds.css')}
  % endif
% endif


## läbivalt vajalik javascript
% if min_js:
  ${h.javascript_link('/modules/jquery/dist/jquery.min.js')}
% else:
  ${h.javascript_link('/modules/jquery/dist/jquery.js')}
% endif
${h.javascript_link('/modules/jquery-ui-dist/jquery-ui.min.js')}
<script>
  $.widget.bridge('uitooltip', $.ui.tooltip);
  $.widget.bridge('uibutton', $.ui.button);  
</script>
${h.javascript_link('/modules/bootstrap/dist/js/bootstrap.bundle.min.js')}
% if min_js:
  ${h.javascript_link('/static/eis/main.js')}
% else:
  ${h.javascript_link('/static/eis/source/window.js', src=True)}
  ${h.javascript_link('/static/lib/jquery.example.js', src=True)}
  ${h.javascript_link('/static/lib/tablesorter/jquery.tablesorter.js', src=True)}
% endif
${h.javascript_link('/modules/jquery-form/dist/jquery.form.min.js')}
${self.include_math(min_js)}
% if c.includes.get('masonry'):
  ${h.javascript_link('/static/lib/masonry.pkgd.min.js')}
% endif
% if min_js:
  ${h.stylesheet_link('/static/lib/fancybox-3.5.7/jquery.fancybox.min.css')}
  ${h.javascript_link('/static/lib/fancybox-3.5.7/jquery.fancybox.min.js')}
% else:
  ${h.stylesheet_link('/static/lib/fancybox-3.5.7/jquery.fancybox.css', src=True)}
  ${h.javascript_link('/static/lib/fancybox-3.5.7/jquery.fancybox.js', src=True)}
% endif
## ylesanded ja testid
% if min_js:
  ${h.javascript_link('/static/eis/ylesannemain.js')}
% else:
  ${h.javascript_link('/static/eis/source/igap_edit.js', src=True)}
  ${h.javascript_link('/static/eis/source/igap.js', src=True)}
  ${h.javascript_link('/static/lib/raphael-2.3.0/raphael.js', src=True)}
  ${h.javascript_link('/static/lib/jscolor.js', src=False)}
  ${h.javascript_link('/static/eis/source/sketchpad.js', src=True)}
  ${h.javascript_link('/static/eis/source/ylesanne.js', src=True)}
  ${h.javascript_link('/static/eis/source/media.js')}
  ${h.javascript_link('/static/eis/source/rcomment.js', src=True)}
  ${h.javascript_link('/static/eis/source/mcomment.js', src=True)}
  ${h.javascript_link('/static/eis/source/iassociate.js', src=True)}
% endif
% if c.include_responsivevoice:
  ${h.javascript_link("https://code.responsivevoice.org/responsivevoice.js")}
% endif
% if c.includes.get('kratt'):
##% if c.is_test:
  ${h.javascript_link('https://eiskratt-test.edu.ee/eiskratt-frontend/kratiteek.js')}
##% else:
##  ${h.javascript_link('https://eiskratt.edu.ee/eiskratt-frontend/kratiteek.js')}
##% endif
% endif
</%def>

<%def name="include_math(min_js)">
## matemaatika toimeti
% if min_js:
  ${h.stylesheet_link('/static/lib/matheditor/lib/matheditor.min.css')}
  ${h.javascript_link('/static/lib/matheditor/lib/matheditor.min.js')}  
% else:
  ${h.stylesheet_link('/static/lib/matheditor/lib/mathquill.css', src=True)}
  ${h.stylesheet_link('/static/lib/matheditor/lib/matheditor.css', src=True)}
  ${h.javascript_link('/static/lib/matheditor/lib/mathquill.js', src=True)}
  ${h.javascript_link('/static/lib/matheditor/lib/matheditor.js', src=True)}      
% endif
</%def>  
