/** @odoo-module **/
import { registerMessagingComponent } from '@mail/utils/messaging_component';
import { WithSearch } from "@web/search/with_search/with_search";
import { useUpdate } from '@mail/component_hooks/use_update/use_update';
import { useRenderedValues } from '@mail/component_hooks/use_rendered_values/use_rendered_values';
// import { registry } from "@web/core/registry";
// import { Layout } from "@web/views/layout";
// import { KeepLast } from "@web/core/utils/concurrency";
// import { Model, useModel } from "@web/views/helpers/model";
// import { session } from "@web/session";
// import { useService } from "@web/core/utils/hooks";
import { _t } from 'web.core';
const { Component } = owl;
const { useRef } = owl.hooks;

export class ContactViews extends Component {
    constructor(...args) {
        super(...args);
        this.products;
    }

    setup() {
        const { arch, fields, resModel, searchViewArch, searchViewFields, type } = this.props;
        this._isLastScrollProgrammatic = false;
        this._willPatchSnapshot = undefined;
        this._lastRenderedValues = useRenderedValues(() => {
            const messageView = this.messageView;
            const thread = messageView;
            const threadCache = messageView;
            return {
                componentHintList: messageView,
                hasScrollAdjust: true,
                messageView,
            };
        });
        // useUpdate({ func: () => this._isProductSearch() });
        // ...
    }

    willPatch() {
        this._willPatchSnapshot = {
            scrollHeight: this._getScrollableElement().scrollHeight,
            scrollTop: this._getScrollableElement().scrollTop,
        };
    }

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------


    /**
     * @returns {integer}
     */
     getScrollHeight() {
        return this._getScrollableElement().scrollHeight;
    }

    /**
     * @returns {integer}
     */
    getScrollTop() {
        return this._getScrollableElement().scrollTop;
    }

    /**
     * @param {integer} value
     */
    setScrollTop(value) {
        if (this._getScrollableElement().scrollTop === value) {
            return;
        }
        this._isLastScrollProgrammatic = true;
        this._getScrollableElement().scrollTop = value;
    }

    
    get contactView() {
        // var self = this;
        // var data = null;
        // var def = this.rpc({
        //     model: 'product.template',
        //     method: 'search_read',
        //     domain: [],
        // }).then(function (result) {
        //     console.log("products ---------",result);
        //     self.products = result;
            
        // });
        // console.log(this.products);
        this.willStart();
        // console.log(this.products);
        return _.map(this.products, (value) => value);
        // return this.products;
        // return this.messaging && this.messaging.models['mail.message_view'].get(this.props.messageViewLocalId);
    }

    async willStart() {
        var self = this;
        var data = null;
        var def = await this.rpc({
            model: 'res.partner',
            method: 'search_read',
            domain: [],
        }).then(function (result) {
            // console.log("will start ---------",result);
            data = result;
            self.products = result;
        });
        // console.log(def);
        // return Promise.all([def]);
    //...
    }


    //--------------------------------------------------------------------------
    // Private
    //-------------------------------------------------------------------------

    /**
     * This method will check if the productId needs a configuration or not.
     *
     * 
     * 
     * 
     *
     * @private
     */
    _isProductSearch = function () {
        var self = this;
        var def = this.rpc({
            model: 'res.partner',
            method: 'search_read',
            domain: [],
        }).then(function (result) {
            console.log("products ---------",result);
            self.products = result;
            // var currentDate = new Date();
            // var duration = 0;
            // if (result.length > 0) {
            //     duration += self._getDateDifference(time.auto_str_to_date(result[0].date_start), currentDate);
            // }
            // var minutes = duration / 60 >> 0;
            // var seconds = duration % 60;
            // self.duration += minutes + seconds / 60;
            // if (self.mode === 'edit') {
            //     self.value = self.duration;
            // }
        });
        // return Promise.all([def]);
    }

    /**
     * @private
     */
     _adjustScrollForExtraMessagesAtTheEnd() {
        const {
            hasScrollAdjust,
        } = this._lastRenderedValues();
        if (!this._getScrollableElement() || !hasScrollAdjust) {
            return;
        }
        this._scrollToEnd();
    }

    /**
     * @private
     */
    _adjustScrollForExtraMessagesAtTheStart() {
        const {
            hasScrollAdjust,
        } = this._lastRenderedValues();
        if (
            !this._getScrollableElement() ||
            !hasScrollAdjust ||
            !this._willPatchSnapshot
        ) {
            return;
        }
        const { scrollHeight, scrollTop } = this._willPatchSnapshot;
        this.setScrollTop(this._getScrollableElement().scrollHeight - scrollHeight + scrollTop);
    }

    /**
     * @private
     */
    _adjustScrollFromModel() {
        const {
            hasScrollAdjust,
            threadCacheInitialScrollHeight,
            threadCacheInitialScrollPosition,
        } = this._lastRenderedValues();
        if (!this._getScrollableElement() || !hasScrollAdjust) {
            return;
        }
        this._scrollToEnd();
        return;
    }

    /**
     * @private
     * @returns {Element|undefined} Scrollable Element
     */
    _getScrollableElement() {
        if (this.props.getScrollableElement) {
            return this.props.getScrollableElement();
        } else {
            return this.el;
        }
    }

    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------

    
}
// Views.template = 'basic.View';
ContactViews.components = { WithSearch };

Object.assign(ContactViews, {
    props: {
        getScrollableElement: {
            type: Function,
            optional: true,
        },
        // ResModel: String,
    },
    template: 'basic.contactsView',
});

registerMessagingComponent(ContactViews);
