# Client library for Adyen Payment Services
# Copyright (C) 2008 Fabio Tranchitella <fabio@tranchitella.it>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
#

from ZSI import TC
from ZSI.client import Binding
from ZSI.auth import AUTH

from adyenSoapModels import *

class AdyenPaymentGateway(object):
    """Payment Gateway utility for Adyen"""

    def __init__(self, url, user, password, merchantAccount):
        self.url = url
        self.user = user
        self.password = password
        self.merchantAccount = merchantAccount

    def authorise(self, txid, amount, currency, holderName, number,
            expiryMonth, expiryYear, cvc, ipAddress=None, browserInfo=None,
            billingAddress=None, shopperEmail=None, shopperReference=None, fraudOffset=None):
        """Send an authorise request"""
        gw = Binding(url=self.url, auth=(AUTH.httpbasic, self.user, self.password))
        request = PaymentRequest(
            Amount(currency, amount),
            browserInfo,
            Card(holderName, number, expiryMonth, expiryYear, cvc, billingAddress),
            self.merchantAccount,
            txid,
            ipAddress,
            shopperEmail,
            shopperReference,
            fraudOffset
        )
        result = gw.RPC(None, 'authorise', (request,), replytype=AuthoriseResponse.typecode)
        return {
            'authCode': result.paymentResult.authCode,
            'pspReference': result.paymentResult.pspReference,
            'issuerUrl': result.paymentResult.issuerUrl,
            'md': result.paymentResult.md,
            'paRequest': result.paymentResult.paRequest,
            'refusalReason': result.paymentResult.refusalReason,
            'fraudResult': result.paymentResult.fraudResult and result.paymentResult.fraudResult.accountScore or None,
        }

    def authorise3d(self, md, paResponse, ipAddress=None, browserInfo=None):
        """Send an authorise3d request"""
        gw = Binding(url=self.url, auth=(AUTH.httpbasic, self.user, self.password))
        request = PaymentRequest3d(
            md,
            self.merchantAccount,
            paResponse,
            browserInfo,
            ipAddress,
        )
        result = gw.RPC(None, 'authorise3d', (request,), replytype=Authorise3dResponse.typecode)
        return {
            'authCode': result.paymentResult.authCode,
            'pspReference': result.paymentResult.pspReference,
            'issuerUrl': result.paymentResult.issuerUrl,
            'md': result.paymentResult.md,
            'paRequest': result.paymentResult.paRequest,
            'refusalReason': result.paymentResult.refusalReason,
            'fraudResult': result.paymentResult.fraudResult and result.paymentResult.fraudResult.accountScore or None,
        }

    def authoriseRecurring(self, amount, currency, reference,
            shopperEmail, shopperReference, selectedRecurringDetailReference, recurring, shopperInteraction):
        """Send an authorise request"""
        gw = Binding(url=self.url, auth=(AUTH.httpbasic, self.user, self.password))
        request = RecurringPaymentRequest(
            Amount(currency, amount),
            self.merchantAccount,
            reference,
            shopperEmail,
            shopperReference,
            selectedRecurringDetailReference,
            Recurring(recurring),
            shopperInteraction
        )
        result = gw.RPC(None, 'authorise', (request,), replytype=AuthoriseResponse.typecode)
        return {
            'authCode': result.paymentResult.authCode,
            'pspReference': result.paymentResult.pspReference,
            'issuerUrl': result.paymentResult.issuerUrl,
            'md': result.paymentResult.md,
            'paRequest': result.paymentResult.paRequest,
            'refusalReason': result.paymentResult.refusalReason,
            'fraudResult': result.paymentResult.fraudResult and result.paymentResult.fraudResult.accountScore or None,
            'resultCode': result.paymentResult.resultCode
        }

    def cancel(self, txid):
        """Send a cancel request"""
        gw = Binding(url=self.url, auth=(AUTH.httpbasic, self.user, self.password))
        request = CancelRequest(self.merchantAccount, txid)
        result = gw.RPC(None, 'cancel', (request,), replytype=CancelResponse.typecode)
        return result.cancelResult.response == '[cancel-received]'

    def capture(self, txid, amount, currency):
        """Send a capture request"""
        gw = Binding(url=self.url, auth=(AUTH.httpbasic, self.user, self.password))
        request = CaptureRequest(self.merchantAccount, txid, ModificationAmount(currency, amount))
        result = gw.RPC(None, 'capture', (request,), replytype=CaptureResponse.typecode)
        return result.captureResult.response == '[capture-received]'

    def refund(self, txid, amount, currency):
        """Send a refund request"""
        gw = Binding(url=self.url, auth=(AUTH.httpbasic, self.user, self.password))
        request = RefundRequest(self.merchantAccount, txid, ModificationAmount(currency, amount))
        result = gw.RPC(None, 'refund', (request,), replytype=RefundResponse.typecode)
        return result.refundResult.response == '[refund-received]'
