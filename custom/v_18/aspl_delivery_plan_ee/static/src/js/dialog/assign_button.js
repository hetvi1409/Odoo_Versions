import { Component, useState } from "@odoo/owl";
import { Dialog } from "@web/core/dialog/dialog";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { session } from "@web/session";

export class AssignDriverPopup extends Component {
  static props = {
    title: String,
    assignDeliveryOrders: Array,
    assignDeliveryDate: String,
    _setLocationsInMap: Function,
    _setLocationsInGoogleMap: Function,
    close: Function,
    loggedInUserLocation: Array,
    PriorityOrders: Array,
    mapProvider : String,
    removedOrderIds: { type: Array, optional: true },
  };

  async setup() {
    super.setup(...arguments);
    this.state = useState({
      selectedDriver: null,
      sequence: 1,
      orders: [],
      resUsers: [],
      removedOrderIds: this.props.removedOrderIds || [],
    });
    this.orm = useService("orm");
    this.loadDrivers();
    this.loadOrders();
    this.state.resUsers = await this.orm.searchRead(
      "res.users",
      [],
      ["id", "name"]
    );
    this.uid = session.storeData.Store.settings.user_id.id;
  }

  async loadDrivers() {
    try {
      const drivers = await this.orm.searchRead("res.users", [], ["name"]);
      this.state.drivers = drivers;
    } catch (error) {
      console.error("Error loading drivers:", error);
    }
  }

  async loadOrders() {
    try {
      this.state.orders = this.props.PriorityOrders;
    } catch (error) {
      console.error("Error loading orders:", error);
    }
  }

  async assignDriver() {
    let self = this
    let data = [];
    $("tr.assign-order-line").each((index, line) => {
      data.push({
        sequence: parseInt(
          $(line).find("td.sequence").attr("data-sequence"),
          10
        ),
        customer_id: parseInt(
          $(line).find("td.cust-partner-name").attr("data-partner-id"),
          10
        ),
        order_id: parseInt(
          $(line).find("td.delivery-order").attr("data-order-id"),
          10
        ),
      });
    });
    const driver = $("select.user-select").val();
    const sequence = $("td.sequence");
    if (data.length > 0) {
      const locations = await this.orm.call(
        "assign.delivery",
        "create_assign_delivery",
        [, self.props.loggedInUserLocation, [parseInt(driver, 10), self.props.assignDeliveryDate, data],sequence]
      );
      if (this.props.mapProvider === "google") {
          this.props._setLocationsInGoogleMap(locations);
        } else if (this.props.mapProvider === "leaflet") {
          this.props._setLocationsInMap(locations);
        } else {
          console.warn("No valid map provider selected.");
        }
    }

    this.state.selectedDriver = null;
    this.state.sequence = 1;
    this.state.orders = [];
    this.props.close();
    window.location.reload();
  }

  closePopup() {
    this.state.selectedDriver = null;
    this.state.sequence = 1;
    this.state.pr
    this.state.orders = [];
    this.props.close(this.state.removedOrderIds || []);
    window.location.reload();
  }

  removeOrderLine(event) {
    const row = event.target.closest("tr")
    const orderCell = row.querySelector("td.delivery-order");
    const orderId = orderCell ? parseInt(orderCell.getAttribute("data-order-id"), 10) : null;
    if (!this.state.removedOrderIds) {
        this.state.removedOrderIds = [];
    }
    event.target.closest("tr").remove();

    $("td.sequence").each((index, seq) => {
      $(seq).html(index + 1 + ".");
    });
  }
}

AssignDriverPopup.template = "aspl_delivery_plan_ee.assign_driver_popup";
AssignDriverPopup.components = { Dialog };