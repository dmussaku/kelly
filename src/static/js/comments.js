function click_event(my_url){
  console.log(my_url);
  var myurl = my_url;
  $.get(myurl, function(data){
    var div_id = '#comments';
    $(div_id).html('<h3>Comments</h3>'+data);
    return false;
  });
  return false;
}
/*
Script for ajax post of a comment
*/
function add_comment(){
  $('#comment_submit_form').submit(function(e){
      e.preventDefault();
      var postData = $(this).serialize();
      $.ajax({
        type: "POST",
        url: $(this).attr('action'),
        data: postData,
        success: function(data){
          console.log(data);
          $('#new-comment').append("<p>"+data['name']+"</p>");
          $('#new-comment').append("<p>"+data['comment']+"</p>");
          $('#new-comment').append("<p>"+data['date_created']+"</p>");
          return false;
        }
      });
      return false;
  });
}



function delete_comment(obj, id) {
    var comment_div = $('#comment-'+id);
    if (confirm('Are you sure you want to delete this comment')) {
        $.ajax({
          type: "GET",
          url: $(obj).attr('link'),
          success: function(data){
            comment_div.animate({ opacity: 'hide' }, "slow");
          }
        });
    }
}