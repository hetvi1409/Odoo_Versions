from odoo import api, fields, models, Command, _


class DocumentDocument(models.Model):
    _inherit = 'documents.document'

    # def _get_users(self):
    #     """Returns the domain that filter out all the Transient
    #     and Abstract models or the models with no views"""
    #     users = []
    #     users += self.env.ref('base.group_user').users.ids
    #     return [('id', 'in', users)]
    #
    # user_ids = fields.Many2many('res.users', string="Users",
    #                             domain=_get_users)

    def write(self, vals):
        # Capture changes in group_ids
        # before_group_ids = set(self.group_ids.ids)
        # before_read_group_ids = set(self.read_group_ids.ids)
        before_user_ids = set(self.favorited_ids.ids)

        result = super(DocumentDocument, self).write(vals)
        # after_group_ids = set(self.group_ids.ids)
        # after_read_group_ids = set(self.read_group_ids.ids)

        # Calculate added and removed group IDs
        # added_group_ids = after_group_ids - before_group_ids
        # removed_group_ids = before_group_ids - after_group_ids
        # added_read_group_ids = after_read_group_ids - before_read_group_ids
        # removed_read_group_ids = before_read_group_ids - after_read_group_ids
        after_user_ids = set(self.favorited_ids.ids)

        added_user_ids = after_user_ids - before_user_ids
        removed_user_ids = before_user_ids - after_user_ids

        children = self.env['documents.document'].search(
            [('folder_id', '=', self.id)])

        for child in children:
            # Update added group_ids for the child
            # if added_group_ids:
            #     child.group_ids = [Command.link(group_id) for group_id in
            #                        added_group_ids]
            # # Update removed group_ids for the child
            # if removed_group_ids:
            #     child.group_ids = [Command.unlink(group_id) for group_id in
            #                        removed_group_ids]
            # if added_read_group_ids:
            #     child.read_group_ids = [Command.link(group_id) for group_id in
            #                        added_read_group_ids]
            # # Update removed group_ids for the child
            # if removed_read_group_ids:
            #     child.read_group_ids = [Command.unlink(group_id) for group_id in
            #                        removed_read_group_ids]
            # Update added user_ids for the child
            if added_user_ids:
                child.favorited_ids = [Command.link(id) for id in
                                   added_user_ids]
            # Update removed group_ids for the child
            if removed_user_ids:
                child.favorited_ids = [Command.unlink(id) for id in
                                   removed_user_ids]
        return result

    @api.model_create_multi
    def create(self, vals_list):
        """Method for generating consumer number for the contacts"""
        for values in vals_list:
            if values.get('folder_id'):
                values['favorited_ids'] = self.env['documents.document'].browse(
                    values.get('folder_id')).favorited_ids
                # values['group_ids'] = self.env['documents.document'].browse(
                #     values.get('folder_id')).group_ids
                # values['read_group_ids'] = self.env['documents.document'].browse(
                #     values.get('folder_id')).read_group_ids
        return super(DocumentDocument, self).create(vals_list)

    @api.depends('favorited_ids')
    @api.depends_context('uid')
    def _compute_has_write_access(self):
        current_user_groups_ids = self.env.user.group_ids
        has_write_access = self.user_has_groups(
            'documents.group_documents_manager')
        if has_write_access:
            self.has_write_access = True
            return
        # for record in self:
        #     if not record.group_ids and not record.read_group_ids and not record.favorited_ids:
        #         folder_has_groups = False
        #     else:
        #         folder_has_groups = (
        #                     (record.group_ids & current_user_groups_ids) or (
        #                         self.env.user in record.favorited_ids))
        #     record.has_write_access = folder_has_groups
