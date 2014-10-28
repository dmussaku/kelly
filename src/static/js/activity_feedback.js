(function($) {
    var sel = {
            showBtn: '[data-js-activity-feedback-visual="show"]',
            showBody: '[data-js-activity-feedback-visual="body"]',
            form: '[data-js-activity-feedback="form"]',
        },
        show = function() {
            var $showLink = $(sel.showBtn),
                show_url = $showLink.prop('href'),
                $showBody = $(sel.showBody);

            if( $showLink.data('isOpen') ) {
                $showBody.hide();
                $showLink.data('isOpen', false);
            } else {
                $.get(show_url, function(data) {
                    $showBody
                        .html(data)
                        .show();

                    $showLink.data('isOpen', true);
                });
            }
        },
        onclick = function(event) {
            show();
            event.preventDefault();
        },
        submit = function(event) {
            var $form = $(event.target);

            $.post($form.prop('action'), $form.serialize())
                .done(function (data, textStatus, xhr) {
                    /*optional stuff to do after success */
                    console.log(data);

                    show();
                });

            event.preventDefault();
        },
        init = function() {
            $(document)
                .on('click', sel.showBtn, onclick)
                .on('submit', sel.form, submit)
        };


    init();

})(jQuery);
