var upload_vcard = (function($) {
    var sel = {
        form: '[data-js-upload-vcard="form"]',
        gif_loader: '[data-js-upload-vcard="gif_loader"]',
      },
      o = {
        $form: $(sel.form),
        $gif_loader: $(sel.gif_loader),
      },

      upload = function(event) {
        var data = new FormData(o.$form);

        o.$gif_loader.show();

        $.ajax({
          url: o.$form.attr('action'),
          type: o.$form.attr('method'),
          data: data,
          cache: false,
          processData: false,
          contentType: false
        })
          .done(function (data) {
            alert('successfuly added'+data.length+' new contacts');
            o.$gif_loader.show();
          });

        event.preventDefault();
      },
      init = function() {
        $(document).on('submit', sel.form, upload);
      };

  init();

})(jQuery);
