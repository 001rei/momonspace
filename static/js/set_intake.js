$(document).ready(function () {
        $('form').submit(function (event) {
            event.preventDefault();

            var programValue = $('input[name="program"]:checked').val();

            $.ajax({
                type: 'POST',
                url: '/set-intake',
                data: {
                    program: programValue
                },
                success: function (response) {
                    console.log('Data berhasil disimpan');
                    update()
                },
                error: function (xhr, status, error) {
                    console.error('Terjadi kesalahan:', error);
                }
            });
        });

        function update() {
        $.ajax({
            type: 'GET',
            url: '/progress',
            success: function(response) {
                var newContent = $(response).find('.intake-info').html();
                $('.intake-info').fadeOut('fast', function() {
                    $(this).html(newContent).fadeIn('fast');
                });
            },
            error: function(xhr, status, error) {
                console.error(xhr.responseText);
            }
        });
    }
});