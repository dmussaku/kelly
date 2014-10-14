function upload(event) {
      $('#gif-loader').show()
      event.preventDefault();
      var data = new FormData($('form').get(0));
      $.ajax({
          url: $(this).attr('action'),
          type: $(this).attr('method'),
          data: data,
          cache: false,
          processData: false,
          contentType: false,
          success: function(data) {
              alert('successfuly added new contacts');
              $('#gif-loader').hide();
          }
      });
      return false;
      }

      $(function() {
          $('form').submit(upload);
      });