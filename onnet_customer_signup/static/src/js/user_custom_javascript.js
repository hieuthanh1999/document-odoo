$(document).ready(function () {
    $('input[name="numUser"]').change(function () {
        let numUser = $(this).val();
        let price = $(this).attr("data-price");
        let package_name = $(this).attr("data-name");
        let trial = $('#trial').val();
        var total_price = numUser*parseFloat(price);
        if(trial ==1 ){
            price = 0;
        }
        $(this).parent().parent('h5.card-header').find('span.h5').html('$'+parseFloat(total_price).toFixed(2));
        if($(this).parent().parent('h5.card-header').find($("input[name='package']")).is(':checked')){
            $('.card .onnet_pricing_users_num').html(numUser);
            $('.card .name_package').html(package_name);
            $('.card .onnet_pricing_apps_price_yearly').html('$'+parseFloat(total_price).toFixed(2));
            $('.card .onnet_pricing_price_yearly').html('$'+total_price.toFixed(2));
            $("input[name='package_total']").val(total_price);
            $("input[name='package_total_change']").val(total_price);
            $("input[name='package_users_num']").val(numUser);
        }
    });

    $("input[name='package']").click(function () {
        let numUser = $(this).parent('h5.card-header').find($("input[name='numUser']")).val();
        let price = $(this).attr("data-price");
        let product_id = $(this).attr("data-value");
        let trial = $('#trial').val();
        var package_name = $('input[name="package"]:checked').attr("data-name");
        if(trial ==1 ){
            numUser = 1;
            price = 0;
        }
        var total_price = numUser*parseFloat(price);
        $('#form_product_id').val(product_id);
            $('.card .onnet_pricing_users_num').html(numUser);
            $('.card .name_package').html(package_name);
            $('.card .onnet_pricing_apps_price_yearly').html('$'+parseFloat(total_price).toFixed(2));
            $('.card .onnet_pricing_price_yearly').html('$'+total_price.toFixed(2));
            $("input[name='package_total']").val(total_price);
            $("input[name='package_total_change']").val(total_price);
            $("input[name='package_users_num']").val(numUser);
    });

    $("input[name='name_addons']").click(function () {
        get_add_click(this);
    });

    $('#next_step').click(function () {
        let step_click = parseFloat($(this).attr('data-step'));
        let trial = $("input[name='trial']").val();
        if(step_click==1){
            jQuery.ajax({
                type: "POST",
                dataType: 'json',
                url:'/plans/step'+step_click,
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": {'trial': trial, 'product_order': []}}),
                success: function (data) {
                    if(data.error){
                        alert('Error: '+ data.error.data.message);
                    }else{
                        $('.s_comparisons').removeClass('o_half_screen_height');
                        $('.s_process_step_icon .step2').addClass('bg-primary');
                        $('.s_process_step_icon .step2').removeClass('bg-600');
                        $('ul.card-header-tabs li.nav-item a').hide();
                        $('ul.card-header-tabs li.nav-item a.active').show();
                        $('#back_step').css("visibility", "visible");
                        $('#next_step').attr('data-step', 2);
                        $('.customer-plan').html(data.result.html);
                        $("input[name='name_addons']").click(function () {
                            get_add_click(this);
                        });
                        $('#back_step').click(function () {
                            let step_back = parseFloat($('#back_step').attr('data-step'));
                            CallBack(step_back, trial);
                        });
                    }
                }
            });
        }
        if(step_click==2){
            jQuery.ajax({
                type: "POST",
                dataType: 'json',
                url:'/plans/step'+step_click,
                contentType: "application/json; charset=utf-8",
                data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": {'trial': trial}}),
                success: function (data) {
                    if(data.error){
                        alert('Error: '+ data.error.data.message);
                    }else{
                        $('.s_process_step_icon .step3').addClass('bg-primary');
                        $('.s_process_step_icon .step3').removeClass('bg-600');
                        $('#next_step').attr('data-step', 3);
                        $('#back_step').attr('data-step', 3);
                        $('.customer-plan').html(data.result.html);
                        $("input[name='company_name']").keyup(function(){
                            changeCompanyName(this);
                        });
//                        $("#edit-db-name").click(function(){
//                            editDbName(this);
//                        });
                        $("input[name='email']").keyup(function(){
                            CheckUser(this);
                        });
                        $("input[name='website']").keyup(function(){
                            CheckDomain(this);
                        });
                        $("input[name='phone']").keyup(function(){
                            if(validatePhone($("input[name='phone']").val())){
                                $("input[name='phone']").removeClass('is-invalid');
                                $(".form-group .error_phone").addClass('d-none');
                            }else{
                                $("input[name='phone']").addClass('is-invalid');
                                $(".error_phone").removeClass('d-none');
                                $(".error_phone").html('Invalid phone number');
                            }
                        });
                    }
                },
            });
        }
        if(step_click==3){
            let trial = $("input[name='trial']").val();
            let product_order = $("input[name='product_order']").val();
            let product_id = $("input[name='product_id']").val();
            let package_users_num = $("input[name='package_users_num']").val();
            var reg_name = $("input[name='name']").val();
            var reg_email = $("input[name='email']").val();
            var reg_phone = $("input[name='phone']").val();
            var reg_company_name = $("input[name='company_name']").val();
            var reg_country = $('select[name="country_id"]').val();
            var reg_language = $('#language_id').val();
            var partner_id = $('input[name="partner_id"]').val();
            var reg_website = $('input[name="website"]').val();
            var reg_domain = $('input[name="db_name"]').val();
            var reg_industry = $('input[name="indistry"]').val();
            jQuery.ajax({
                type: "POST",
                dataType: 'json',
                dataType: 'json',
                url:'/check-user',
                data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": {'email': reg_email, 'partner_id': partner_id}}),
                contentType: "application/json; charset=utf-8",
                success: function (data) {
                    if(data.error){
                        alert('Error: '+ data.error.data.message);
                    }else{
                        if(data.result == true){
                            $("input[name='email']").addClass('is-invalid');
                            $(".error_email").removeClass('d-none');
                            $('.error_email').html('Email address already exists');
                            return false;
                        }else{
                            $("input[name='email']").removeClass('is-invalid');
                            $(".error_email").addClass('d-none');
                            if(reg_website.length < 4){
                                $("input[name='website']").addClass('is-invalid');
                                $(".domain-name-form .error_website").removeClass('d-none');
                                $(".domain-name-form .error_website").html('Your domain must be at least 4 characters long');
                                return false;
                            }else{
                                jQuery.ajax({
                                    type: "POST",
                                    dataType: 'json',
                                    url:'/check-domain',
                                    data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": {'domain': reg_website}}),
                                    contentType: "application/json; charset=utf-8",
                                    success: function (data) {
                                        if(data.error){
                                            alert('Error: '+ data.error.data.message);
                                        }else{
                                            if(data.result.check==1){
                                                $("input[name='website']").addClass('is-invalid');
                                                $(".domain-name-form .error_website").removeClass('d-none');
                                                $('.domain-name-form .error_website').html('Domain address already exists');
                                                return false;
                                            }else{
                                                $("input[name='website']").removeClass('is-invalid');
                                                $(".domain-name-form .error_website").addClass('d-none');
                                                if(ddlValidate(reg_name,reg_email,reg_phone,reg_company_name,reg_country,reg_language, reg_website)) {
                                                    jQuery.ajax({
                                                        type: "POST",
                                                        dataType: 'json',
                                                        url: '/plans/step'+step_click,
                                                        contentType: "application/json; charset=utf-8",
                                                        data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": {'trial': trial, 'reg_name': reg_name, 'reg_email': reg_email, 'reg_phone': reg_phone, 'reg_company_name': reg_company_name, 'reg_country': reg_country, 'reg_language_id': reg_language, 'reg_domain': reg_website, 'product_order': product_order, 'product_id': product_id, 'number_user': package_users_num, 'reg_industry': reg_industry}}),
                                                        success: function (data) {
                                                            if(data.error){
                                                                alert('Error: '+ data.error.data.message);
                                                            }else{
                                                                if(data.result.trial==1){
                                                                    window.location= window.location.origin + '/firework?product_id=' + data.result.id_plans + '&industry_id=' + reg_industry;
                                                                }else{
                                                                    $('.s_process_step_icon .step4').addClass('bg-primary');
                                                                    $('.s_process_step_icon .step4').removeClass('bg-600');
                                                                    $('#next_step').attr('data-step', 4);
                                                                    $('#next_step').hide();
                                                                    $('.back_step').css("visibility", "hidden");
                                                                    window.location= window.location.origin + '/pricing-payment';
                                                                }
                                                            }
                                                        },
                                                    });
                                                }
                                            }
                                        }
                                    },
                                });
                            }
                        }
                    }
                },
            });
        }
    });
});
  function changeCompanyName(e) {
        let slugCompanyName = slugify(this.$("input[name='company_name']").val());
        if (slugCompanyName != null) {
            this.$('#db-name').val(slugCompanyName);
            this.$('.db-name-section #website').val(slugCompanyName);
            this.$('#db-name-read-only').html(slugCompanyName);
        }
   }

  function CheckDomain(e) {
    let DomainName = slugify(this.$("input[name='website']").val());
    this.$("input[name='website']").val(DomainName);
    if(DomainName.length < 4){
        $("input[name='website']").addClass('is-invalid');
        $(".domain-name-form .error_website").removeClass('d-none');
        $(".domain-name-form .error_website").html('Your domain must be at least 4 characters long');
        return false;
    }else{
        jQuery.ajax({
            type: "POST",
            dataType: 'json',
            url:'/check-domain',
            data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": {'domain': DomainName}}),
            contentType: "application/json; charset=utf-8",
            success: function (data) {
                if(data.error){
                    alert('Error: '+ data.error.data.message);
                }else{
                    if(data.result.check==1){
                        $("input[name='website']").addClass('is-invalid');
                        $(".domain-name-form .error_website").removeClass('d-none');
                        $('.domain-name-form .error_website').html('Domain address already exists');
                        return false;
                    }else{
                        $("input[name='website']").removeClass('is-invalid');
                        $(".domain-name-form .error_website").addClass('d-none');
                        return true;
                    }
                }
            },
        });
    }
  }

 function CheckUser(e) {
    let Email = this.$("input[name='email']").val();
    let partner_id = this.$("input[name='partner_id']").val();
    jQuery.ajax({
        type: "POST",
        dataType: 'json',
        dataType: 'json',
        url:'/check-user',
        data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": {'email': Email, 'partner_id': partner_id}}),
        contentType: "application/json; charset=utf-8",
        success: function (data) {
            if(data.error){
                alert('Error: '+ data.error.data.message);
            }else{
                if(data.result.check==1){
                    $("input[name='email']").addClass('is-invalid');
                    $(".error_email").removeClass('d-none');
                    $('.error_email').html('Email address already exists');
                    return false;
                }else{
                    $("input[name='email']").removeClass('is-invalid');
                    $(".error_email").addClass('d-none');
                }
            }
        },
    });
  }
 function slugify(str){
    if (str == null)
        return '';
    var from = "ąàáäâãåæăćęèéëêìíïîłńòóöôõøśșțùúüûñçżź"
      , to = "aaaaaaaaaceeeeeiiiilnoooooosstuuuunczz"
      , regex = new RegExp(defaultToWhiteSpace(from),'g');
    str = String(str).toLowerCase().replace(regex, function(c) {
        var index = from.indexOf(c);
        return to.charAt(index) || '-';
    });
    str = str.replace(/[^\w\s-]/g, '');
    return str.replace(/([A-Z])/g, '-$1').replace(/[-_\s]+/g, '-').toLowerCase();
 }

 var defaultToWhiteSpace = function(characters) {
    if (characters == null)
        return '\\s';
    else if (characters.source)
        return characters.source;
    else
        return '[' + escapeRegExp(characters) + ']';
};

function editDbName(e) {
    this.customDomainName = true;
    this.$('.field-db-name-read-only').addClass('d-none');
    this.$('.db-name-section').removeClass('d-none');
}

function get_add_click(){
    var list_packages = [];
    var list_2= [];
    const obj = new contentHtml()
    var total = 0;
    var price = $('#form_package_total').val();
    var price_old = $('#form_package_total_change').val();
    var pro1 = $("input[name='product_id']").val();
    var trial = $("#trial").val();
    var sum_total = 0;
    $("input[name='name_addons']:checked:enabled").each(function () {
        addons_price = $(this).attr('data-price');
        if(trial == 1){
            addons_price = 0.0;
        }
        list_packages.push($(this).attr('data-name')+'-'+addons_price);
        total += parseFloat(addons_price);
        list_2.push($(this).val());
    });
    $("input[name='product_order']").val(list_2);
    obj.add(list_packages);
    $('#o_yearly_table .list_package').remove()
    $('.package_total').before(obj.html);
    sum_total = total + parseFloat(price_old);
    if(trial == 1){
        price_old = 0;
        price = 0;
        sum_total = 0;
    }
    $('.card .onnet_pricing_price_yearly').html(parseFloat(sum_total).toFixed(2));
    $("input[name='package_total']").val(parseFloat(sum_total).toFixed(2));
}

function contentHtml(){
     this.html = "";
}

contentHtml.prototype.add = function (array){
    array.forEach(list_package,this)
}

function list_package(item, index) {
    var items = item.split("-");
    this.html +='<tr class="list_package">';
        this.html +='<td>';
            this.html +='<span class="btn-link name_package">'+ items[0] +'</span>';
        this.html +='</td>';
        this.html +='<td class="text-right">';
            this.html +='<b class="onnet_pricing_apps_price_yearly">$'+ parseFloat(items[1]).toFixed(2) +'</b>';
            this.html +='<span class="onnet_pricing_currency"> USD</span>';
        this.html +='</td>';
    this.html +='</tr>';
}

var screenSize= $( window ).width();

//check item > 4 show slide
    $('.owl-carousel').owlCarousel({
        loop: false,
         nav: false,
        dots: false,
        margin:2,
//        autoplay: true,
//        autoPlaySpeed: 5000,
//        autoPlayTimeout: 5000,
//        autoplayHoverPause: true,
        responsive:{
            0:{
                items: 1
            },
            480:{
                items: 2
            },
            768:{
                items: 3
            },
            992:{
                items: 3
            }
        }
    })

//check if item < 5 và windown width size < 1200 show slide else do not show slides
if(screenSize < 1200 && $('.owl_plancing').length < 34) {
    $('.owl-carousel').owlCarousel({
        loop: false,
        margin:2,
        nav: false,
        responsive:{
            0:{
                items: 1
            },
            480:{
                items: 2
            },
            768:{
                items: 3
            },
            992:{
                items: 3
            }
        }
    })
}

function ddlValidate(reg_name, reg_email, reg_phone, reg_company_name, reg_country, reg_language, reg_website) {
    var check = true;
    if(reg_name === "" || reg_email === "" || reg_phone === "" || reg_company_name === "" || reg_country === "" || reg_language === "" || reg_website === ""){
         check = false;
    }
    if(reg_name === "") {
        $("input[name='name']").addClass('is-invalid');
        $(".form-group .error_name").removeClass('d-none');
        $(".form-group .error_name").html('Required Field');
        check == false
    }else{
        $("input[name='name']").removeClass('is-invalid');
        $(".form-group .error_name").addClass('d-none');
    }
    if(reg_phone === "") {
        $("input[name='phone']").addClass('is-invalid');
        $(".form-group .error_phone").removeClass('d-none');
        $(".form-group .error_phone").html('Required Field');
        check == false
    }else{
        if(validatePhone(reg_phone)){
            $("input[name='phone']").removeClass('is-invalid');
            $(".form-group .error_phone").addClass('d-none');
        }else{
            $("input[name='phone']").addClass('is-invalid');
            $(".error_phone").removeClass('d-none');
            $(".error_phone").html('Invalid phone number');
            return false;
        }
    }
    if(reg_email === "") {
        $("input[name='email']").addClass('is-invalid');
        $(".form-group .error_email").removeClass('d-none');
        $(".form-group .error_email").html('Required Field');
        return false;
    }else{
        if(!validateEmail(reg_email)) {
            $("input[name='email']").addClass('is-invalid');
            $(".form-group .error_email").removeClass('d-none');
            $(".form-group .error_email").html('Invalid Email Address');
            return false;
        }
    }
    if(reg_company_name === "") {
        $("input[name='company_name']").addClass('is-invalid');
        $(".form-group .error_message").removeClass('d-none');
        $(".form-group .error_message").html('Required Field');
        return false;
    }else{
        $("input[name='company_name']").removeClass('is-invalid');
        $(".form-group .error_message").addClass('d-none');
    }
    if(reg_country === "") {
        $("#country_id").addClass('is-invalid');
        $(".form-group .error_country").removeClass('d-none');
        $(".form-group .error_country").html('Required Field');
        return false;
    }else{
        $("#country_id").removeClass('is-invalid');
        $(".form-group .error_country").addClass('d-none');
    }
    if(reg_website === "") {
        $('#website').addClass('is-invalid');
        $(".form-group .error_website").removeClass('d-none');
        $(".form-group .error_website").html('Required Field');
        return false;
    }
    if(reg_language === "") {
        $('#language_id').addClass('is-invalid');
        $(".form-group .error_language").removeClass('d-none');
        $(".form-group .error_language").html('Required Field');
        return false;
    }else{
        $('#language_id').removeClass('is-invalid');
        $(".form-group .error_language").addClass('d-none');
    }

    if(check == false){
        return false
    }else{
        return true
//  document.forms["frm_subcription"].submit();
    }
}

function validateEmail($email) {
  var emailReg = /^([\w-\.]+@([\w-]+\.)+[\w-]{2,4})?$/;
  return emailReg.test( $email );
}

function validatePhone(txtPhone) {
    var filter = /^[\+65]?[(]?[0-9]{2}[)]?[-\s\.]?[0-9]{4}[-\s\.]?[0-9]{4}$/im;
    if (filter.test(txtPhone)) {
        return true;
    }
    else {
        return false;
    }
}

function CallBack(step, trial) {
    if(step==3){
        product_order = $("input[name='product_order']").val();
        jQuery.ajax({
            type: "POST",
            dataType: 'json',
            url:'/plans/step1',
            contentType: "application/json; charset=utf-8",
            data: JSON.stringify({'jsonrpc': "2.0", 'method': "call", "params": {'trial': trial, 'product_order': product_order}}),
            success: function (data) {
                if(data.error){
                    alert('Error: '+ data.error.data.message);
                }else{
                    $('.choose-number').hide();
                    $('.s_comparisons').removeClass('o_half_screen_height');
                    $('.s_process_step_icon .step3').removeClass('bg-primary');
                    $('.s_process_step_icon .step3').addClass('bg-600');
                    $('ul.card-header-tabs li.nav-item a').hide();
                    $('ul.card-header-tabs li.nav-item a.active').show();
                    $('#back_step').css("visibility", "visible");
                    $('#back_step').attr('data-step', 2);
                    $('#next_step').attr('data-step', 2);
                    $('.customer-plan').html(data.result.html);
                    $("input[name='name_addons']").click(function () {
                        get_add_click(this);
                    });
                }
            },
        });
    }else{
        location.reload();
    }
}

function escapeRegExp(str) {
    if (str == null)
        return '';
    return String(str).replace(/([.*+?^=!:${}()|[\]\/\\])/g, '\\$1');
}