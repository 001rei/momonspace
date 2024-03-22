$(document).ready(function() {
    $('#progressForm').submit(function(event) {
        event.preventDefault();
        
        var formData = $(this).serialize();
        
        $.ajax({
            type: 'POST',
            url: '/progress',
            data: formData,
            success: function(response) {
                console.log(response); 
                updateTable(); 
            },
            error: function(xhr, status, error) {
                console.error(xhr.responseText);
            }
        });
    });

    function updateTable() {
        $.ajax({
            type: 'GET',
            url: '/progress',
            success: function(response) {
                var newContent = $(response).find('.table-wrapper-scroll-y tbody').html();
                $('.table-wrapper-scroll-y tbody').fadeOut('fast', function() {
                    $(this).html(newContent).fadeIn('fast');
                });
            },
            error: function(xhr, status, error) {
                console.error(xhr.responseText);
            }
        });
    }
});