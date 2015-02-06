from openerp.osv import orm


class ads_cron_manager(orm.Model):
    """
        Yes, this is dirty as hell, but it was the quickest solution to ensure
        we no longer have concurrent transaction problems when both cron jobs
        intrude on each other's timeframes.
    """
    _name = 'ads_cron_manager'
    _description = 'ADS Cron Manager'

    _columns = {
    }

    def sync_ads(self, cr, uid=1):
        self.pool.get('stock.picking').cron_upload_to_ads(cr, uid)
        self.pool.get('ads.manager').poll(cr, uid)

