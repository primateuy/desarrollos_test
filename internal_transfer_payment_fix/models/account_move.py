# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import logging

_logger = logging.getLogger(__name__)


class AccountInvoiceLine(models.Model):
    _inherit = 'account.move.line'

    def _check_constrains_account_id_journal_id(self):
        # Avoid using api.constrains for fields journal_id and account_id as in case of a write on
        # account move and account move line in the same operation, the check would be done
        # before all write are complete, causing a false positive
        self.flush_recordset()
        for line in self.filtered(lambda x: x.display_type not in ('line_section', 'line_note')):
            account = line.account_id
            journal = line.move_id.journal_id

            if account.deprecated and not self.env.context.get('skip_account_deprecation_check'):
                raise UserError(_('The account %s (%s) is deprecated.', account.name, account.code))

            account_currency = account.currency_id
            if account_currency and account_currency != line.company_currency_id and account_currency != line.currency_id:
                raise UserError(_('The account selected on your journal entry forces to provide a secondary currency. '
                                  'You should remove the secondary currency on the account.'))

            if account.allowed_journal_ids and journal not in account.allowed_journal_ids:
                raise UserError(_('You cannot use this account (%s) in this journal, check the field \'Allowed Journals\' '
                                  'on the related account.', account.display_name))

            if account in (journal.default_account_id, journal.suspense_account_id):
                continue

            is_account_control_ok = not journal.account_control_ids or account in journal.account_control_ids

            if not is_account_control_ok:
                raise UserError(_("You cannot use this account (%s) in this journal, check the section 'Control-Access' under "
                                  "tab 'Advanced Settings' on the related journal.", account.display_name))
