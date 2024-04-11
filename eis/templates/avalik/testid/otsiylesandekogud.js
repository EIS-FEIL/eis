function toggle_keeletase_yk()
{
    $('form#yk_search tr.keeletase').toggle($('form#yk_search select#keeletase option').length > 1);
}

$(function(){
    $('form#yk_search select[name="aine"]').change(function(){
        update_options(this, 
                       "${h.url('pub_formatted_valikud', kood='KEELETASE', format='json')}", 
                       'ylem_kood', 
                       $('form#yk_search select#keeletase'),
                       null,
                       null,
                       null,
                       toggle_keeletase_yk);
    });
    toggle_keeletase_yk();   
});
function toggle_add_yk(){   
    var visible = ($('div#listdiv_yk input:checked[name="ylesanne_id"]').length > 0);
    $('div#listdiv_yk span#add').toggleClass('invisible', !visible);
}
$(function(){
  ## ylesande märkeruudu klikkimisel kuvame/peidame salvestamise nupu
    $('div#listdiv_yk').on('click', 'input[name="ylesanne_id"]', toggle_add_yk);
    $('div#listdiv_yk').on('click', 'input[name="all_id"]', function(){
        $(this).closest('table').find('input[name="ylesanne_id"]').prop('checked', this.checked);
        toggle_add_yk();
    });

## ylesandekogu otsingus kogu nimel klikkides kuvame kogu sisu
    $('#listdiv_yk').on('click', '.yk-title', function(){
        var container = $(this).siblings('div.yk-items');
        var glyph = $(this).find('span.glyphicon');
        if(container[0].childElementCount == 0)
        {
            var url = $(this).attr('href');
            console.log('url='+url);
            glyph.removeClass('glyphicon-folder-close').addClass('glyphicon-folder-open');
            dialog_load(url, '', 'GET', container, function(){hold_dlg_height(null, false, $('#listdiv_yk'));});
        }
        else if(glyph.hasClass('glyphicon-folder-open'))
        {
           ## kogu sisu on lahti, paneme kinni
            glyph.removeClass('glyphicon-folder-open').addClass('glyphicon-folder-close');
            container.hide();
        }
        else
        {
           ## kogu sisu on kinni, teeme lahti
            glyph.removeClass('glyphicon-folder-close').addClass('glyphicon-folder-open');
            container.show();
        }
        hold_dlg_height(null, false, $('#listdiv_yk'));
    });

    ## ylesandekogu otsingus kogusisese grupi nimel klikkides kuvame grupi sisu
    $('#listdiv_yk').on('click', '.ykg-title', function(){
        var container = $(this).siblings('div.ykg-items');
        var glyph = $(this).find('span.glyphicon');
        if(glyph.hasClass('glyphicon-triangle-bottom'))
        {
           ## kogu sisu on lahti, paneme kinni
            glyph.removeClass('glyphicon-triangle-bottom').addClass('glyphicon-triangle-right');
            container.hide();
        }
        else
        {
           ## kogu sisu on kinni, teeme lahti
            glyph.removeClass('glyphicon-triangle-right').addClass('glyphicon-triangle-bottom');
            container.show();
            window.setTimeout(function(){hold_dlg_height(null, false, $('#listdiv_yk'));}, 500);
        }
    });
});
