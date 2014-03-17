/*********************
 * Feature Container *
 *********************/

/* Spoiler feature implementation */
$('.spoiler').on('click', '.spoiler-pre', function(){
  $(this).slideUp();
  $(this).siblings('.spoiler-pre').slideUp();
  $(this).siblings('.spoiler-post').slideDown();
});

function doc_mod_authors() {
  var count = parseInt($('#id_authors-TOTAL_FORMS').val());
  var forms = $('#importAuthors').children('.dynamic-formset');
  for (var i=0; i<count; ++i) {
    forms.get(i).id = 'authors-' + i + '-row';
    $(forms.get(i)).children().each(function() {
      updateElementIndex(this, 'authors', i);
    });
    if ($('#id_authors-' + i + '-id').val() != ''
        || $('#id_authors-' + i + '-author').val() != '') {
      $('#id_authors-' + i + '-sort_value').val('' + (i + 1));
    }
  }
  return true;
}

function doc_toggle_delete(btn) {
  if(!$.fn.bootstrapBtn) {
    var bootstrapButton = $.fn.button.noConflict();
    $.fn.bootstrapBtn = bootstrapButton;
  }
  $(btn).bootstrapBtn('toggle');
  var target = '#' + $(btn).attr('data-for');
  if($(target).attr('value') == "on") {
    $(target).removeAttr('value');
  } else {
    $(target).attr('value', 'on');
  }
}
