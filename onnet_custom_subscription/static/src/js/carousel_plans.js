var screenSize= $( window ).width();

//check item > 4 show slide
if($('.customer_items').length > 6) {
    $('.layout_customers .owl-carousel').owlCarousel({
        loop: false,
        nav: false,
        dots: false,
        responsive:{
            0:{
                items: 1
            },
            480:{
                items: 2
            },
            768:{
                items: 4
            },
            992:{
                items: 6
            }
        }
    })
}
else{
}
//check if item < 5 và windown width size < 1200 show slide else do not show slides
if(screenSize < 1200 && $('.customer_items').length < 7) {
    $('.layout_customers .owl-carousel').owlCarousel({
        loop: false,
        nav: false,
        responsive:{
            0:{
                items: 1
            },
            480:{
                items: 2
            },
            768:{
                items: 2
            },
            992:{
                items: 3
            }
        }
    })
}

//slide Plans
 $('.plans_content .owl-carousel').owlCarousel({
        loop: false,
        nav: false,
        margin: 10,
        dots: false,
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

// Show data plans
odoo.define('onnet_custom_subscription.carousel_plans', function (require) {
    "use strict";

    var ajax = require('web.ajax');
    var rpc = require('web.rpc');

    $('.plans_content').hide();

    $('.tab_customers ').on('click', '.customer_items', function() {
            activeTab(this);
            return false;
    });

    function activeTab(obj){
        $('.customer_items.active').removeClass('active');
        $(obj).addClass('active');

        var id = $(obj).attr('data-values');
        $('.plans_content').hide();
        $('#'+id).show();
    }

    activeTab($('.tab_customers .customer_items.active:first-child'));
});

