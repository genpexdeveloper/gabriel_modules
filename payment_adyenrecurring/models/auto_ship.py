import requests
import urlparse
from suds.client import Client
from suds.transport.http import HttpAuthenticated
from ZSI import TC
from ZSI.client import Binding
from ZSI.auth import AUTH
from requests.auth import HTTPBasicAuth
from openerp.osv import osv, fields
from adyenPaymentGateway import AdyenPaymentGateway
from datetime import datetime

class auto_ship(osv.osv):

	_inherit = "ip_web_addons.auto_ship"

	_columns = {
		'shopperReference': fields.char('shopperReference', help="shopperReference used to identify shopper with ADYEN"),
	}

	def retrieve_reccurent_details(self, cr, uid, autoship_id, context=None):
		pa_model = self.pool['payment.acquirer']

		autoship = self.browse(cr, uid, autoship_id, context=context)
		if autoship.shopperReference:
			pa_ids = pa_model.search(cr, uid, [('provider', '=', 'adyen'), ('website_published', '=', True)], context=context)
			if pa_ids and pa_ids[0]:
				adyenpayment = pa_model.browse(cr, uid, pa_ids[0], context=context)
				adyenurl = pa_model.get_adyen_restrecurringservice_urls(cr, uid, adyenpayment.environment,
																		context=context)

				#recurringrequest = {"action": "Recurring.listRecurringDetails",
				#					"recurringDetailsRequest.merchantAccount": adyenpayment.adyen_merchant_account,
				#					'recurringDetailsRequest.shopperReference': autoship.shopperReference,
				#					'recurringDetailsRequest.recurring.contract': 'RECURRING'}
				#The request to send is a bit different than the one in the documentation
				recurringrequest = {"request.shopperReference": autoship.shopperReference,
									'request.merchantAccount': adyenpayment.adyen_merchant_account}

				recurringDetailsResponse = requests.post(adyenurl, params=recurringrequest,
								auth=HTTPBasicAuth('ws@Company.%s' % adyenpayment.adyen_company_account,
													adyenpayment.adyen_ws_password))
				if recurringDetailsResponse.status_code == 200:
					recurringDetails = urlparse.parse_qs(recurringDetailsResponse.text)
					numctr = 0
					toReturn = []
					while 'result.details.%s.recurringDetailReference' % numctr in recurringDetails:
						recurringDetail = {
							'recurringDetailReference': recurringDetails['result.details.%s.recurringDetailReference' % numctr][0],
							'variant': recurringDetails['result.details.%s.variant' % numctr][0],
							'creationDate': recurringDetails['result.details.%s.creationDate' % numctr][0].replace("T", " "),
						}
						if 'result.details.%s.card.holderName' % numctr in recurringDetails:
							recurringDetail['holderName'] = recurringDetails['result.details.%s.card.holderName' % numctr][0]
							recurringDetail['expiryMonth'] = recurringDetails['result.details.%s.card.expiryMonth' % numctr][0]
							recurringDetail['expiryYear'] = recurringDetails['result.details.%s.card.expiryYear' % numctr][0]
							recurringDetail['cardNumber'] = recurringDetails['result.details.%s.card.number' % numctr][0]
						toReturn.append(recurringDetail)
						numctr = numctr + 1
					return toReturn
		return False

	def request_payment(self, cr, uid, autoship_id, amount, currency, emailaddr, reference, saleorder, context=None):
		pa_model = self.pool['payment.acquirer']

		autoship = self.browse(cr, uid, autoship_id, context=context)
		if autoship.shopperReference and not saleorder.payment_tx_id:
			pa_ids = pa_model.search(cr, uid, [('provider', '=', 'adyen'), ('website_published', '=', True)], context=context)
			if pa_ids and pa_ids[0]:
				adyenpayment = pa_model.browse(cr, uid, pa_ids[0], context=context)

				payment_data = {
					'acquirer_id':  pa_ids[0],
					'type': 'server2server',
					'state': 'pending',
					'amount': amount,
					'currency_id': saleorder.currency_id.id,
					'reference': reference,
					'partner_id': saleorder.partner_id.id,
			        'partner_name': saleorder.partner_id.name,
			        'partner_lang': saleorder.partner_id.lang,
			        'partner_email': emailaddr,
			        'partner_zip': saleorder.partner_id.zip,
			        'partner_address': saleorder.partner_id.street,
			        'partner_city': saleorder.partner_id.city,
			        'partner_country_id': saleorder.partner_id.country_id.id,
			        'partner_phone': saleorder.partner_id.phone,
			        'partner_reference': autoship.shopperReference,
				}
				pay_id = self.pool['payment.transaction'].create(cr, uid, payment_data, context=context)
				try:
					adyensoapurl = pa_model.get_adyen_soappaymentservice_urls(cr, uid, adyenpayment.environment,
																				context=context)
					adyencli = AdyenPaymentGateway(adyensoapurl, 'ws@Company.%s' % adyenpayment.adyen_company_account, adyenpayment.adyen_ws_password, adyenpayment.adyen_merchant_account)
					res = adyencli.authoriseRecurring(int(amount*100), currency, reference, emailaddr, autoship.shopperReference, 'LATEST', 'RECURRING', 'ContAuth')
					if res['resultCode'] == 'Authorised':
						payment_data = {
							'state': 'done',
							'state_message': '',
							'date_validate': datetime.now().isoformat(),
							'adyen_psp_reference': res['pspReference'],
						}
						self.pool['sale.order'].write(cr, uid, saleorder.id, {'payment_tx_id': pay_id,'payment_acquirer_id':pa_ids[0]}, context=context)
					else:
						payment_data = {
							'state': 'error',
							'state_message': res['refusalReason'],
						}

					self.pool['payment.transaction'].write(cr, uid, pay_id, payment_data, context=context)

				except Exception, e:
					payment_data = {
						'state': 'error',
						'state_message': unicode(e),
					}
					self.pool['payment.transaction'].write(cr, uid, pay_id, payment_data, context=context)
