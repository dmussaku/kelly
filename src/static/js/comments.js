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
        $(div_class).html(data);
        return false;
      });
      console.log('asdas');
    }
  });
  return false;
});

$(document).on('submit', '#comment-delete-form', function() {
  var postData = $(this).serialize();
  var my_url = $(this).attr('url');
  console.log(postData);
  $.ajax({
    type:'POST',
    url: my_url,
    data: postData,
    success: function(data){
      var comment_div = '.comment-'+$('#comment-id').val()
      alert(comment_div);
      $(comment_div).animate({ opacity: 'hide' }, "slow");
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


$.comments = {
  'click_event': click_event,
  'delete_comment': delete_comment,
}
