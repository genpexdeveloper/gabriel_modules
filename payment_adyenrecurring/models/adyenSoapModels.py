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

# sudo aptitude install python-zsi

from ZSI import TC


class Amount:
    """Amount"""

    def __init__(self, currency, value):
        self.currency = currency
        self.value = value

Amount.typecode = TC.Struct(Amount, [
        TC.String(('http://common.services.adyen.com', 'currency')),
        TC.Ilong(('http://common.services.adyen.com', 'value')),
    ], ('http://payment.services.adyen.com', 'amount'))


class BrowserInfo:
    """Browser info"""

    def __init__(self, userAgent, acceptHeader):
        self.userAgent = userAgent
        self.acceptHeader = acceptHeader

BrowserInfo.typecode = TC.Struct(BrowserInfo, [
        TC.String(('http://common.services.adyen.com', 'userAgent')),
        TC.String(('http://common.services.adyen.com', 'acceptHeader')),
    ], ('http://payment.services.adyen.com', 'browserInfo'), nillable=True)


class BillingAddress:
    """Billing address"""

    def __init__(self, city=None, country=None, empty=None, houseNumberOrName=None,
            postalCode=None, stateOrProvince=None, street=None):
        self.city = city
        self.country = country
        self.empty = empty
        self.houseNumberOrName = houseNumberOrName
        self.postalCode = postalCode
        self.stateOrProvince = stateOrProvince
        self.street = street

BillingAddress.typecode = TC.Struct(BillingAddress, [
        TC.String(('http://payment.services.adyen.com', 'city'), nillable=True),
        TC.String(('http://payment.services.adyen.com', 'country'), nillable=True),
        TC.String(('http://payment.services.adyen.com', 'empty'), nillable=True),
        TC.String(('http://payment.services.adyen.com', 'houseNumberOrName'), nillable=True),
        TC.String(('http://payment.services.adyen.com', 'postalCode'), nillable=True),
        TC.String(('http://payment.services.adyen.com', 'stateOrProvince'), nillable=True),
        TC.String(('http://payment.services.adyen.com', 'street'), nillable=True),
    ], ('http://payment.services.adyen.com', 'billingAddress'), nillable=True)


class FraudResult:
    """Fraud result"""

    def __init__(self):
        self.accountScore = None

FraudResult.typecode = TC.Struct(FraudResult, [
        TC.Integer(('http://payment.services.adyen.com', 'accountScore'), nillable=True),
    ], ('http://payment.services.adyen.com', 'fraudResult'), nillable=True)


class Card:
    """Credit card"""

    def __init__(self, holderName, number, expiryMonth, expiryYear, cvc=None,
            issueNumber=None, startMonth=None, startYear=None, billingAddress=None):
        self.holderName = holderName
        self.number = number
        self.expiryMonth = expiryMonth
        self.expiryYear = expiryYear
        self.cvc = cvc

Card.typecode = TC.Struct(BrowserInfo, [
        BillingAddress.typecode,
        TC.String(('http://payment.services.adyen.com', 'cvc'), nillable=True),
        TC.String(('http://payment.services.adyen.com', 'expiryMonth')),
        TC.String(('http://payment.services.adyen.com', 'expiryYear')),
        TC.String(('http://payment.services.adyen.com', 'holderName')),
        TC.String(('http://payment.services.adyen.com', 'number')),
        TC.String(('http://payment.services.adyen.com', 'issueNumber'), nillable=True),
        TC.String(('http://payment.services.adyen.com', 'startMonth'), nillable=True),
        TC.String(('http://payment.services.adyen.com', 'startYear'), nillable=True),
    ], ('http://payment.services.adyen.com', 'card'))


class Recurring:
    """Recurring contract"""

    def __init__(self, contract):
        self.contract = contract

Recurring.typecode = TC.Struct(Recurring, [
        TC.String(('http://payment.services.adyen.com', 'contract'), nillable=True),
    ], ('http://payment.services.adyen.com', 'recurring'), nillable=True)


class PaymentRequest:
    """Payment Request"""

    def __init__(self, amount, browserInfo, card, merchantAccount, reference, shopperIP, shopperEmail, shopperReference, fraudOffset):
        self.amount = amount
        self.browserInfo = browserInfo
        self.card = card
        self.merchantAccount = merchantAccount
        self.reference = reference
        self.shopperIP = shopperIP
        self.shopperEmail = shopperEmail
        self.shopperReference = shopperReference

PaymentRequest.typecode = TC.Struct(PaymentRequest, [
        Amount.typecode,
        BrowserInfo.typecode,
        Card.typecode,
        TC.String(('http://payment.services.adyen.com',  'merchantAccount')),
        TC.String(('http://payment.services.adyen.com',  'reference')),
        TC.String(('http://payment.services.adyen.com',  'shopperIP'), nillable=True),
        TC.String(('http://payment.services.adyen.com',  'shopperEmail'), nillable=True),
        TC.String(('http://payment.services.adyen.com',  'shopperReference'), nillable=True),
    TC.Integer(('http://payment.services.adyen.com', 'fraudOffset'), nillable=True),
    ], ('http://payment.services.adyen.com', 'paymentRequest'))


class PaymentRequest3d:
    """Payment Request 3d"""

    def __init__(self, md, merchantAccount, paResponse, browserInfo, shopperIP):
        self.md = md
        self.merchantAccount = merchantAccount
        self.paResponse = paResponse
        self.browserInfo = browserInfo
        self.shopperIP = shopperIP

PaymentRequest3d.typecode = TC.Struct(PaymentRequest3d, [
        TC.String(('http://payment.services.adyen.com', 'md')),
        TC.String(('http://payment.services.adyen.com', 'merchantAccount')),
        TC.String(('http://payment.services.adyen.com', 'paResponse')),
        BrowserInfo.typecode,
        TC.String(('http://payment.services.adyen.com', 'shopperIP'), nillable=True),
    ], ('http://payment.services.adyen.com', 'paymentRequest3d'))


class PaymentResult:
    """Payment Result"""

PaymentResult.typecode = TC.Struct(PaymentResult, [
        TC.String(('http://payment.services.adyen.com', 'authCode'), nillable=True),
        TC.String(('http://payment.services.adyen.com', 'pspReference'), nillable=True),
        TC.String(('http://payment.services.adyen.com', 'issuerUrl'), nillable=True),
        TC.String(('http://payment.services.adyen.com', 'md'), nillable=True),
        TC.String(('http://payment.services.adyen.com', 'paRequest'), nillable=True),
        TC.String(('http://payment.services.adyen.com', 'refusalReason'), nillable=True),
        TC.String(('http://payment.services.adyen.com', 'resultCode'), nillable=True),
        FraudResult.typecode,
    ], ('http://payment.services.adyen.com', 'paymentResult'))


class RecurringPaymentRequest:
    """Payment Request"""

    def __init__(self, amount, merchantAccount, reference, shopperEmail, shopperReference, selectedRecurringDetailReference, recurring, shopperInteraction):
        self.amount = amount
        self.merchantAccount = merchantAccount
        self.reference = reference
        self.shopperEmail = shopperEmail
        self.shopperReference = shopperReference
        self.selectedRecurringDetailReference = selectedRecurringDetailReference
        self.recurring = recurring
        self.shopperInteraction = shopperInteraction

RecurringPaymentRequest.typecode = TC.Struct(RecurringPaymentRequest, [
        Amount.typecode,
        Recurring.typecode,
        TC.String(('http://payment.services.adyen.com',  'merchantAccount')),
        TC.String(('http://payment.services.adyen.com',  'reference')),
        TC.String(('http://payment.services.adyen.com',  'shopperEmail'), nillable=True),
        TC.String(('http://payment.services.adyen.com',  'shopperReference'), nillable=True),
        TC.String(('http://payment.services.adyen.com',  'selectedRecurringDetailReference'), nillable=True),
        TC.String(('http://payment.services.adyen.com',  'shopperInteraction'), nillable=True),
    ], ('http://payment.services.adyen.com', 'paymentRequest'))

class AuthoriseResponse:
    """Authorise Response"""

AuthoriseResponse.typecode = TC.Struct(AuthoriseResponse, [
        PaymentResult.typecode,
    ], ('http://payment.services.adyen.com', 'authoriseResponse'))


class Authorise3dResponse:
    """Authorise3d Response"""

Authorise3dResponse.typecode = TC.Struct(Authorise3dResponse, [
        PaymentResult.typecode,
    ], ('http://payment.services.adyen.com', 'authorise3dResponse'))


class CancelRequest:
    """Cancel request"""

    def __init__(self, merchantAccount, originalReference):
        self.merchantAccount = merchantAccount
        self.originalReference = originalReference

CancelRequest.typecode = TC.Struct(CancelRequest, [
        TC.String(('http://payment.services.adyen.com', 'merchantAccount'), nillable=True),
        TC.String(('http://payment.services.adyen.com', 'originalReference'), nillable=True),
    ], ('http://payment.services.adyen.com', 'cancel'))


class CancelResult:
    """Cancel Result"""

CancelResult.typecode = TC.Struct(CancelResult, [
        TC.String(('http://payment.services.adyen.com', 'pspReference'), nillable=True),
        TC.String(('http://payment.services.adyen.com', 'response'), nillable=True),
    ], ('http://payment.services.adyen.com', 'cancelResult'))


class CancelResponse:
    """Cancel Response"""

CancelResponse.typecode = TC.Struct(CancelResponse, [
        CancelResult.typecode,
    ], ('http://payment.services.adyen.com', 'cancelResponse'))


class ModificationAmount:
    """Modification amount"""

    def __init__(self, currency, value):
        self.currency = currency
        self.value = value

ModificationAmount.typecode = TC.Struct(ModificationAmount, [
        TC.String(('http://common.services.adyen.com', 'currency')),
        TC.Ilong(('http://common.services.adyen.com', 'value')),
    ], ('http://payment.services.adyen.com', 'modificationAmount'))


class CaptureRequest:
    """Capture request"""

    def __init__(self, merchantAccount, originalReference, modificationAmount):
        self.merchantAccount = merchantAccount
        self.originalReference = originalReference
        self.modificationAmount = modificationAmount

CaptureRequest.typecode = TC.Struct(CaptureRequest, [
        TC.String(('http://payment.services.adyen.com', 'merchantAccount'), nillable=True),
        TC.String(('http://payment.services.adyen.com', 'originalReference'), nillable=True),
        ModificationAmount.typecode,
    ], ('http://payment.services.adyen.com', 'capture'))


class CaptureResult:
    """Capture Result"""

CaptureResult.typecode = TC.Struct(CaptureResult, [
        TC.String(('http://payment.services.adyen.com', 'pspReference'), nillable=True),
        TC.String(('http://payment.services.adyen.com', 'response'), nillable=True),
    ], ('http://payment.services.adyen.com', 'captureResult'))


class CaptureResponse:
    """Capture Response"""

CaptureResponse.typecode = TC.Struct(CaptureResponse, [
        CaptureResult.typecode,
    ], ('http://payment.services.adyen.com', 'captureResponse'))


class RefundRequest:
    """Refund request"""

    def __init__(self, merchantAccount, originalReference, modificationAmount):
        self.merchantAccount = merchantAccount
        self.originalReference = originalReference
        self.modificationAmount = modificationAmount

RefundRequest.typecode = TC.Struct(RefundRequest, [
        TC.String(('http://payment.services.adyen.com', 'merchantAccount'), nillable=True),
        TC.String(('http://payment.services.adyen.com', 'originalReference'), nillable=True),
        ModificationAmount.typecode,
    ], ('http://payment.services.adyen.com', 'refund'))


class RefundResult:
    """Refund Result"""

RefundResult.typecode = TC.Struct(RefundResult, [
        TC.String(('http://payment.services.adyen.com', 'pspReference'), nillable=True),
        TC.String(('http://payment.services.adyen.com', 'response'), nillable=True),
    ], ('http://payment.services.adyen.com', 'refundResult'))


class RefundResponse:
    """Refund Response"""

RefundResponse.typecode = TC.Struct(RefundResponse, [
        RefundResult.typecode,
    ], ('http://payment.services.adyen.com', 'refundResponse'))
