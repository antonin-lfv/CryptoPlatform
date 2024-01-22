//[advanced form element Javascript]


$(function () {
    "use strict";
	
	//Bootstrap-TouchSpin
        $(".vertical-spin").TouchSpin({
            verticalbuttons: true,
            verticalupclass: 'ti-plus',
            verticaldownclass: 'ti-minus'
        });
        var vspinTrue = $(".vertical-spin").TouchSpin({
            verticalbuttons: true
        });
        if (vspinTrue) {
            $('.vertical-spin').prev('.bootstrap-touchspin-prefix').remove();
        }

        $("input[name='range_int_selector_rent']").TouchSpin({
            initval: 1
        });

        $("input[name='range_int_selector_unrent']").TouchSpin({
            initval: 1
        });

        $("input[name='range_int_selector_buy']").TouchSpin({
            initval: 1
        });

        $("input[name='range_int_selector_sell']").TouchSpin({
            initval: 1
        });
	
  });