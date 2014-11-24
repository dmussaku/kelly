var upload_vcard = (function($) {
    var sel = {
        form: '#file_upload_form',
        gif_loader: '[data-js-upload-vcard="gif_loader"]',
      },
      o = {
        $form: $(sel.form),
        $gif_loader: $(sel.gif_loader),
      },

      upload = function(event) {

        var data = new FormData(o.$form[0]);
        o.$gif_loader.show();
        $.ajax({
          url: o.$form.attr('action'),
          type: o.$form.attr('method'),
          data: data,
          dataType: jsonp,
          crossdomain: true,
          cache: false,
          processData: false,
          contentType: false
        })
          .done(function (data) {
            alert('successfuly added '+data.length+' new contacts');
            o.$gif_loader.remove();
          });
        
        event.preventDefault();
      },
      init = function() {
        $(document).on('submit', sel.form, upload);
      };

  init();

})(jQuery);
