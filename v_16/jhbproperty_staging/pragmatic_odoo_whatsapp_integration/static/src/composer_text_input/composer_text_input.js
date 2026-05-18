/** @odoo-module **/

import { useRefToModel } from '@mail/component_hooks/use_ref_to_model';
import { useUpdate } from '@mail/component_hooks/use_update';
import { registerMessagingComponent } from '@mail/utils/messaging_component';
import { isEventHandled, markEventHandled } from '@mail/utils/utils';

const { Component } = owl;

export class WhatsappComposerTextInput extends Component {

    /**
     * @override
     */
    setup() {
        super.setup();
        useRefToModel({ fieldName: 'mirroredTextareaRef', refName: 'mirroredTextarea' });
        useRefToModel({ fieldName: 'textareaRef', refName: 'textarea' });
        /**
         * Updates the composer text input content when composer is mounted
         * as textarea content can't be changed from the DOM.
         */
        useUpdate({ func: () => this._update() });
    }

    //--------------------------------------------------------------------------
    // Public
    //--------------------------------------------------------------------------

    /**
     * @returns {ComposerView}
     */
    get composerView() {
        return this.props.record;
    }

    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * Determines whether the textarea is empty or not.
     *
     * @private
     * @returns {boolean}
     */
    _isEmpty() {
        return this.composerView.textareaRef.el.value === "";
    }

    onKeydownTextarea(ev) {
        if (!this.composerView.exists()) {
            return;
        }
        switch (ev.key) {
            case 'Escape':
                if (this.composerView.hasSuggestions) {
                    ev.preventDefault();
                    this.composerView.closeSuggestions();
                    markEventHandled(ev, 'ComposerTextInput.closeSuggestions');
                }
                break;
            // UP, DOWN, TAB: prevent moving cursor if navigation in mention suggestions
            case 'ArrowUp':
            case 'PageUp':
            case 'ArrowDown':
            case 'PageDown':
            case 'Home':
            case 'End':
            case 'Tab':
                if (this.composerView.hasSuggestions) {
                    // We use preventDefault here to avoid keys native actions but actions are handled in keyUp
                    ev.preventDefault();
                }
                break;
            // ENTER: submit the message only if the dropdown mention proposition is not displayed
            case 'Enter':
                this.composerView.postMessage();
                break;
        }
    }

    /**
     * Updates the content and height of a textarea
     *
     * @private
     */
    _update() {
        if (!this.root.el) {
            return;
        }
        if (this.composerView.doFocus) {
            this.composerView.update({ doFocus: false });
            if (this.messaging.device.isSmall) {
                this.root.el.scrollIntoView();
            }
            this.composerView.textareaRef.el.focus();
        }
        if (this.composerView.hasToRestoreContent) {
            this.composerView.textareaRef.el.value = this.composerView.composer.textInputContent;
            if (this.composerView.isFocused) {
                this.composerView.textareaRef.el.setSelectionRange(
                    this.composerView.composer.textInputCursorStart,
                    this.composerView.composer.textInputCursorEnd,
                    this.composerView.composer.textInputSelectionDirection,
                );
            }
            this.composerView.update({ hasToRestoreContent: false });
        }
        this.composerView.updateTextInputHeight();
    }

}

Object.assign(WhatsappComposerTextInput, {
    props: { record: Object },
    template: 'whatsapp.ComposerTextInput',
});

registerMessagingComponent(WhatsappComposerTextInput);
