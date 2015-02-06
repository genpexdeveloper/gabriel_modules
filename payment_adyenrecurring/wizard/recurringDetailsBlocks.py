# -*- coding: utf-'8' "-*-"
from openerp import models, fields, api

class recurringDetailsBlocks(models.TransientModel):
    _name = 'payment_adyenrecurring.recurringdetailsblocks'

    recurringDetail_id = fields.Many2one('payment_adyenrecurring.recurringdetailswizard',
        string="Recurring detail", required=True)
    recurringDetailReference = fields.Char(string="recurring Detail Reference")
    variant = fields.Char(string="variant")
    creationDate = fields.Datetime(string="creation Date")
    holderName = fields.Char(string="holderName")
    expiryMonth = fields.Char(string="expiry Month")
    expiryYear = fields.Char(string="expiry Year")
    cardNumber = fields.Char(string="last 4 digits of card Number")