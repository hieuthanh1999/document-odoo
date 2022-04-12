$(document).ready(function () {
  $('#hidden_subscription_modal').hide();
     $(".active_subscription_status").on('click', function () {
          jQuery.ajax({
                type: "POST",
                dataType: 'json',
                url:'/data',
                data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": {'id_sub': $(this).attr('data-id'), 'stage': $(this).attr('data-stage'), 'id_order': $(this).attr('data-order')}}),
                contentType: "application/json; charset=utf-8",
                success: function (data) {
                    if(data.error){
                        alert('Error: '+ data.error.data.message);
                    }else{
                        if(data.result.check_active == 2){
                            window.location= window.location.origin + '/plans/payment';
                        }else{
                             $('#hidden_subscription_modal .modal-dialog.modal-content').height(420);
                            $('.content_data').html(data.result.html);
                            $('#next_step_account').attr('data-step',5);
                            $('#hidden_subscription_modal').modal('show');
                        }
                    }
                },
           });
     });
     $('#next_step_account').click(function () {
        let step_click = parseFloat($(this).attr('data-step'));
        let id_sub = $(this).attr('data-id');
        let total = $("input[name='total']").val();
         if(step_click==5){
            jQuery.ajax({
                type: "POST",
                dataType: 'json',
                url:'/data/'+step_click,
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": {'id_sub': id_sub, 'total': total}}),
                success: function (data) {
                    if(data.error){
                        alert('Error: '+ data.error.data.message);
                    }else{
                        $('#next_step_account').attr('data-step',6);
                        $('.content_data').html(data.result.html);
                    }
                },
            });
         }
         if(step_click==6){
            var reg_name = $("input[name='name']").val();
            var reg_email = $("input[name='email']").val();
            var reg_phone = $("input[name='phone']").val();
            var reg_company_name = $("input[name='company_name']").val();
            var total_price = $("input[name='total']").val();
            var reg_country = $('select[name="country_id"]').val();
            var reg_language_id = $('select[name="language_id"]').val();
            var data = {
                'name': reg_name,
                'email': reg_email,
                'phone': reg_phone,
                'company': reg_company_name,
                'country': reg_country,
                'lang': reg_language_id,
                'total_price': total_price,
            };
            jQuery.ajax({
                type: "POST",
                dataType: 'json',
                url:'/data/'+step_click,
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": {'id_sub': id_sub, 'data_info': data}}),
                success: function (data) {
                    if(data.error){
                        alert('Error: '+ data.error.data.message);
                    }else{
                        window.location= window.location.origin + '/plans/payment';
                    }
                },
           });
        }
    });

     $(".upsell_subscription_status").on('click', function () {
        var id_order = $(this).attr("data-id");
        var data_arr = {
            'id_order': id_order,
            'type': 'upgrade',
        };
        $('#upsell_subscription').attr('data-step',1);
        get_modal_grade(data_arr)
     });
     $("#upsell_subscription").on('click', function () {
        let step_click = parseFloat($(this).attr('data-step'));
        let id_sub = $(this).attr('data-id');
        if(step_click == 1){
            var product_id = $("select[name='product_id']").val();
            var order_id = $("input[name='order_id']").val();
            var type = $("input[name='type']").val();
            var numUser = $("input[name='numUser']").val();
            var data_arr = {
                'order_id': order_id,
                'product_id': product_id,
                'type': type,
                'numUser': numUser
            };
            jQuery.ajax({
                type: "POST",
                dataType: 'json',
                url:'/detail_sale_order',
                data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": {'data': data_arr}}),
                contentType: "application/json; charset=utf-8",
                success: function (data) {
                    if(data.error){
                        alert('Error: '+ data.error.data.message);
                    }else{
                        $('#hidden_subscription_upsell_modal .modal-dialog.modal-content').height(520);
                        $('#hidden_subscription_upsell_modal .content_data').html(data.result.html);
                        $('#upsell_subscription').attr('data-step',2);
                        $('#hidden_subscription_upsell_modal').modal('show');
                    }
                },
           });
        }
        if(step_click == 2){
            var product_id = $("input[name='product_id']").val();
            var order_id = $("input[name='order_id']").val();
            var type = $("input[name='type']").val();
            var quantity = $("input[name='quantity']").val();
            var credit = $("input[name='credit']").val();
            var total = $("input[name='total']").val();
            var price_new_one_user = $("input[name='price_new_one_user']").val();
            jQuery.ajax({
                type: "POST",
                dataType: 'json',
                url:'/data/5',
                data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": {'id_sub': order_id, 'total': total, 'product_id': product_id, 'type': type, 'quantity': quantity, 'credit': credit, 'price_new_one_user': price_new_one_user}}),
                contentType: "application/json; charset=utf-8",
                success: function (data) {
                    if(data.error){
                        alert('Error: '+ data.error.data.message);
                    }else{
                        $('#hidden_subscription_upsell_modal .modal-dialog.modal-content').height(590);
                        $('#upsell_subscription').attr('data-step',3);
                        $('.content_data').html(data.result.html);
                    }
                },
           });
        }
        if(step_click == 3){
            var reg_name = $("input[name='name']").val();
            var reg_email = $("input[name='email']").val();
            var reg_phone = $("input[name='phone']").val();
            var reg_company_name = $("input[name='company_name']").val();
            var reg_country = $('select[name="country_id"]').val();
            var reg_language_id = $('select[name="language_id"]').val();
            var order_id = $("input[name='order_id']").val();
            var product_id = $("input[name='product_id']").val();
            var partner_id = $("input[name='partner_id']").val();
            var type = $("input[name='type']").val();
            var quantity = $("input[name='quantity']").val();
            var credit = $("input[name='credit']").val();
            var price_new_one_user = $("input[name='price_new_one_user']").val();
            var total = $("input[name='total']").val();
            var data = {
                'name': reg_name,
                'email': reg_email,
                'phone': reg_phone,
                'company': reg_company_name,
                'country': reg_country,
                'lang': reg_language_id,
                'product_id': product_id,
                'partner_id': partner_id,
                'type': type,
                'quantity': quantity,
                'credit': credit,
                'price_new_one_user': price_new_one_user,
                'total': total,
            };
            jQuery.ajax({
                type: "POST",
                dataType: 'json',
                url:'/create_sale_order',
                data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": {'order_id': order_id, 'data': data}}),
                contentType: "application/json; charset=utf-8",
                success: function (data) {
                    if(data.error){
                        alert('Error: '+ data.error.data.message);
                    }else{
                        if(data.result.order_id){
                            if(data.result.type == 'upgrade'){
                                window.location= window.location.origin + '/plans/payment';
                            }else{
                                $('#hidden_subscription_upsell_modal .modal-dialog.modal-content').height(300);
                                $('#upsell_subscription').hide();
                                $('.content_data').html(data.result.messeger);
                            }
                        }
                    }
                },
           });
        }
    });
});
function get_modal_grade(e){
    jQuery.ajax({
        type: "POST",
        dataType: 'json',
        url:'/showproduct',
        data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": {'data': e}}),
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            if(data.error){
                alert('Error: '+ data.error.data.message);
            }else{
                $('#hidden_subscription_upsell_modal .modal-dialog.modal-content').height(500);
                $('.content_data').html(data.result.html);
                $('#hidden_subscription_upsell_modal').modal('show');
                $('#action_update').change(function () {
                    var type = $('select[name="action_update"]').val();
                    var order_id = $("input[name='order_id']").val();
                    var data_arr2 = {
                        'order_id': order_id,
                        'type': type
                    };
                    $("input[name='type']").val(type);
                    get_plan(data_arr2)
                });
                $('#product_id').change(function () {
                    var product_id = $('select[name="product_id"]').val();
                    var order_id = $("input[name='order_id']").val();
                    var data = {
                        'order_id': order_id,
                        'product_id': product_id,
                    };
                    get_user_number(data)
                });
            }
        },
    });
}
function get_plan(e){
    jQuery.ajax({
        type: "POST",
        dataType: 'json',
        url:'/get-plan',
        data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": {'data': e}}),
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            if(data.error){
                alert('Error: '+ data.error.data.message);
            }else{
                $('select[name="product_id"]').html(data.result.html);
                if(data.result.html ==''){
                    $('#upsell_subscription').hide();
                    $('.choose-users input[name="numUser"]').attr('min',0);
                    $('.choose-users input[name="numUser"]').val(0);
                }else{
                    $('.choose-users input[name="numUser"]').attr('min',data.result.numuser);
                    $('.choose-users input[name="numUser"]').val(data.result.numuser);
                    $('#upsell_subscription').show();
                }
            }
        },
    });
}
function get_user_number(e){
    jQuery.ajax({
        type: "POST",
        dataType: 'json',
        url:'/get-user-number',
        data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": {'data': e}}),
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            if(data.error){
                alert('Error: '+ data.error.data.message);
            }else{
                $('.choose-users input[name="numUser"]').attr('min',data.result.numuser);
                $('.choose-users input[name="numUser"]').val(data.result.numuser);
            }
        },
    });
}