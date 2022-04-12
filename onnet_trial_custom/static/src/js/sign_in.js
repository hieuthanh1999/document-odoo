odoo.define('onnet_trial_custom.sign_in', function (require) {
'use strict';
    $('.sign-in-custom .input-group-append .btn.btn-secondary').click(function(){
        var x = document.getElementById("password");
        if (x.type === "password") {
            x.type = "text";
        } else {
            x.type = "password";
        }
    });

    $('#redirect_domain').click(function(e) {
        e.preventDefault();
        var dcode = $(this).attr('data-value');
          $.ajax({
            type: 'GET',
            url: dcode,
            success: function(response) {
              window.location = dcode;
            },
            error: function (error) {
                $('#redirect_domain').trigger('click');
            }
          });
    });

     $('.invite-left .send_email').click(function(){
        var values = {};
        var arr_key = [];
        var arr_value = [];
        var val_name = true
        var val_email = true

        let input_name = $("input[name='name']");
        let input_email = $('input[name="email"]');
        input_name.each(function(i) {
            if($(this).val() != ''){
                var check_email = $(this).parents('.row_input').find('input[name="email"]');

                if(check_email.val() == ''){
                    check_email.addClass('is-invalid');
                    $(this).parents('.row_input').find(".error_email").removeClass('d-none');
                    $(this).parents('.row_input').find(".error_email").html('Email is empty!');
                }else{
                    arr_key.push($(this).val())
                    check_email.removeClass('is-invalid');
                    $(this).parents('.row_input').find(".error_email").addClass('d-none');
                }
            }
        });
        input_email.each(function(i) {
             if($(this).val() != ''){
                if(validateEmail($(this).val())){
                    arr_value.push($(this).val())
                    $(this).removeClass('is-invalid');
                    $(this).parents('.form__group').find(".error_email").addClass('d-none');
                    let check_name = $(this).parents('.row_input').find('input[name="name"]');
                    if(check_name.val() == ''){
                        check_name.addClass('is-invalid');
                        $(this).parents('.row_input').find(".error_name").removeClass('d-none');
                        $(this).parents('.row_input').find(".error_name").html('User is empty!');
                    }else{
                        check_name.removeClass('is-invalid');
                        $(this).parents('.row_input').find(".error_name").addClass('d-none');
                    }
                }else{
                    $(this).addClass('is-invalid');
                    $(this).parents('.form__group').find(".error_email").removeClass('d-none');
                    $(this).parents('.form__group').find(".error_email").html('Invalid email');
                }
             }
        });
        input_name.each(function(i) {
            if($(this).hasClass('is-invalid')){
              val_name = false;
                return
            }
        });
        input_email.each(function(i) {
            if($(this).hasClass('is-invalid')){
              val_email = false;
              return
            }
        });

        if(val_email == true && val_name == true){
            jQuery.ajax({
                type: "POST",
                dataType: 'json',
                url:'/send_email',
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": {'arr_key': arr_key, 'arr_value': arr_value}}),
                success: function (data) {
                        window.location= window.location.origin + '/done-screen/';
                  }
            });
        }
    });

    function validateEmail($email) {
        var emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
        return emailReg.test( $email );
    }
});