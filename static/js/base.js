/*********************
 * Feature Container *
 *********************/

/* Spoiler feature implementation */
$('.spoiler').on('click', '.spoiler-pre', function(){
  $(this).slideUp();
  $(this).siblings('.spoiler-pre').slideUp();
  $(this).siblings('.spoiler-post').slideDown();
});
