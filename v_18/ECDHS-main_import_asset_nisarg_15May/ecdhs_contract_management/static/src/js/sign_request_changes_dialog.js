/** @odoo-module **/

import { Dialog } from "@web/core/dialog/dialog";
import { useEffect, useState } from "@odoo/owl";

/**
 * ECDHS Contract Management – Request Changes Dialog (7.2)
 *
 * Allows providers to request contract updates/changes before signing.
 * Shows a modal with a text field for specifying the requested changes
 * and validates the input before submission.
 */
export class SignRequestChangesDialog extends Dialog {
	static components = { Dialog };
	static template = "ecdhs_contract_management.SignRequestChangesDialog";

	setup() {
		super.setup();
		this.state = useState({
			changeReason: "",
			isSubmitting: false,
			error: null,
		});
	}

	/**
	 * Validate change reason before submission.
	 * Requires at least one real word (2+ alphabetic characters).
	 */
	isValidReason() {
		const trimmed = (this.state.changeReason || "").trim();
		if (!trimmed) return false;
		// Match at least one sequence of two or more alphabetic characters
		return /[a-zA-Z]{2,}/.test(trimmed);
	}

	/**
	 * Submit the change request via RPC.
	 */
	async submitChangeRequest() {
		const reason = (this.state.changeReason || "").trim();

		if (!this.isValidReason()) {
			this.state.error =
				"A reason is required and must contain at least one real word.";
			return;
		}

		this.state.isSubmitting = true;
		this.state.error = null;

		try {
			const result = await this.rpc({
				model: "sign.request",
				method: "action_request_changes",
				args: [this.props.signRequestId, reason],
			});

			if (result) {
				// Show success message
				this.props.onSuccess && this.props.onSuccess(result);
				this.close();
			} else {
				this.state.error =
					"Failed to submit change request. Please try again.";
			}
		} catch (error) {
			this.state.error = error.message || "An error occurred.";
		} finally {
			this.state.isSubmitting = false;
		}
	}

	/**
	 * Handle keydown events in the text area.
	 */
	onKeyDown(event) {
		if (event.key === "Enter" && event.ctrlKey) {
			// Ctrl+Enter to submit
			this.submitChangeRequest();
		}
	}
}

// Register the dialog component
SignRequestChangesDialog.isXML = false;
