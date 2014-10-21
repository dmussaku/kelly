function click_event(my_url){
  console.log('click_event');
  var myurl = my_url;
  $.get(myurl, function(data){
    var div_class = '.comments';
    $(div_class).html(data);
    return false;
  });
  return false;
}
/*
Script for ajax post of a comment
*/
function comment_submit(){
  console.log($(this));
}


$(document).on('submit', '#comment-form', function() {
  var postData = $(this).serialize();
  var my_url = $(this).attr('url');
  console.log(postData);
  $.ajax({
    type:'POST',
    url: my_url,
    data: postData,
    success: function(data){
      $.get(my_url, function(data){
        var div_class = '.comments';
        $(div_class).html(data).animate({opacity:'show'}, "slow");
        return false;
      });
      console.log('asdas');
    }
  });
  return false;
});


function delete_comment(url,id){
  if (confirm("Are you sure you want to delete that comment?")){
    var csrf = $('#csrf').val();
    $.post(url,
    {
      csrfmiddlewaretoken: csrf,
      id: id
    },
    function(){
      var comment_div = '.comment-'+id;
      $(comment_div).animate({ opacity: 'hide' }, "slow");
    });
  }
}

function edit_form(id){
  var comment_form = $('#add-comment-form');
  $('#add-comment-form').remove();
  var comment_div = '.comment-'+id;
  $(comment_div).html(comment_form.html());
}


$.comments = {
  'click_event': click_event,
  'delete_comment': delete_comment,
  'edit_form': edit_form,
}
