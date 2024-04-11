function grupp_rowspan()
{
  ## grupi veerus jäetakse iga grupi kohta nähtavaks 1 lahter,
  ## mis katab kõik selle grupi read
  $('table.items-tbl td[grupp_id]').each(function(){
     var grupp_id = $(this).attr('grupp_id');
     var elems = $('table.items-tbl tr:visible td[grupp_id="'+grupp_id+'"]');
     elems.hide();
     elems.first().show().attr('rowspan', elems.length);
  });
}

function compact_text_colspan()
{
  ## kui kompaktses vaates teksti veergu ei kuvata, oleks selle asemel oranz taust
  ## et poleks oranzi tausta, teeme grupi nimetuse pikemaks
  $('table.items-tbl:not(.compact)>tbody>tr td.compactlink').attr('colspan', '1');
  $('table.items-tbl.compact>tbody>tr:not(.compact-row) td.compactlink').attr('colspan', '1');      
  $('table.items-tbl.compact>tbody>tr.compact-row td.compactlink').attr('colspan', 5);
}
$(function(){  
    ## Peida read, kus õpilaste arv on 0 - käivitab ridade peitmise    
  $('input#nullita').click(function(){
    $('.items-tbl div.nulliga').closest('tr').toggle();
    grupp_rowspan();
  });
    ## Peida read, kus õpilaste arv on 0 - kui 0-ridu pole, siis pole vaja märkeruutu kuvada
  if($('.items-tbl div.nulliga').length == 0)
    {
        $('input#nullita').closest('label').hide();
    }
  $('input#kompakt').click(function(){
     $('table.items-tbl').toggleClass('compact');
     compact_text_colspan();
  });

  $(document).on('click', '.items-tbl.compact .compactlink', function(){
    var show = !$(this).closest('tr').hasClass('compact-row');
    var grupp_id = $(this).attr('grupp_id');
    ## peidame kõik muud read
    $('table.items-tbl>tbody>tr').addClass('compact-row');
    ## eemaldame rida peitva compact-row klassi kõigilt ridadelt, kus on sama grupiga veerg
    $('table.items-tbl>tbody>tr td[grupp_id="'+grupp_id+'"]').each(function(){
      $(this).closest('tr').toggleClass('compact-row', show);
    });
     compact_text_colspan();
  });

  % if (c.level_NG or c.level_YG) and c.init_kompakt:
  compact_text_colspan();
  % endif
});
