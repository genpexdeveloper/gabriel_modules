// Base model
var IPModel = function(options) {
  Backbone.Model.apply(this, [ options ]);
};
_.extend(IPModel.prototype, Backbone.Model.prototype, {
  ajax : function(params, callback, fail, error) {
    if (!$.isPlainObject(params)) {
      params = {
        url : params
      };
    }
    if (typeof params.handleResponse === "undefined") {
      params.handleResponse = true;
    }
    return $.ajax(_.extend({}, params, {
      xhrFields : {
        withCredentials : true
      },
      error : function(jqXHR, exception) {
        if (params.handleResponse) {
          if (jqXHR.status === 0) {
            message = 'Not connected. Verify Network.';
          }
          else if (jqXHR.status === 401) {
            message = 'Unauthorized. [401].';
          }
          else if (jqXHR.status === 403) {
            message = 'Forbidden. [403].';
          }
          else if (jqXHR.status === 404) {
            message = 'Requested page not found. [404]';
          }
          else if (jqXHR.status === 500) {
            message = 'Internal Server Error [500].';
          }
          else if (exception === 'parsererror') {
            message = 'Requested JSON parse failed.';
          }
          else if (exception === 'timeout') {
            message = 'Time out error.';
          }
          else if (exception === 'abort') {
            message = 'Ajax request aborted.';
          }
          else {
            message = 'Uncaught Error.\n' + jqXHR.responseText;
          }
          if (typeof error === "function") {
            error({
              status : "error",
              message : message
            }, jqXHR, exception);
          }
          else {
            if (typeof console !== "undefined") {
              console.log(message, jqXHR, exception);
            }
          }
        }
        else {
          if (typeof error === "function") {
            error(jqXHR, exception);
          }
          else {
            if (typeof console !== "undefined") {
              console.log(jqXHR, exception);
            }
          }
        }
      },
      success : function(data, status, XMLHttpRequest) {
        data = JSON.parse(data);
        if (params.handleResponse) {
          if (data.status === "success") {
            if (typeof callback === "function") {
              callback(data.data, status, XMLHttpRequest);
            }
          }
          else if (data.status === "fail") {
            if (typeof fail === "function") {
              fail(data.data, status, XMLHttpRequest);
            }
            else {
              if (typeof console !== "undefined") {
              }
            }
          }
          else if (data.status === "error") {
            if (typeof error === "function") {
              error(data.message, status, XMLHttpRequest);
            }
            else {
              if (typeof console !== "undefined") {
                console.log(data.message, status, XMLHttpRequest);
              }
            }
          }
        }
        else {
          if (typeof callback === "function") {
            callback(data, status, XMLHttpRequest);
          }
        }
      }
    }));
  }
});
IPModel.extend = Backbone.Model.extend;
var ip_model = new IPModel();
var layout_header_cart;
// USED TO FORMAT CURRENCY
Number.prototype.formatMoney = function(c, d, t) {
  var n = this, c = isNaN(c = Math.abs(c)) ? 2 : c, d = d == undefined ? "." : d, t = t == undefined ? "," : t, s = n < 0 ? "-" : "", i = parseInt(n = Math.abs(+n || 0).toFixed(c)) + "", j = (j = i.length) > 3 ? j % 3 : 0;
  return s + (j ? i.substr(0, j) + t : "") + i.substr(j).replace(/(\d{3})(?=\d)/g, "$1" + t) + (c ? d + Math.abs(n - i).toFixed(c).slice(2) : "");
};
// USED TO REMOVE CSS OR JS BEFORE PAGE FULLY LOADED
function removeJsCssFile(filename, filetype) {
  var targetelement = (filetype == "js") ? "script" : (filetype == "css") ? "link" : "none" //determine element type to create nodelist from
  var targetattr = (filetype == "js") ? "src" : (filetype == "css") ? "href" : "none" //determine corresponding attribute to test for
  var allsuspects = document.getElementsByTagName(targetelement)
  for (var i = allsuspects.length; i >= 0; i--) { //search backwards within nodelist for matching elements to remove
    if (allsuspects[i] && allsuspects[i].getAttribute(targetattr) != null && allsuspects[i].getAttribute(targetattr) == filename) allsuspects[i].parentNode.removeChild(allsuspects[i]) //remove element by calling parentNode.removeChild()
  }
}
var Layout_Header_Cart = Backbone.View.extend({
  el : '.header-cart',
  currency : ip_currency,
  update : function() {
    ip_model.ajax('/shop/get_cart_info', _.bind(this._update_cart, this));
  },
  _update_cart : function(response) {
    if (response.product_count > 0) {
      $('.ip-mycart-undertable').show();
    }
    else {
      $('.ip-mycart-undertable').hide();
    }
    this.$el.find('.header-cart-incart').text(response.product_count);
    this.$el.find('.header-cart-amount').text(Number(response.total_price).formatMoney(2) + ' ' + this.currency);

  }
});
var Product_Autoship_Button = Backbone.View.extend({
  el : '#ip-autoship',
  initialize : function() {
    var self = this;

    $(document).on('click', '#ip-autoship.btn-autoship', _.bind(this.set_autoship, this));
    $(document).on('click', '#ip-autoship.btn-danger', _.bind(this.unset_autoship, this));
    $(document).on('click', '#ip-autoship.btn-disabled', _.bind(this.open_modal, this));
    $('#aj-autoship-confirm').on('click', function(e) {
      e.preventDefault();
      var interval = $.trim($('#aj-as-interval').val());
      var end_date = $.trim($('#aj-as-end-date').val());
      if (interval == "") {
        $('#aj-as-interval').parent().addClass('has-error');
        return;
      }
      else {
        $('#aj-as-interval').parent().removeClass('has-error');
      }
      if (end_date == "") {
        $('#aj-as-end-date').parent().addClass('has-error');
        return;
      }
      else {
        $('#aj-as-end-date').parent().removeClass('has-error');
      }
      var add_to_autoship = function() {
        ip_model.ajax({
          url : '/shop/set_auto_ship',
          type : 'POST',
          data : {
            "auto_ship" : "true",
            "interval" : interval,
            "end_date" : end_date
          }
        }, function() {
          self.update();
          $('#aj-autoship-modal').modal('hide');
        }, function(data) {
          if (typeof data.interval !== "undefined") {
            $('#aj-as-interval').parent().addClass('has-error');
            return;
          }
          else {
            $('#aj-as-interval').parent().removeClass('has-error');
          }
          if (typeof data.end_date !== "undefined") {
            $('#aj-as-end-date').parent().addClass('has-error');
            return;
          }
          else {
            $('#aj-as-end-date').parent().removeClass('has-error');
          }

          if (typeof data.auto_ship !== "undefined") {
            $('#aj-autoship-modal').modal('hide');
            var modal = $('#aj-error-modal').clone();
            modal.find('.ip-error-modal-title').text('Autoship cannot be added');
            modal.find('.modal-body').text(data.auto_ship);
            modal.modal('show');
          }
        }, function() {
          $('#aj-autoship-modal').modal('hide');
          $('#aj-error-modal').modal('show');
        });
      };
      if (typeof product_page_variants_table !== "undefined") {
        if (!product_page_variants_table.selected) return;
        var prod_id = product_page_variants_table.selected.attr('data-variant-id');
        var prod_quantity = product_page_variants_table.selected.find('.ip-number-group input[type="text"].input-number').val();
        var data = {};
        data[prod_id] = prod_quantity;
        ip_add_to_cart(data, add_to_autoship);
      }
      else {
        add_to_autoship();
      }
    });
  },
  update : function() {

    var self = this;

    self._check_if_can_add_to_cart();

    ip_model.ajax('/shop/get_auto_ship', function(response) {
      if (response.auto_ship == "false") {
        self._check_if_can_autoship();
      }
      else {
        self._set_as_is_autoship(response);
      }
    }, function(response) {
      self._check_if_can_autoship();

    });
  },
  set_autoship : function() {
    var self = this;
    $('#aj-autoship-modal').modal('show');
  },
  unset_autoship : function() {
    var self = this;
    ip_model.ajax({
      url : '/shop/set_auto_ship',
      type : 'POST',
      data : {
        "auto_ship" : "false"
      }
    }, function() {
      self.update();
    }, function() {
    }, function() {
      $('#aj-error-modal').modal('show');
    });
  },
  open_modal : function(e) {
    e.preventDefault();
    $('#aj-non-autoship-modal').modal('show');
  },

  _check_if_can_add_to_cart : function() {

    ip_model.ajax({
      url : '/shop/get_cart_info/',
      type : "GET",
    }, function(e) {

      if( e.contains_autoship ) {
        $('a[data-autoship=False]').addClass('btn-disabled')
        $('a[data-autoship=False]').css('opacity',0.2).off('click').on('click',function(e){
         e.preventDefault();
        });
        
      }
      else
        {
        $('a[data-autoship=True]').removeClass('btn-disabled')
        $('a[data-autoship=True]').css('opacity',1).off('click');
        }
      
      if (e.contains_autoship  && $("#ip-autoship").length < 1 ) {
        
        
        $('.ip-product-cart-button').addClass('btn-disabled');
       
      }
      else {
        $('.ip-product-cart-button').removeClass('btn-disabled');
        
      }
    });

    //
  },

  _check_if_can_autoship : function() {
    var self = this;

    if (self.$el.attr('data-disable-if-empty-cart') === "true" && Number($('.header-cart-incart').text()) < 1) {
      self._set_as_can_not_autoship();
      return;
    }

    ip_model.ajax('/shop/can_auto_ship', function(response) {
      if (response.can_auto_ship == "false") {
        self._set_as_can_not_autoship();
      }
      else {
        self._set_as_can_autoship();
      }
    });

  },
  _set_as_can_autoship : function() {
    $('.aj-autoship-details').hide();
    this.$el.removeClass('btn-danger btn-disabled').addClass('btn-autoship').text(this.$el.attr('data-title-add'));
  },
  _set_as_is_autoship : function(data) {
    $('.aj-autoship-details').find('span.aj-autoship-details-interval').text(data.interval);
    $('.aj-autoship-details').find('span.aj-autoship-details-end-date').text(data.end_date);
    $('.aj-autoship-details').show();
    this.$el.removeClass('btn-autoship btn-disabled').addClass('btn-danger').text(this.$el.attr('data-title-remove'));
  },
  _set_as_can_not_autoship : function() {
    $('.aj-autoship-details').hide();
    this.$el.removeClass('btn-autoship btn-danger').addClass('btn-disabled').text(this.$el.attr('data-title-add'));
  }
});
// USED TO ADD PRODUCTS TO CART BY ID AND QUANTITY
function ip_add_to_cart(data, callback) {
  


  $('.ip-product-cart-button').find('.btn-label').find('i').attr('class', 'glyphicon glyphicon-time');

  ip_model.ajax({
    url : '/shop/add_cart_multi',
    type : "POST",
    data : data
  }, function() {
    if (typeof callback == "function") {
      callback();
    }
    layout_header_cart.update();
    product_autoship_button.update();

    $('.ip-product-cart-button').find('.btn-label').find('i').attr('class', 'glyphicon glyphicon-ok');

    setTimeout(function() {
      $('.ip-product-cart-button').find('.btn-label').find('i').attr('class', 'ip-cart-icon');
    }, 2000);
  }, function() {
  }, function() {
    $('#aj-error-modal').modal('show');
  });
}
var Number_Group = Backbone.View.extend({
  el : '.ip-number-group',
  initialize : function() {
    this.$el.each(function() {
      var input = $(this).find('input[type="text"]');
      var minus = $(this).find('button[data-type="minus"]');
      var plus = $(this).find('button[data-type="plus"]');
      minus.on('click', function() {
        if (Number(input.val()) > Number(input.attr('min'))) input.val(Number(input.val()) - Number(input.attr('data-step'))).change();
        if (Number(input.val()) === Number(input.attr('min'))) $(this).prop('disabled', true);
      });
      plus.on('click', function() {
        input.val(Number(input.val()) + Number(input.attr('data-step'))).change();
        if (Number(input.val()) > Number(input.attr('min'))) minus.prop('disabled', false);
      });
    });
  },
});
// DOCUMENT LOADED
$(document).ready(function() {
  number_group = new Number_Group();
  layout_header_cart = new Layout_Header_Cart();
  layout_header_cart.update();
  // WRAP LISTING ITEMS
  var divs = $("#ip-products > div.ip-category-product, .ip-product, .ip-product-thumb");
  var number_to_wrap = 4;
  if (/Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)) {
    number_to_wrap = 2;
  }
  for (var i = 0; i < divs.length; i += number_to_wrap) {
    divs.slice(i, i + number_to_wrap).wrapAll("<div class='row'></div>");
  }
  // SCROLL TO TOP ON CLICK "BACK TO TOP" LINK
  $(document).on('click', '.back-to-top', function(e) {
    e.preventDefault();
    $('html, body').animate({
      scrollTop : $('html').offset().top
    }, 500);
  });
  // KICKOFF FANCYBOX
  $('.fancybox').fancybox({
    type : 'image'
  });
  // PREVENT DROPDOWN FROM CLOSING WHEN CHICKED INSIDE
//  $('.dropdown-menu').on('click', function(e) {
//    e.stopPropagation();
//  });
  //INITAILIZE DATEPICKER
  $('.datepicker, .end_date').prop('readonly', true).datepicker({
    format : "yyyy-mm-dd"
  });
  // CHECKOUT PAGE RIGHT COL FIX (temp)
  //$('.oe_mycart').next('.col-lg-offset-1.col-lg-3.col-md-3, #right_column').attr('class', 'col-lg-4 col-md-4 text-muted col-lg-3');
  // LOGIN FORM BUTTON FIXES
  $('.oe_login_buttons').removeClass('clearfix');
});