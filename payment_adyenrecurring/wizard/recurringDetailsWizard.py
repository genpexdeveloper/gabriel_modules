# -*- coding: utf-'8' "-*-"
from openerp import models, fields, api

class recurringDetailsWizard(models.TransientModel):
    _name = 'payment_adyenrecurring.recurringdetailswizard'

    def _default_autoship(self):
        return self.env['ip_web_addons.auto_ship'].browse(self._context.get('active_id'))
    
    def _default_blocks(self):
        active_id = self._context.get('active_id')
        res_blocks = self.env['ip_web_addons.auto_ship'].retrieve_reccurent_details(active_id)
        toReturn = []
        for block in res_blocks:
            block['recurringDetail_id'] = active_id
            toReturn.append([0, 0, block])
        return toReturn
    
    autoship_id = fields.Many2one('ip_web_addons.auto_ship',
        string="Auto ship", required=True, default=_default_autoship)
    block_ids = fields.One2many('payment_adyenrecurring.recurringdetailsblocks', 
                                'recurringDetail_id', string="Details", 
                                default=_default_blocks)