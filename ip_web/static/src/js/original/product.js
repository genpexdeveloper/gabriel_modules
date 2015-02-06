var Product_Page_Top_Price = Backbone.View.extend({
  el : '.ip-single-product-price',
  initialize : function() {
  },
  set_value : function(value) {
    this.$el.find('.oe_currency_value').text(Number(value).formatMoney(2));
  }
});
var Product_Page_Variants_Table = Backbone.View.extend({
  el : '.ip-variants-table',
  selected : null,
  initialize : function() {
    var all_empty = this.$el.find('td.ip-variants-table-size').filter(function() {
      return $.trim($(this).text()) != '';
    }).length == 0;
    if (all_empty) this.$el.find('.ip-variants-table-size').hide();
    this.$el.find('tbody tr').on('click', _.bind(this.select, this));
    this.$el.find('.ip-number-group input[type="text"]').on('change', _.bind(this.handle_after_select, this));
  },
  select_first : function() {
    if (this.$el.find('tbody').find('tr:first').size() === 0) return false;
    var first = this.$el.find('tbody').find('tr:first');
    first.addClass("ui-state-highlight");
    this.selected = first;
    this.handle_after_select();
  },
  select : function(e) {
    this.$el.find('.ui-state-highlight').removeClass("ui-state-highlight");
    this.selected = $(e.target).closest('tr').addClass("ui-state-highlight");
    this.handle_after_select();
  },
  handle_after_select : function() {
    if (!this.selected) return;
    var variant_id = this.selected.attr('data-variant-id');
    var variant_price = Number(this.selected.attr('data-variant-price'));
    var quantity = Number(this.selected.find('.ip-number-group').find('input[type="text"]').val());
    product_page_fbt.set_active(variant_id);
    product_page_cab.set_active(variant_id);
    var fbt_additional = product_page_fbt.get_amount();
    var total = variant_price * quantity + fbt_additional;
    product_page_top_price.set_value(variant_price);
    product_page_cart_summary.set_total_price(total);
    $('section.ip-product-description').hide();
    $('section.ip-product-description[data-variant-id="' + variant_id + '"]').show();
    product_autoship_button.update();
  }
});
var Product_Page_Variants_Undertable = Backbone.View.extend({
  el : '.ip-product-undertable-buttons-wrapper',
  initialize : function() {
    this.$el.find('.ip-product-cart-button').on('click', function(e) {
      e.preventDefault();
      if ($(e.target).hasClass("btn-disabled")) {
        $('#aj-cant-add-to-cart').modal('show');
        return;
      }
      if (!product_page_variants_table.selected) return;
      var prod_id = product_page_variants_table.selected.attr('data-variant-id');
      var prod_quantity = product_page_variants_table.selected.find('.ip-number-group input[type="text"].input-number').val();
      var data = {};
      data[prod_id] = prod_quantity;
      ip_add_to_cart(data);
    });
  }
});
var Product_Page_FBT = Backbone.View.extend({
  el : '#ip-fbt',
  element : null,
  initialize : function() {
    this.$el.find('input[type="checkbox"]').click(function() {
      if ($(this).is(':checked')) {
        product_page_cart_summary.add_to_total($(this).attr('price'));
        product_page_cart_summary.increase_total_selected_variants();
      }
      else {
        product_page_cart_summary.remove_from_total($(this).attr('price'));
        product_page_cart_summary.decrease_total_selected_variants();
      }
    });
  },
  set_active : function(variant_id) {
    this.element = this.$el.find('.ip-fbt[data-variant-id="' + variant_id + '"]');
    if (this.element.is(':visible')) return;
    this.clear_all();
    this.$el.find('.ip-fbt').hide();
    this.element.show();
    product_page_cart_summary.set_total_variants(this.element.attr('data-fbt-total'));
  },
  clear_all : function() {
    this.$el.find('input[type="checkbox"]:checked').each(function() {
      $(this).removeAttr('checked');
      product_page_cart_summary.remove_from_total($(this).attr('price'));
      product_page_cart_summary.decrease_total_selected_variants();
    });
  },
  get_amount : function() {
    var amount = 0;
    this.element.find('input[type="checkbox"]:checked').each(function() {
      amount += Number($(this).attr('price'));
    });
    return amount;
  }
});
var Product_Page_CAB = Backbone.View.extend({
  el : '#ip-cab',
  element : null,
  set_active : function(variant_id) {
    this.element = this.$el.find('.ip-cab[data-variant-id="' + variant_id + '"]');
    this.$el.find('.ip-cab').hide();
    this.element.show();
  }
});
var Product_Page_Cart_Summary = Backbone.View.extend({
  el : '.ip-fbt-summary',
  initialize : function() {
    this.$el.next().find('.ip-product-cart-button').on('click', function() {
      var data = {};

      if (!product_page_variants_table.selected) return;
      var prod_id = product_page_variants_table.selected.attr('data-variant-id');
      var prod_quantity = product_page_variants_table.selected.find('.ip-number-group input[type="text"].input-number').val();
      data[prod_id] = prod_quantity;
      product_page_fbt.$el.find('input[type="checkbox"]:checked').each(function() {
        data[$(this).attr('data-id')] = 1;
      });
      ip_add_to_cart(data);
    });
  },
  set_total_variants : function(total) {
    this.$el.find('.variants-count-total').text(total);
    if (Number(total) === 0) {
      this.$el.find('.ip-variants-count').hide();
      this.$el.next().find('.ip-product-cart-button').hide();
    }
    else {
      this.$el.find('.ip-variants-count').show();
      this.$el.next().find('.ip-product-cart-button').show();
    }
  },
  set_total_selected_variants : function(total) {
    this.$el.find('.variants-count-selected').text(total);
  },
  increase_total_selected_variants : function() {
    var element = this.$el.find('.variants-count-selected');
    element.text(Number(element.text()) + 1);
  },
  decrease_total_selected_variants : function() {
    var element = this.$el.find('.variants-count-selected');
    element.text(Number(element.text()) - 1);
  },
  set_total_price : function(total) {
    $('body').find('.ip-single-product-price .oe_currency_value').text(total.formatMoney(2));

  },
  add_to_total : function(amount) {
    var element = this.$el.find('.ip-fbt-total .oe_currency_value');
    element.text((Number(element.text()) + Number(amount)).formatMoney(2));
  },
  remove_from_total : function(amount) {
    var element = this.$el.find('.ip-fbt-total .oe_currency_value');
    element.text((Number(element.text()) - Number(amount)).formatMoney(2));
  }
});
var Product_Image_Gallery = Backbone.View.extend({
  el : '.ip-product-gallery',
  initialize : function() {
    var self = this;
    this.$el.find('.ip-product-thumb').on('click', function(e) {
      e.preventDefault();
      self.$el.find('.ip-product-thumbs .active').removeClass('active');
      $(this).addClass('active');
      var image = $(this).find('span').attr('data-oe-field');
      var variant_id = $(this).find('span').attr('data-oe-id');
      self.$el.find('.ip-product-main-image > a.fancybox').hide();
      self.$el.find('.ip-product-main-image > a.fancybox span[data-oe-field="' + image + '"][data-oe-id="' + variant_id + '"]').show().parent().show();
    });
  }
});
$(document).ready(function() {
  // REMOVE FIRST PLUS SIGN FOR FREQUENTLY BOUGHT ITEMS LISTING
  $('.ip-fbt-image.ip-fbt-plus:first').removeClass('ip-fbt-plus');
  // REMOVE FIRST BORDER FROM "CUSTOMERS ALSO BOUGHT" LISTING
  $('.ip-cab-item.ip-border-right-dotted:last').removeClass('ip-border-right-dotted');
  // ADD TO CARD EVENT ON "CUSTOMERS ALSO BOUGHT" LISTING ITEM
  $(document).on('click', '.ip-link-add-to-cart', function(e) {

    e.preventDefault();
    var data = {};
    if ($(e.target).hasClass('btn-disabled')) return;

    data[$(this).attr('data-id')] = 1;
    ip_add_to_cart(data);
  });
  $('.aj-get-this-on').each(function() {
    var date = moment($(this).text(), "MM-DD-YYYY");
    $(this).text(date.format('D, MMM'));
  });
  $('.aj-order-by').each(function() {
    var date = moment();
    $(this).text(date.format('H:m, dddd'));
  });
  $('.aj-box-quantity').on('click', function(e) {
    e.preventDefault();
    var quantity_input = $(this).parents('tr:first').find('.ip-number-group input[type="text"]');
    if ($(this).hasClass('active')) {
      quantity_input.val(Number(quantity_input.val()) / Number(quantity_input.attr('data-step'))).change();
      ;
      $(this).removeClass('active');
      quantity_input.attr('data-step', 1);
    }
    else {
      quantity_input.val(Number(quantity_input.val()) * Number($(this).attr('data-box-quantity'))).change();
      ;
      $(this).addClass('active');
      quantity_input.attr('data-step', $(this).attr('data-box-quantity'));
    }
  });
});