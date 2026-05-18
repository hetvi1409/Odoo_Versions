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
    const data = [];

    const rows = document.querySelectorAll("tr.assign-order-line");

    rows.forEach((line) => {
        const sequenceEl = line.querySelector("td.sequence");
        const customerEl = line.querySelector("td.cust-partner-name");
        const orderEl = line.querySelector("td.delivery-order");

        if (!sequenceEl || !customerEl || !orderEl) {
            return;
        }

        data.push({
            sequence: parseInt(sequenceEl.dataset.sequence, 10),
            customer_id: parseInt(customerEl.dataset.partnerId, 10),
            order_id: parseInt(orderEl.dataset.orderId, 10),
        });
    });

    const driverSelect = document.querySelector("select.user-select");
    const driver = driverSelect ? parseInt(driverSelect.value, 10) : null;

    // Optional: sequence elements (same as your original code)
    const sequence = document.querySelectorAll("td.sequence");

    if (data.length > 0 && driver) {
        const locations = await this.orm.call(
            "assign.delivery",
            "create_assign_delivery",
            [
                [],
                this.props.loggedInUserLocation,
                [driver, this.props.assignDeliveryDate, data],
                sequence,
            ]
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