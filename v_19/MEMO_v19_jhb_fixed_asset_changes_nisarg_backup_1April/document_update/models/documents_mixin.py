from odoo import models


class DocumentMixin(models.AbstractModel):
    """
    Inherit this mixin to automatically create a `documents.document` when
    an `ir.attachment` is linked to a record.
    """
    _inherit = 'documents.mixin'

    def _get_document_vals(self, attachment):
        """
        Return values used to create a `documents.document`
        """
        self.ensure_one()
        document_vals = {}
        if self._check_create_documents():
            document_vals = {
                'attachment_id': attachment.id,
                'name': attachment.name or self.display_name,
                'folder_id': self._get_document_folder().id,
                'owner_id': self._get_document_owner().id,
                'partner_id': self._get_document_partner().id,
                'tag_ids': [(6, 0, self._get_document_tags().ids)],
                'jmc_property_id': self._get_document_jmc_property().id,
            }
        return document_vals
    # def _get_document_vals(self, attachment):
    #     """return the values."""
    #     res = super()._get_document_vals()
    #     if self._check_create_documents():
    #         res['jmc_property_id'] = self._get_document_property().id
    #     return res

    def _get_document_jmc_property(self):
        """"""
        return self.env['building']
