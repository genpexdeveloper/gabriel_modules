# -*- coding: utf-'8' "-*-"
from openerp.osv import osv, fields

class AcquirerAdyenRecurring(osv.Model):
    _inherit = 'payment.acquirer'

    _columns = {
        'adyen_company_account': fields.char('Adyen Company Account'),
        'adyen_ws_password': fields.char('Adyen Web services password'),
    }

    def adyen_form_generate_values(self, cr, uid, id, partner_values, tx_values, context=None):
        partner_values, adyen_tx_values = super(AcquirerAdyenRecurring, self).adyen_form_generate_values(cr, uid, id, partner_values, tx_values, context=context)
        ordname = tx_values['reference']
        order_model = self.pool['sale.order']
        counter_model = self.pool['ir.sequence']

        order_ids = order_model.search(cr, uid, [('name', '=', ordname)], context=context)
        orders = order_model.browse(cr, uid, order_ids, context=context)
        if orders and orders[0] and orders[0].draft_auto_ship:
            if not orders[0].shopperReference:
                shopperReference = counter_model.next_by_code(cr, uid, 'shopperReference', context=context)
                order_model.write(cr, uid, orders[0].id, {'shopperReference': shopperReference}, context=context)
            else:
                shopperReference = orders[0].shopperReference

            adyen_tx_values.update({
                'shopperEmail': partner_values['email'],
                'shopperReference': shopperReference,
                'recurringContract': "RECURRING",
            })
            acquirer = self.browse(cr, uid, id, context=context)
            adyen_tx_values['merchantSig'] = self._adyen_generate_merchant_sig(acquirer, 'in', adyen_tx_values)
        else:
            adyen_tx_values.update({
                'shopperReference': "",
            })
        return partner_values, adyen_tx_values

    def get_adyen_restrecurringservice_urls(self, cr, uid, environment, context=None):
        return'https://pal-%s.adyen.com/pal/servlet/Recurring/listRecurringDetails/V6' % environment
    
    def get_adyen_restpaymentservice_urls(self, cr, uid, environment, context=None):
        return 'https://pal-%s.adyen.com/pal/adapter/httppost?Payment.authorise' % environment
        #return 'https://pal-%s.adyen.com/pal/servlet/Payment/authorise/v9' % environment
    
    def get_adyen_soappaymentservice_urls(self, cr, uid, environment, context=None):
        return 'https://pal-%s.adyen.com/pal/servlet/soap/Payment' % environment
        #return 'https://pal-%s.adyen.com/pal/servlet/Payment/authorise/v9' % environment
    
    def get_adyen_soappaymentservice_wsdl(self, cr, uid, environment, context=None):
        return 'https://pal-%s.adyen.com/pal/Payment.wsdl' % environment
        #return 'https://pal-%s.adyen.com/pal/servlet/Payment/authorise/v9' % environment
        
class TxAdyenRecurring(osv.Model):
    _inherit = 'payment.transaction'

    _columns = {
        'adyen_shopper_reference': fields.char('Adyen Shopper Reference'),
    }
