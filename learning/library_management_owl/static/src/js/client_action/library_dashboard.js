/** @odoo-module **/
import { registry } from '@web/core/registry';
import { Component, onWillStart, useState } from "@odoo/owl";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";
import { useService } from "@web/core/utils/hooks";


export class LibraryManagmentDashboard extends Component {
    static template = 'library_management_owl.library_dashboard_template';
    static props = {...standardActionServiceProps,};


    setup() {
        // super.setup();
        this.state = useState({
            totalBooks: 0,
            borrowedBooks: 0,
            availableBooks: 0,
        });
        // console.log('THIS>STATE',this.state);

        this.actionService = useService("action");

        // onWillStart(async () => {
        //     await this.loadData();
        // });
    }

    async loadData() {
        const orm = useService('orm');
        console.log('ORM SERVICE:', orm);
        const result = await orm.call(
            'library.book',
            'get_book_stats',
            []
        );
        console.log('Book Stats:', result);
        // this.state.totalBooks = result.total_books;
        // this.state.borrowedBooks = result.borrowed_books;
        // this.state.availableBooks = result.available_books;
    }

    onButtonClicked(event) {
        alert('Button Clicked in Library Dashboard!');
        console.log('Button Clicked:', event);
    }

}

registry.category('actions').add('library_management_owl.library_dashboard', LibraryManagmentDashboard);