/** @odoo-module */

import { _t } from "@web/core/l10n/translation";
import { BarcodeScanner } from "@barcodes/components/barcode_scanner";
import { Component, onWillStart, useState } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { standardActionServiceProps } from "@web/webclient/actions/action_service";
import { AssignDriverPopup } from "@aspl_delivery_plan_ee/js/dialog/assign_button";
import { session } from "@web/session";
import { onMounted } from "@odoo/owl";
import { user } from "@web/core/user";


export class DeliveryPlan extends Component {
  static template = "aspl_delivery_plan_ee.DeliveryTemplate";
  static components = { BarcodeScanner };
  static props = { ...standardActionServiceProps };

  setup() {
    super.setup(...arguments);
    this.user = user;

    this.state = useState({
      formatedDate: new Date().toISOString().split("T")[0],
      selectedWarehouseId: null,
      warehouses: [],
      selectedOrderLines: [],
      storedCustomers: [],
      customers: [],
      informationPopupData: {},
      loggedInUserLocation: [],
      locationsPriorityOrders: {},
      company_name: "",
      company_address: "",
      company_phone: "",
      color_scheme: "",
    });

    this.dialog = useService("dialog");
    this.notification = useService("notification");
    this.orm = useService("orm");
    this.markers = [];
    this.routingControls = [];
    this.loadCustomerData();
    this.bindCloseButton();
    this.fetchLoggedinSourceLocation();
    this.getMapConfig().then((config) => {
      this.mapType = (
        config["aspl_delivery_plan_ee.map_type"] || "leaflet"
      ).toLowerCase();
      this.googleApiKey = config["aspl_delivery_plan_ee.api_key"] || null;
      this.initializeMap();
    });

    onMounted(async () => {
      try {
        const uid = this.uid;
        console.log("Logged-in User ID:", uid);
        const userData = await this.orm.call("res.users", "read", [[uid], ["partner_id","color_scheme"]]);
        const partnerId = userData[0]?.partner_id?.[0];
        if (partnerId) {
          const partnerData = await this.orm.call("res.partner", "read", [[partnerId], ["name", "street", "phone", "city", "country_id", "partner_latitude", "partner_longitude"]]);
          const partner = partnerData[0];
          this.state.company_name = partner.name;
          console.log("User's Company Name:", this.state.company_name);

          this.state.color_scheme = userData[0]?.color_scheme || "light";

          this.state.company_address = `${partner.street || ""}, ${partner.city || ""}, ${partner.country_id?.[1] || ""}`;
          this.state.company_phone = partner.phone || "";
          if (partner.partner_latitude && partner.partner_longitude) {
            this.state.loggedInUserLocation = [partner.partner_latitude, partner.partner_longitude];
          } else {
            console.warn("User does not have coordinates set.");
          }
        }
      } catch (error) {
        console.error("Error fetching user/company data:", error);
      }
    });
  }

  async getMapConfig() {
    const keys = [
      "aspl_delivery_plan_ee.map_type",
      "aspl_delivery_plan_ee.api_key",
    ];
    const values = {};
    for (const key of keys) {
      values[key] = await this.orm.call("ir.config_parameter", "get_param", [key,]);
    }
    return values;
  }

  updateWarehouse(ev) {
    const selectedId = parseInt(ev.target.value);
    this.state.selectedWarehouseId = selectedId;

    const selectedWarehouse = this.state.warehouses.find(
        (w) => w.id === selectedId
    );

    if (selectedWarehouse) {
      const warehouseId = parseInt(event.target.value);
      this.state.selectedWarehouseId = warehouseId || null;
      this.loadCustomerData();
        this.state.company_name = selectedWarehouse.name;
        this.state.company_address = [
            selectedWarehouse.street,
            selectedWarehouse.city,
            selectedWarehouse.zip,
            selectedWarehouse.state_id?.[1],
            selectedWarehouse.country_id?.[1],
        ]
            .filter(Boolean)
            .join(", ");
        if (selectedWarehouse.latitude && selectedWarehouse.longitude) {
            this.state.loggedInUserLocation = [
                parseFloat(selectedWarehouse.latitude),
                parseFloat(selectedWarehouse.longitude),
            ];
        } else {
            console.warn("Warehouse location coordinates are missing.");
        }
      } else {
        // Reset fallback values
        this.state.company_name = "Your Company";
        this.state.company_address = "Unknown Address";
        this.state.loggedInUserLocation = [0, 0]; // or browser geolocation fallback
      }
      this._setLocationsInMap(this.state.locationsPriorityOrders || []);
  }

  initializeMap() {
    const containerCheck = () => {
      const container = document.getElementById("map");
      if (!container) {
        setTimeout(containerCheck, 500);
      } else {
        if (this.mapType === "google map" && this.googleApiKey) {
          this.loadGoogleMap();
        } else {
          this.loadMap();
        }
      }
    };
    containerCheck();
  }

  loadGoogleMap() {
    this.mapProvider = "google";
    const mapContainer = document.getElementById("map");
    const script = document.createElement("script");
    script.src = `https://maps.googleapis.com/maps/api/js?key=${this.googleApiKey}`;

    script.onload = async () => {
      this.map = new google.maps.Map(mapContainer, {
        center: { lat: 23.176782342345028, lng: 72.62920203545316 },
        zoom: 13,
      });
      this.sourceIcon = L.icon({
      iconSize: [40, 40], // Size of the icon
      iconAnchor: [20, 40], // Anchor point of the icon (to align it properly)
      popupAnchor: [0, -40], // Anchor point of the popup relative to the icon
    });
    this.destIcon = L.icon({
      iconSize: [40, 40], // Size of the icon
      iconAnchor: [20, 40], // Anchor point of the icon (to align it properly)
      popupAnchor: [0, -40], // Anchor point of the popup relative to the icon
    });
      // Make sure prepareDeliveries exists and returns expected data
      const filteredOrders = this.prepareDeliveries
        ? this.prepareDeliveries()
        : [];

      try {
        const locations = await this.orm.call(
          "assign.delivery",
          "process_delivery",
          [null, this.state.loggedInUserLocation, filteredOrders]
        );
        this._setLocationsInGoogleMap(locations);
      } catch (error) {
        console.error("Error fetching delivery locations:", error);
      }
    };
    document.head.appendChild(script);
  }

  _setLocationsInGoogleMap(locations) {
    if (this.markers && this.markers.length > 0) {
      this.markers.forEach((marker) => marker.setMap(null));
    }
    this.markers = [];
    if (this.directionsRenderers && this.directionsRenderers.length > 0) {
      this.directionsRenderers.forEach((renderer) => renderer.setMap(null));
    }
    this.directionsRenderers = [];

    const source = this.state.loggedInUserLocation;
    const sourceMarker = new google.maps.Marker({
      position: { lat: source[0], lng: source[1] },
      map: this.map,
      icon: this.sourceIcon,
      title: "Your Location",
    });

    // Define the HTML content for the InfoWindow
    const contentString = `
      <div style="
                  font-size: 14px;
                  font-family: 'Odoo', Arial, sans-serif;
                  background: #ffffff;
                  max-width: 250px;">
        <div style="font-size: 16px; font-weight: bold; color: #714B67; margin-bottom: 8px;">
          📍 Your Location
        </div>
        <div style="color: white;
            font-weight: bold;
            font-size: 16px;
            margin-bottom: 5px;
            background-color: #714B67;
            border-radius: 5px;
            padding: 5px;">
            <div>${this.state.company_name}</div>
        </div>
        <div style="margin-bottom: 5px;">
          <strong style="color: #6c757d;">Address:</strong>
          <span style="color: #333;">${this.state.company_address}</span>
        </div>
      </div>
    `;

    // Create the InfoWindow
    const infoWindow = new google.maps.InfoWindow({
      content: contentString,
    });

    // Open the InfoWindow immediately
    infoWindow.open(this.map, sourceMarker);

    // Optional: Click to reopen InfoWindow
    sourceMarker.addListener("click", () => {
      infoWindow.open(this.map, sourceMarker);
    });

    this.markers.push(sourceMarker);

    Object.entries(locations).forEach(([partner_id, orders]) => {
      const order = orders["orders"][0];
      const latlng = order.cordinates;

      const customerName = order.partner_name || "Unknown";
      const priority = orders.priority || "N/A";
      const address = order.address || "No Address";
      const orderList = orders.orders
        .map((o) => `<li>${o.order}</li>`)
        .join("");

      const contentString = `
      <div style="
                font-size: 14px;
                font-family: 'Odoo', Arial, sans-serif;
                background: #ffffff;
                max-width: 250px;
              ">

              <div style="color: white;
              font-weight: bold;
              font-size: 16px;
              margin-bottom: 5px;
              background-color: #714B67;
              border-radius: 5px;padding: 5px;">
                <div>${customerName}</div>
              </div>

              <div style="margin-bottom: 5px;">
                <strong style="color: #6c757d;">Priority:</strong>
                <span style="color: #017e84; font-weight: bold;">${priority}</span>
              </div>

              <div style="margin-bottom: 5px;">
                <strong style="color: #6c757d;">Address:</strong>
                <span style="color: #333;">${address}</span>
              </div>

              <div>
                <strong style="color: #6c757d;">Orders:</strong>
                <div style="
                    max-height: 100px;
                    overflow-y: auto;
                    border: 1px solid #d5d8dc;
                    padding: 5px;
                    border-radius: 5px;
                    background: #017e84;
                    margin-top: 5px;
                    color: white;
                  ">
                  <ul style="
                      margin: 0;
                      padding-left: 15px;
                      list-style-type: none;
                    ">
                    ${orderList}
                  </ul>
                </div>
              </div>
            </div>
          `;

      const infoWindow = new google.maps.InfoWindow({ content: contentString });
      let customDestIcon =  {
        path: "M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7zm0 9.5c-1.38 0-2.5-1.12-2.5-2.5S10.62 6.5 12 6.5s2.5 1.12 2.5 2.5S13.38 11.5 12 11.5z",
        scale: 1.5,
        fillColor: 'black',
        fillOpacity: 1,
        strokeWeight: 1,
        strokeColor: 'black',
        anchor: new google.maps.Point(12, 24),
      };
      const marker = new google.maps.Marker({
        position: { lat: latlng[0], lng: latlng[1] },
        map: this.map,
        icon: customDestIcon,
        title: customerName,
        label: {
          text: String(priority),
          color: "black",
          fontWeight: "bold",
          fontSize: "14px",
        }
      });

      marker.addListener("click", () => {
        infoWindow.open(this.map, marker);
      });

      this.markers.push(marker);

      // Optional: add route from source to destination
      const directionsService = new google.maps.DirectionsService();
      const directionsRenderer = new google.maps.DirectionsRenderer({
        suppressMarkers: true,
      });
      directionsRenderer.setMap(this.map);
      this.directionsRenderers.push(directionsRenderer);

      directionsService.route(
        {
          origin: { lat: source[0], lng: source[1] },
          destination: { lat: latlng[0], lng: latlng[1] },
          travelMode: google.maps.TravelMode.DRIVING,
        },
        (result, status) => {
          if (status === "OK") {
            directionsRenderer.setDirections(result);
          } else {
            console.error("Directions request failed due to", status);
          }
        }
      );
    });
  }


    loadMap() {
        let self = this;
        this.mapProvider = "leaflet";

        if (!document.getElementById("map")) {
            console.error("Map container not found!!");
            setTimeout(() => this.loadMap(), 5000);
            return;
        }

        // Initialize map
        this.map = L.map("map").setView(
            [23.176782342345028, 72.62920203545316],
            13
        );

        // Street Map (OpenStreetMap)
        const streetMap = L.tileLayer(
            "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            {
                attribution: "&copy; OpenStreetMap contributors",
            }
        );

        // Satellite Map (ESRI)
        const satelliteMap = L.tileLayer(
            "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
            {
                attribution: "Tiles &copy; Esri",
            }
        );
        streetMap.addTo(this.map);
        const baseMaps = {
            "Street View": streetMap,
            "Satellite View": satelliteMap,
        };
        L.control.layers(baseMaps, null, { position: "topright" }).addTo(this.map);

        /* ------------------ ICONS ------------------ */
        // Source marker icon
        this.sourceIcon = L.divIcon({
            className: "custom-div-icon",
            html: `<div class="fa fa-map-marker" style="color:red;font-size:26px;"></div>`,
            iconSize: [40, 40],
            iconAnchor: [20, 40],
            popupAnchor: [0, -40],
        });

        // Destination icon generator
        this.getDestIcon = (priority) =>
            L.divIcon({
                className: "priority-icon",
                html: `
                    <div class="priority-wrapper">
                        <div class="priority-label">${priority}</div>
                        <div class="fa fa-map-marker marker-icon"></div>
                    </div>
                `,
                iconSize: [40, 50],
                iconAnchor: [20, 50],
                popupAnchor: [0, -50],
            });
    }



    _setLocationsInMap(locations) {
      // Remove existing markers and routes
      this.markers.forEach((marker) => this.map.removeLayer(marker));
      this.routingControls.forEach((route) => this.map.removeControl(route));
      this.markers = this.routingControls = [];

      // Set source as selected warehouse
      const selectedWarehouse = this.state.warehouses.find(
        (wh) => wh.id === this.state.selectedWarehouseId
      );

      if (!selectedWarehouse?.latitude || !selectedWarehouse?.longitude) {
        console.warn('Selected warehouse has no coordinates.');
        return;
      }

      const source = [
        parseFloat(selectedWarehouse.latitude),
        parseFloat(selectedWarehouse.longitude)
      ];

      const sourceMarker = L.marker(source, { icon: this.sourceIcon })
      .addTo(this.map)
      .bindPopup(`
        <div style="font-size: 14px; font-family: 'Odoo', Arial, sans-serif; background: #ffffff; max-width: 250px;">
          <div style="font-size: 16px; font-weight: bold; color: #714B67; margin-bottom: 8px;">
            📍 Warehouse Location
          </div>
          <div style="color: white; font-weight: bold; font-size: 16px; margin-bottom: 5px; background-color: #714B67; border-radius: 5px;padding: 5px;">
            ${selectedWarehouse.name}
          </div>
          <div style="margin-bottom: 5px;">
            <strong style="color: #6c757d;">Address:</strong>
            <span style="color: #333;">${selectedWarehouse.street || ''}, ${selectedWarehouse.city || ''}</span>
          </div>
        </div>
      `)
      .openPopup();

      this.markers.push(sourceMarker);
      // cordinates calculation for destination locations
      let cordinates = [];
      Object.entries(locations).forEach(([partner_id, orders]) => {
      let customerName =
        orders["orders"][0]?.partner_name || "Unknown Customer";
      let priority = orders["priority"];
      let address = orders["orders"][0]?.address || "No Address";
      let orderList = orders["orders"]
        .map((order) => `<li>${order.order}</li>`)
        .join("");

      let popupContent = `
                      <div style="
                          font-size: 14px;
                          font-family: 'Odoo', Arial, sans-serif;
                          background: #ffffff;
                          // border: 1px solid #d5d8dc;
                          // border-radius: 8px;
                          // padding: 12px;
                          // box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
                          max-width: 250px;
                        ">

                        <div style="color: white;
                        font-weight: bold;
                        font-size: 16px;
                        margin-bottom: 5px;
                        background-color: #714B67;
                        border-radius: 5px;padding: 5px;">
                          <div>${customerName}</div>
                        </div>

                        <div style="margin-bottom: 5px;">
                          <strong style="color: #6c757d;">Priority:</strong>
                          <span style="color: #017e84; font-weight: bold;">${priority}</span>
                        </div>

                        <div style="margin-bottom: 5px;">
                          <strong style="color: #6c757d;">Address:</strong>
                          <span style="color: #333;">${address}</span>
                        </div>

                        <div>
                          <strong style="color: #6c757d;">Orders:</strong>
                          <div style="
                              max-height: 100px;
                              overflow-y: auto;
                              border: 1px solid #d5d8dc;
                              padding: 5px;
                              border-radius: 5px;
                              background: #017e84;
                              margin-top: 5px;
                              color: white;
                            ">
                            <ul style="
                                margin: 0;
                                padding-left: 15px;
                                list-style-type: none;
                              ">
                              ${orderList}
                            </ul>
                          </div>
                        </div>
                      </div>
                    `;

      let notes = "";
      let single_cordinate = false;
      orders["orders"].forEach((order) => {
        notes = notes + order.order;
        single_cordinate = order.cordinates;
        cordinates.push(order.cordinates);
      });

      const destinationMarker = L.marker(single_cordinate, {
          icon: this.getDestIcon(priority),
        })
          .addTo(this.map)
          .bindPopup(popupContent);
      this.markers.push(destinationMarker);
    });

    // Route mapping in map
    console.log("Cordinates for routing:", cordinates);
    cordinates.forEach((cordinate) => {
      const control = L.Routing.control({
        waypoints: [L.latLng(source), L.latLng(cordinate)],
        routeWhileDragging: true,
        addWaypoints: false, // Disable adding new waypoints interactively
        draggableWaypoints: false, // Disable dragging waypoints
        createMarker: function () {
          return null;
        }, // Remove default markers
      }).addTo(this.map);
      console.log("Routing control added:", control);
      this.routingControls.push(control);
    });
  }

  searchPartner() {
    let self = this;
    $("#searchPartner").autocomplete({
      // Search dropdown
      source: function (request, response) {
        const requestTerm = request.term.trim();

        // If input is empty, restore all customers
        if (requestTerm === "") {
          self.state.customers = self.state.storedCustomers;
          response([]);
          return;
        }

        let search_timeout = setTimeout(() => {
          response([
            {
              id: "searchByName",
              value: requestTerm,
              label: "Search By Name: " + requestTerm,
            },
            {
              id: "searchByOrder",
              value: requestTerm,
              label: "Search By Order: " + requestTerm,
            },
          ]);
        }, 0);
      },

      // Searched result
      select: function (event, ui) {
        const searchCategory = ui.item.id;
        const requestTerm = ui.item.value.trim();
        let searchedFilterdCustomers = {};

        if (searchCategory === "searchByName") {
          searchedFilterdCustomers = Object.fromEntries(
            Object.entries(self.state.customers).filter(([key, customer]) =>
              customer.partner_name
                .toLowerCase()
                .includes(requestTerm.toLowerCase())
            )
          );
        } else if (searchCategory === "searchByOrder") {
          searchedFilterdCustomers = Object.fromEntries(
            Object.entries(self.state.customers).filter(([id, customer]) =>
              Object.entries(customer.orders).some(([order_id, order]) =>
                order.name.toLowerCase().includes(requestTerm.toLowerCase())
              )
            )
          );
        }
        self.state.customers = searchedFilterdCustomers;
      },
    });

    // Handle manual input change to reset data when input is cleared
    $("#searchPartner").on("input", function () {
      if ($(this).val().trim() === "") {
        self.state.customers = self.state.storedCustomers;
      }
    });
  }

  prepareDeliveries() {
    let self = this;
    const selectedOrders = $("input.item-checkbox:checked");
    let selectedOrdersDict = {};

    selectedOrders.each((index, order) => {
      const delivery_order_id = $(order).attr("value");
      const delivery_order_customer_id = $(order).attr("data-customer-id");
      if (!selectedOrdersDict[delivery_order_customer_id]) {
        selectedOrdersDict[delivery_order_customer_id] = [delivery_order_id];
      } else {
        let existingOrderIds = selectedOrdersDict[delivery_order_customer_id];
        existingOrderIds.push(delivery_order_id);
        selectedOrdersDict[delivery_order_customer_id] = existingOrderIds;
      }
    });

    const priorityMap = {};
    if (Array.isArray(this.state.locationsPriorityOrders)) {
        this.state.locationsPriorityOrders.forEach(loc => {
            const priority = loc.priority;
            if (Array.isArray(loc.orders)) {
                loc.orders.forEach(order => {
                    priorityMap[order.id] = 'priority';
                });
            }
        });
    } else {
        console.warn("locationsPriorityOrders is not an array:", this.state.locationsPriorityOrders);
    }

    let existingDeliveryOrders = this.state.customers;
    const filteredOrders = Object.keys(this.state.customers).flatMap(
      (partnerId) =>
        this.state.customers[partnerId].orders.filter(
          (order) =>
            selectedOrdersDict[partnerId]?.includes(order.id.toString()) // Ensure ID comparison works
        )
    );
    return filteredOrders;
  }


  async processDelivery() {
    if (!this.state.selectedWarehouseId) {
        this.notification.add("Please select a warehouse before processing deliveries.", {
            type: "warning",
        });
        return;
    }

    const filteredOrders = this.prepareDeliveries();
    if (!filteredOrders || filteredOrders.length === 0) {
        this.notification.add("Please select order to Process.");
        return;
    }
    const locations = await this.orm.call(
      "assign.delivery",
      "process_delivery",
      [, this.state.loggedInUserLocation, filteredOrders]
    );
    this.state.locationsPriorityOrders = locations;
    const priorityMap = {};

    locations.forEach((location, idx) => {
      const priority = location.priority;

      (location.orders || []).forEach((order, orderIdx) => {
        let orderId;

        if (Array.isArray(order) && typeof order[0] === 'number') {
          orderId = order[0];  // [id, name]
        } else if (typeof order === 'object' && order !== null) {
          orderId = order.id ?? order.order_id;
        } else if (typeof order === 'number') {
          orderId = order;
        }

        if (orderId !== undefined) {
          priorityMap[orderId] = priority;
        } else {
          console.warn(`Invalid order at index ${orderIdx} in location[${idx}]`, order);
        }
      });
    });

    this.state.orderPriorityMap = priorityMap;

    Object.values(this.state.customers).forEach(customer => {
      customer.orders.forEach(order => {
        const priority = this.state.orderPriorityMap[order.id];
        if (priority !== undefined) {
          order.priority = priority;
        }
      });
    });

    if (this.mapProvider === "google") {
      this._setLocationsInGoogleMap(locations);

    } else if (this.mapProvider === "leaflet") {
      this._setLocationsInMap(locations);
    } else {
      console.warn("No valid map provider selected.");
    }
  }

  assignDelivery() {
    let self = this;
    const filteredOrders = this.prepareDeliveries();

    if (!filteredOrders || filteredOrders.length === 0) {
        this.notification.add("Please select order to assign delivery.");
        return;
    }
    if (!Array.isArray(this.state.locationsPriorityOrders) || this.state.locationsPriorityOrders.length === 0) {
        this.notification.add("Please click on 'Process' first to generate priority orders.");
        return;
    }
    const dialog = this.env.services.dialog;

    const locationMapFunction =
      this.mapProvider === "google"
        ? this._setLocationsInGoogleMap.bind(this)
        : this._setLocationsInMap.bind(this);

    dialog.add(AssignDriverPopup, {
      title: _t("Assign Driver"),
      assignDeliveryOrders: filteredOrders,
      assignDeliveryDate: this.state.formatedDate,
      _setLocationsInMap: locationMapFunction,
      _setLocationsInGoogleMap : locationMapFunction,
      loggedInUserLocation: this.state.loggedInUserLocation,
      PriorityOrders: this.state.locationsPriorityOrders,
      mapProvider : this.mapProvider,
      removedOrderIds: this.state.removedOrderIds || [],
      close: () => {},
    });
  }

  async loadCustomerData() {
    console.log("Loading customer data...");

    const selectedWarehouseId = this.state.selectedWarehouseId;
    console.log("Selected Warehouse ID:", selectedWarehouseId);
    const formatedDate = this.state.formatedDate;
    console.log("Formated Date:", formatedDate);

    try {
        const warehouses = await this.orm.searchRead(
              "stock.warehouse", [],
              ["id", "name", "lot_stock_id", "company_id", "street", "city", "zip", "country_id", "state_id", "latitude", "longitude"]
            );
        console.log("Fetched Warehouses:", warehouses);

        this.state.warehouses = warehouses;

        const lotLocationToWarehouse = {};
        warehouses.forEach(wh => {
            if (wh.lot_stock_id?.[0]) {
                lotLocationToWarehouse[wh.lot_stock_id[0]] = wh.id;
            }
        });
        let domain = [
            ["state", "in", ["assigned"]],
            ["scheduled_date", ">=", formatedDate + " 00:00:00"],
            ["scheduled_date", "<=", formatedDate + " 23:59:59"],
            ["delivery_date", ">=", formatedDate + " 00:00:00"],
            ["delivery_date", "<=", formatedDate + " 23:59:59"],
            ["picking_type_id.code", "in", ["outgoing"]],
        ];
        console.log("Initial Domain:", domain);
          if (selectedWarehouseId) {
            const selectedWarehouse = warehouses.find(w => w.id === selectedWarehouseId);
            if (selectedWarehouse && selectedWarehouse.lot_stock_id?.[0]) {
                domain.push(["location_id", "child_of", selectedWarehouse.lot_stock_id[0]]);
            }
            console.log("Domain after warehouse filter:", domain);
        }
        console.log("Final Domain for Pickings Search:", domain);
        // Fetch pickings
        const pickings = await this.orm.searchRead(
            "stock.picking",
            domain,
            ["partner_id", "name", "location_id", "responsible_driver"]

        );
        console.log("Fetched Pickings:", pickings);

        // Fetch related moves
        const moves = await this.orm.searchRead(
            "stock.move",
            // [["id", "in", pickings.flatMap((p) => p.move_ids_without_package)]],
            [["id", "in", pickings.flatMap((p) => p.move_ids)]],
            ["product_id", "product_uom_qty", "location_dest_id"]
        );

        const locationIds = [
            ...new Set([
                ...pickings.map((p) => p.location_id?.[0]).filter(Boolean),
                ...moves.map((m) => m.location_dest_id?.[0]).filter(Boolean),
            ]),
        ];
        console.log("Location IDs to fetch:", locationIds);

        // Fetch locations
        const locations = await this.orm.searchRead(
            "stock.location",
            [["id", "in", locationIds]],
            ["id", "name"]
        );
        console.log("Fetched Locations:", locations);
        const locationMap = Object.fromEntries(locations.map(loc => [loc.id, loc.name]));

        const customers = {};
        pickings.forEach((picking) => {
            const partnerId = picking.partner_id?.[0];
            if (!partnerId) return;

            const partnerName = picking.partner_id[1];
            const orderLines = moves
                .filter((move) => picking.move_ids.includes(move.id))
                .map((move) => ({
                    product_name: move.product_id[1],
                    quantity: move.product_uom_qty,
                    warehouse_name: locationMap[move.location_dest_id[0]] || "Unknown Warehouse",
                }));

            if (!customers[partnerId]) {
                customers[partnerId] = {
                    partner_id: partnerId,
                    partner_name: partnerName,
                    orders: [],
                    orders_moves: [],
                };
            }

            customers[partnerId].orders.push(picking);
            customers[partnerId].orders_moves.push(...orderLines);
        });

        this.state.customers = customers;
    } catch (error) {
        console.error("Error fetching customer data:", error);
    }
  }

  toggleOrderList(event, customer) {
    $("#menu").css("display", "none");

    console.log("Toggling order list for customer ID:", customer);
    const dropdownItem = $(event.target);
    console.log("Toggling order list for customer:", customer);
    if (dropdownItem.hasClass("fa-chevron-circle-down")) {
      dropdownItem.removeClass("fa-chevron-circle-down");
      dropdownItem.addClass("fa-chevron-circle-up");
      $("div#orders-list-" + customer).css("display", "block");
    } else if (dropdownItem.hasClass("fa-chevron-circle-up")) {
      dropdownItem.removeClass("fa-chevron-circle-up");
      dropdownItem.addClass("fa-chevron-circle-down");
      $("div#orders-list-" + customer).css("display", "none");
    }
  }

  toggleselectall(event) {
    let checkboxes = document.querySelectorAll(".item-checkbox");
    let allChecked = Array.from(checkboxes).every(
      (checkbox) => checkbox.checked
    );

    checkboxes.forEach((checkbox) => {
      checkbox.checked = !allChecked;
    });
  }

  updateDate(event) {
    console.log("Date changed:", $(event.target).val());
    console.log("Event target:", event.target);
    console.log("Event:", this);
    this.state.formatedDate = $(event.target).val();
    this.loadCustomerData();
  }

  bindCloseButton() {
    const closeButton = document.getElementById("closeBtn");
    if (closeButton) {
      closeButton.addEventListener("click", () => {
        this.closeMenu();
      });
    }
  }

  closeMenu() {
    $("#menu").css("display", "none");
  }

  async showOrderDetails(event) {
    // $("#menu").css("display", "block");
    const menu = document.getElementById("menu");
    if (menu) {
        menu.style.display = "block";
    }

    let target = $(event.target);
    // let popup = $("#menu");
    let popup = document.getElementById("menu");

    let offset = target.offset();
    popup.style.top = offset.top + target.outerHeight() - 50 + "px";
    popup.style.left = offset.left + 43 + "px";
    popup.style.display = "block";

    let order = $(event.target).data("order");
    this.state.informationPopupData = await this.orm.call(
      "assign.delivery",
      "get_delivery_product_lines",
      [, order]
    );
  }

  async unlockOrderDetails(event) {
    const icon = event.currentTarget;  // The clicked <i> element
    const orderId = icon.getAttribute("data-order");  // Get the order ID
    try {
        const res = await this.orm.call("assign.delivery", "unlock_delivery", [, orderId]);
        if (res === true || res === "ok" || res?.success) {
            icon.style.display = "none";
        } else {
            console.warn("Unlock failed or returned false");
        }
    } catch (err) {
        console.error("Error during unlock:", err);
    }
}

  fetchPopupData(event) {
    let sourceOrderId = $(event.target).parent().attr("value");
  }

  async fetchLoggedinSourceLocation() {
    this.uid = session.storeData.Store.settings.user_id.id;
    this.state.loggedInUserLocation = await this.orm.call(
      "assign.delivery",
      "fetch_loggedin_source_location",
      [, this.uid]
    );
  }
}

registry.category("actions").add("aspl_delivery_plan_ee.delivery_plan_list_filter", DeliveryPlan);