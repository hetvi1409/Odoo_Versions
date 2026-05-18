/** @odoo-module **/

import { patch } from "@web/core/utils/patch";
import { normalizePosition, generateRandomId } from "@sign/components/sign_request/utils";
import { SignTemplateIframe } from "@sign/backend_components/sign_template/sign_template_iframe";
import { SignTemplate } from "@sign/backend_components/sign_template/sign_template_action";
import { SearchableRoleDialog } from "@ecdhs_contract_management/js/searchable_role_dialog";

/**
 * ECDHS Contract Management – Sign editor compatibility shim.
 *
 * Reuses the same role-selection dialog flow used by Initials for all dropped
 * sign field types in template edition. This avoids the failing popover path
 * users reported for signature/date/text/checkbox/radio/selection insertion.
 */
patch(SignTemplateIframe.prototype, {
	openDialogAfterInitialDrop(data) {
		this.dialog.add(SearchableRoleDialog, {
			addRole: (role, targetAllPages) => {
				data.responsible = role;
				this.currentRole = role;
				this.addInitialSignItem(data, targetAllPages);
			},
			responsible: this.currentRole,
			roles: this.signRolesById,
			pageCount: this.pageCount,
			title: "Add Initials",
		});
	},

	onDrop(e) {
		const page = e.target.closest(".page");
		if (!page) {
			return;
		}
		const targetPage = Number(page.dataset.pageNumber);
		e.preventDefault();

		if (!this.allowEdit) {
			return;
		}

		const { top, left, width, height } = page.getBoundingClientRect();

		if (e.dataTransfer.getData("typeId")) {
			const typeId = Number(e.dataTransfer.getData("typeId"));
			const id = generateRandomId();
			const signItemType = this.signItemTypesById[typeId];
			const data = {
				type_id: [typeId, signItemType.item_type],
				type: signItemType.item_type,
				id,
				page: targetPage,
				posX: Math.round(normalizePosition((e.pageX - left) / width, 0.15) * 1000) / 1000,
				posY: Math.round(normalizePosition((e.pageY - top) / height, 0.05) * 1000) / 1000,
				width: signItemType.default_width,
				height: signItemType.default_height,
				required: true,
				placeholder: signItemType.display_name,
				option_ids: [],
				alignment: "left",
				responsible: this.currentRole,
				isSignItemEditable: true,
				name: signItemType.display_name,
				selected: false,
				updated: true,
			};

			this.setCanvasVisibility("visible");

			if (data.type === "initial") {
				this.helperLines.hide();
				if (this.pageCount > 1) {
					return this.openDialogAfterInitialDrop(data);
				}
			} else if (data.type === "radio") {
				this.helperLines.hide();
				return this.openDialogAfterRoleDrop(data);
			} else {
				this.helperLines.hide();
				return this.openDialogAfterRoleDrop(data);
			}

			this.signItems[targetPage][id] = {
				data,
				el: this.renderSignItem(data, page),
			};
			this.refreshSignItems();
			this.saveChanges();
			return;
		}

		if (e.dataTransfer.getData("page") && e.dataTransfer.getData("id")) {
			return super.onDrop(e);
		}
	},

	openDialogAfterRoleDrop(data) {
		this.dialog.add(SearchableRoleDialog, {
			addRole: (role, targetAllPages) => {
				data.responsible = role;
				this.currentRole = role;

				if (data.type === "radio") {
					this.addRadioSet(data);
					return;
				}

				if (targetAllPages && this.pageCount > 1) {
					for (let page = 1; page <= this.pageCount; page++) {
						const id = generateRandomId();
						const signItemData = { ...data, page, id, updated: true };
						this.signItems[page][id] = {
							data: signItemData,
							el: this.renderSignItem(signItemData, this.getPageContainer(page)),
						};
					}
					this.refreshSignItems();
					this.saveChanges();
					return;
				}

				this.signItems[data.page][data.id] = {
					data,
					el: this.renderSignItem(data, this.getPageContainer(data.page)),
				};
				this.refreshSignItems();
				this.saveChanges();
			},
			responsible: this.currentRole,
			roles: this.signRolesById,
			pageCount: this.pageCount,
			title: "Select Responsible",
		});
	},
});

patch(SignTemplate.prototype, {
	async fetchSignRoles() {
		this.signRoles = await this.orm.call("sign.item.role", "search_read", [], {
			context: {
				...this.props.context,
				sign_template_id: this.signTemplate?.id,
				restrict_contract_sign_roles: true,
			},
		});
	},
});
