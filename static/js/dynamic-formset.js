function updateElementIndex(el, prefix, ndx) {
  var id_regex = new RegExp('(' + prefix + '-\\d+)');
  var replacement = prefix + '-' + ndx;
  if ($(el).attr("for"))
        $(el).attr("for", $(el).attr("for").replace(id_regex, replacement));
  if (el.id)
        el.id = el.id.replace(id_regex, replacement);
  if (el.name)
        el.name = el.name.replace(id_regex, replacement);
  if ($(el).attr('class'))
        $(el).attr('class', $(el).attr('class').replace(id_regex, replacement));
  if ($(el).children().length > 0) {
  $(el).children().each(function() {
	updateElementIndex(this, prefix, ndx);
	//if(!$(this).is($('select'))){
	//$(this).val('');
	//}
  });
  }
}

function addForm(btn, prefix) {
  var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
  var last_div = $(btn).parent().prev('.dynamic-formset');
  var row = last_div.clone().get(0);
  row.id = prefix + '-' + formCount + '-row';
  $(row).children().each(function() {
	updateElementIndex(this, prefix, formCount);
	if(!$(this).is($('select'))){
	$(this).val('');
	}
  });
  $(row).insertAfter(last_div).children('.hidden').removeClass('hidden');
  $(row).find('.delete-row').click(function() {
	deleteForm(this, prefix);
  });
  $('#id_' + prefix + '-TOTAL_FORMS').val(formCount + 1);
  return (formCount);
}

function deleteForm(btn, prefix) {
  var formCount = parseInt($('#id_' + prefix + '-TOTAL_FORMS').val());
  var forms = $(btn).parents('.dynamic-formset').siblings('.dynamic-formset');
  $(btn).parents('.dynamic-formset').remove();
  $('#id_' + prefix + '-TOTAL_FORMS').val(forms.length);
  for (var i=0, formount=forms.length; i<forms.length; ++i) {
	forms.get(i).id = prefix + '-' + i + '-row';
        $(forms.get(i)).children().each(function() {
         updateElementIndex(this, prefix, i);
        });
  }
  return false;
}
