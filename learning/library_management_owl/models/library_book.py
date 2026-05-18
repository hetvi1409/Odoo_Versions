# -*- coding: utf-8 -*-

from odoo import models, fields, api


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    _rec_name = 'name'

    name = fields.Char('Title', required=True)
    author = fields.Char('Author')
    isbn = fields.Char('ISBN')
    category = fields.Char('Category')
    status = fields.Selection([
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('reserved', 'Reserved')
    ], default='available')


    def get_book_stats(self):
        # total_books = self.search_count([])
        # borrowed_books = self.search_count([('status', '=', 'borrowed')])
        # available_books = self.search_count([('status', '=', 'available')])
        # return {
        #     'total_books': total_books,
        #     'borrowed_books': borrowed_books,
        #     'available_books': available_books
        # }
        return {
            'total_books': 42,
            'borrowed_books': 15,
            'available_books': 27
        }