
$(document).ready(function() {
    $('#show-password').on('click', function() {
        var passwordField = $('#password');
        var passwordFieldType = passwordField.attr('type');
        if (passwordFieldType == 'password') {
            passwordField.attr('type', 'text');
        } else {
            passwordField.attr('type', 'password');
        }
    });
});
