var change_normityyp = function(field)
{
    var block = $(field).closest('.nptable');
    var val = $(field).val();
    ## kas disabled kysimuse valikuväli
    var k_is_disabled = val != '${const.NORMITYYP_VASTUS}' && val != '${const.NORMITYYP_VALEM}' && val != '${const.NORMITYYP_PROTSENT}' && val != '${const.NORMITYYP_PALLID}' && val != '${const.NORMITYYP_PUNKTID}';
    if(k_is_disabled)
        block.find('textarea.kkood,select.kkood1').val('');
    ## kas disabled valem
    block.find('.trvalem').toggle(val == '${const.NORMITYYP_VALEM}');
    block.find('.trpolevalem').toggle(val != '${const.NORMITYYP_VALEM}');
    ch_diag_kood($(field), true);
};
## koodi valimisel kuvatakse või peidetakse valikväli või arvuväli sõltuvalt, kas valiti valiku kood
function ch_diag_kood(fld, set_default_op)
{
    var block = fld.closest('.nptable');
    var tyyp = block.find('.normityyp').val();
    var kood = block.find('.kkood1').val();
    if((tyyp == '${const.NORMITYYP_VASTUS}') && (typeof choices[kood] != 'undefined'))
    {
        // on valikud
        block.find('.tingimus_vaartus').val('').hide();
        block.find('.tingimus_valik').each(function(n, item){
            var choice = $(item);
            var old_value = choice.val();
            choice.find('option').remove();
            for(var i=0; i<choices[kood].length; i++)
            {
                choice.append($('<option/>')
                              .attr('value', choices[kood][i][0])
                              .text(choices[kood][i][1]));                    
            }
            choice.val(old_value);
            choice.show();
        });
    }
    else
    {
        // valikuid pole, kuvame punktide/pallide arvuvälja
        block.find('.tingimus_vaartus').show();
        block.find('.tingimus_valik').val('').hide();
    }
}

var change_alatest = function(fld){
    var tbl = fld.closest('.nptable');
    var ty = tbl.find('select[name$=".testiylesanne_id"]');
    ty.find('option').show();
    if(fld.val())
    {
        ty.find('option:not([name="'+fld.val()+'"])').hide();
        ty.find('option').eq(0).show();
        if(ty.find('option:selected[name!="'+fld.val()+'"]').length)
            ty.val('');
        $('.diag-grupp_id').val('');
    }
};
var change_ty = function(fld){
    var tbl = fld.closest('table');    
    var ala = tbl.find('select[name$=".alatest_id"]');
    var selected = fld.find('option:selected');
    if(selected)
    {
        ala.find('option[value="'+selected.attr('name')+'"]').attr('selected',true);
        //change_alatest(ala);
        $('.diag-grupp_id').val('');    
    }
    update_k(fld);

    ## leiatakse ahelas eespool olevad ylesanded
    var url = "${h.url_current('index')}";
    $.ajax({
        type: 'GET',
        url: url,
        data: 'sub=ahel&ty_id=' + fld.val(),
        success: function(data){
            ch_ahel_yl(data);
        }
    });
};

var update_k = function(fld){
## leiatakse ylesande valikkysimuste koodid
    var tbl = $('table.nptable');
    var ty_id = tbl.find('.testiylesanne_id').val();
    var nptyyp = $('select[name="np.normityyp"]').val();
    var onyl_polevalem = (ty_id != '') && (nptyyp != "${const.NORMITYYP_VALEM}");
    tbl.find('.tronyl-polevalem').toggle(onyl_polevalem);
    tbl.find('.trpoleyl').toggle(!onyl_polevalem);
    if(!onyl_polevalem)
    {
       ## testiylesannet ei ole valitud või on valem, kuvame kysimuse koodi tekstiväljana
      return;
    }
    
    var url = "${h.url_current('index')}";
    var data = 'sub=valik';
    if(ty_id)
        data = data + '&ty_id=' + ty_id;
    if(tbl.find('.alatest_id').length > 0)
        data = data + '&alatest_id=' + tbl.find('.alatest_id').val();
    // kui on ty_id või alatest_id, siis teha päring
    if(data.indexOf('&') > -1)
    $.ajax({
            type: 'GET',
            url: url,
            data: data,
            success: function(data){
                var opt_kood = data.koodid;
                choices = data.valikud;
                var kkood1 = tbl.find('select.kkood1');
                var oldval = kkood1.val();
                kkood1.find('option').slice(1).remove();
                for(var i=0; i<opt_kood.length; i++)
                {
                    var option = $('<option></option>').attr('value', opt_kood[i][0]).text(opt_kood[i][1]);
                    if(opt_kood[i][0] == oldval)
                        option.prop('selected', true);
                    kkood1.append(option);
                }
            }
    });
};
function on_addrow_npts(tableid)
{
    init_ckeditor_tbl('np', tableid, -1, '${request.localizer.locale_name}', '${h.ckeditor_toolbar('basic')}', null, null, 'body16');
}
## ahela veerus kuvame ainult neid ylesandeid, mis on ahelas eespool
## jätkuylesande veerus ainult neid, mis ei ole ahelas eespool
function ch_ahel_yl(data)
{
    var ahelas = data[0].map(String);
    var ahelas0 = data[1].map(String);
## ahela tingimuse väljal kuvame ainult neid ylesandeid, mis on ahelas eespool
    $.each($('.diag-ahel option'),function(){
        var fld = $(this);
        var visible = this.value=='' || ahelas.indexOf(this.value)>-1;
        fld.toggle(visible);
        if(fld.prop('selected') && !visible) fld.prop('selected', false);
    });
## jätkuylesande väljal kuvame ainult neid, mis ei ole ahelas juba olemas ja pole jooksev
    $.each($('.diag-yl option'),function(){
        var fld = $(this);
        var visible = (ahelas.indexOf(this.value)==-1) && (ahelas0.indexOf(this.value)==-1);
        fld.toggle(visible);
        if(fld.prop('selected') && !visible) fld.prop('selected', false);           
    });
}

function reinit_ckeditor()
{
    destroy_old_ckeditor();
    var inputs = $('table.nptagasisided>tbody textarea.editable');
    init_ckeditor(inputs, 'np_ckeditor_top', '${request.localizer.locale_name}', '${h.ckeditor_toolbar('basic')}', null, null, 'body16');
}

$(function(){
    var block = $('div#dialog_div');
    
    ## kysimuse kood kuvada kas tekstiväljana või valikuna sõltuvalt sellest, kas ylesanne on valitud
    var fld = $('select[name="np.normityyp"]')[0];
    change_normityyp(fld);
    update_k(fld);
    
    block.find('select[name$=".normityyp"]').change(function(){
        change_normityyp(this);
        update_k($(this));        
    });
    change_normityyp(block.find('select[name$=".normityyp"]')[0]);
    block.find('select[name$=".alatest_id"]').change(function(){
        change_alatest($(this));
        update_k($(this));
    });
    block.find('select[name$=".testiylesanne_id"]').change(function(){
        change_ty($(this));
    });
    block.find('select[name$=".alatest_id"]').each(function(n, el){
        change_alatest($(el));
    });
    block.find('input.minmax').change(function(){
        var lavi0 = ($(this).val().match(/^([+-]?\d+).*/) || [0,0])[1];
        $('.sryhm0').text(lavi0);
    });    

    block.find('.kkood1').change(function(){
        // valikus kysimuse valimisel kantakse sama väärtus valemi väljale
        var val = $(this).val();
        if(val != '')
        {
            $('.kkood').val(val);
        }
        ch_diag_kood($(this));
    });
    block.find('.diag-grupp_id').change(function(){
        $(this).closest('table').find('.testiylesanne_id').val('');
        var kkood1 = $('.kkood1');
        kkood1.find('option').slice(1).remove();
        ch_diag_kood($(this));
    });    
    ch_diag_kood($('.normityyp'), false);
    ch_ahel_yl(${model.json.dumps(c.ahelas_data)});
    $('table.nptagasisided').on('click', '.ts-up', function(){
        var tr = $(this).closest('tr')[0];
        if(tr.previousElementSibling)
        {
            tr.parentNode.insertBefore(tr, tr.previousElementSibling);
            reinit_ckeditor();
        }
    });
    $('table.nptagasisided').on('click', '.ts-down', function(){
        ##var tr = $(this).closest('tr');
        ##if(tr.next().length) tr.next().insertBefore(tr);
        var tr = $(this).closest('tr')[0];        
        if(tr.nextElementSibling)
        {
            tr.parentNode.insertBefore(tr.nextElementSibling, tr);
            reinit_ckeditor();
        }
    });
    reinit_ckeditor();
    ## eemaldame normipunkti .modal dialoogi tabIndex=-1,
    ## et CKEditori dialoogide (nt tabel) väljadel oleks võimalik saada fookus
    block.removeAttr('tabIndex');

    ## märkeruudust saab valida, kas kuvada statistika tagasiside
    $('input[name="show_stat"]').each(function(){
        if(!this.checked)
            $(this).closest('.col').find('.stat').hide();
    });
    $('input[name="show_stat"]').click(function(){
        $(this).closest('.col').find('.stat').toggle(this.checked);
    });
    
});

