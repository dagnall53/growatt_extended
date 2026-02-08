from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import CoordinatorEntity
import logging

_LOGGER = logging.getLogger(__name__)

DOMAIN = "growatt_extended"
GROWATT_DOMAIN = "growatt_server"


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """Set up extended Growatt sensors."""

    data = hass.data[DOMAIN][entry.entry_id]
    coordinator = data["coordinator"]
    growatt_entry_id = data["growatt_entry_id"]

    # DEBUG: dump full data structure
    _LOGGER.warning("Growatt Extended: coordinator.data = %s", coordinator.data)

    # Find the Growatt device from the official integration
    device_registry = dr.async_get(hass)
    growatt_device = None

    for device in device_registry.devices.values():
        if growatt_entry_id in device.config_entries:
            growatt_device = device
            break

    if growatt_device is None:
        raise RuntimeError("Growatt Extended: Could not find Growatt device")

    # Define all extended sensors
    sensors = [

        # -------------------------
        # BATTERY SENSORS
        # -------------------------
        GrowattExtendedSensor(
            coordinator, growatt_entry_id,
            "battery_soc", "Battery State of Charge", "%"
        ),
        GrowattExtendedSensor(
            coordinator, growatt_entry_id,
            "battery_charge_power", "Battery Charge Power", "W"
        ),
        GrowattExtendedSensor(
            coordinator, growatt_entry_id,
            "battery_discharge_power", "Battery Discharge Power", "W"
        ),
        GrowattExtendedSensor(
            coordinator, growatt_entry_id,
            "battery_net_power", "Battery Net Power", "W"
        ),
        GrowattExtendedSensor(
            coordinator, growatt_entry_id,
            "battery_energy_today", "Battery Energy Today", "kWh"
        ),
        GrowattExtendedSensor(
            coordinator, growatt_entry_id,
            "battery_energy_total", "Battery Total Energy", "kWh"
        ),
        GrowattExtendedSensor(
            coordinator, growatt_entry_id,
            "battery_status", "Battery Status", None
        ),
        GrowattExtendedSensor(
            coordinator, growatt_entry_id,
            "battery_error_code", "Battery Error Code", None
        ),

        # -------------------------
        # GRID SENSORS
        # -------------------------
        GrowattExtendedSensor(
            coordinator, growatt_entry_id,
            "grid_power", "Grid Power", "W"
        ),
        GrowattExtendedSensor(
            coordinator, growatt_entry_id,
            "grid_load_power", "Grid → Load Power", "W"
        ),
        GrowattExtendedSensor(
            coordinator, growatt_entry_id,
            "grid_state", "Grid Import/Export State", None
        ),

        # -------------------------
        # SOLAR / PV SENSORS
        # -------------------------
        GrowattExtendedSensor(
            coordinator, growatt_entry_id,
            "pv_power", "PV Power", "W"
        ),
        GrowattExtendedSensor(
            coordinator, growatt_entry_id,
            "pv_energy_today", "PV Energy Today", "kWh"
        ),
        GrowattExtendedSensor(
            coordinator, growatt_entry_id,
            "pv_energy_total", "PV Total Energy", "kWh"
        ),

        # -------------------------
        # LOAD (DERIVED)
        # -------------------------
        GrowattExtendedSensor(
            coordinator, growatt_entry_id,
            "load_power", "Home Load Power", "W"
        ),

        # -------------------------
        # PLANT / ENVIRONMENTAL
        # -------------------------
        GrowattExtendedSensor(
            coordinator, growatt_entry_id,
            "money_today", "Money Saved Today", "¥"
        ),
        GrowattExtendedSensor(
            coordinator, growatt_entry_id,
            "money_total", "Money Saved Total", "¥"
        ),
        GrowattExtendedSensor(
            coordinator, growatt_entry_id,
            "co2_reduction", "CO₂ Reduction", "kg"
        ),

        # -------------------------
        # DATALOGGER
        # -------------------------
        GrowattExtendedSensor(
            coordinator, growatt_entry_id,
            "datalogger_signal", "Datalogger Signal Quality", None
        ),
        GrowattExtendedSensor(
            coordinator, growatt_entry_id,
            "datalogger_status", "Datalogger Connection Status", None
        ),
        GrowattExtendedSensor(
            coordinator, growatt_entry_id,
            "datalogger_last_update", "Datalogger Last Update", None
        ),
        GrowattExtendedSensor(
            coordinator, growatt_entry_id,
            "datalogger_update_interval", "Datalogger Update Interval", "s"
        ),
    ]

    async_add_entities(sensors)


class GrowattExtendedSensor(CoordinatorEntity, SensorEntity):
    """Representation of an extended Growatt sensor."""

    def __init__(self, coordinator, growatt_entry_id, key, name, unit):
        super().__init__(coordinator)
        self._attr_unique_id = f"{growatt_entry_id}_{key}"
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_device_info = {
            "identifiers": {(GROWATT_DOMAIN, growatt_entry_id)},
            "name": "Growatt Inverter",
            "manufacturer": "Growatt",
            "model": "SPA3000 + ShineWiFi-S",
        }
        self._key = key

    @property
    def native_value(self):
        data = self.coordinator.data
        if not data:
            return None

        storage = data.get("storageList", [{}])[0]
        datalog = data.get("datalogList", [{}])[0]

        # -------------------------
        # BATTERY
        # -------------------------
        if self._key == "battery_soc":
            try:
                return int(storage.get("capacity", "0%").replace("%", ""))
            except Exception:
                return None

        if self._key == "battery_charge_power":
            return int(storage.get("pCharge", 0))

        if self._key == "battery_discharge_power":
            # Not provided by Growatt for SPA — always 0
            return int(storage.get("pDischarge", 0))

        if self._key == "battery_net_power":
            charge = int(storage.get("pCharge", 0))
            discharge = int(storage.get("pDischarge", 0))
            return discharge - charge

        if self._key == "battery_energy_today":
            return float(storage.get("eChargeToday", 0))

        if self._key == "battery_energy_total":
            return float(storage.get("energy", 0))

        if self._key == "battery_status":
            return storage.get("deviceStatus")

        if self._key == "battery_error_code":
            return storage.get("dtc")

        # -------------------------
        # GRID
        # -------------------------
        if self._key == "grid_power":
            return int(data.get("storagePgrid", 0))

        if self._key == "grid_load_power":
            return int(data.get("storagePuser", 0))

        if self._key == "grid_state":
            gp = int(data.get("storagePgrid", 0))
            if gp < 0:
                return "Importing"
            if gp > 0:
                return "Exporting"
            return "Idle"

        # -------------------------
        # SOLAR / PV
        # -------------------------
        if self._key == "pv_power":
            return int(data.get("invTodayPpv", 0))

        if self._key == "pv_energy_today":
            return float(data.get("todayEnergy", 0))

        if self._key == "pv_energy_total":
            return float(data.get("totalEnergy", 0))

        # -------------------------
        # LOAD (DERIVED)
        # -------------------------
        if self._key == "load_power":
            pv = int(data.get("invTodayPpv", 0))
            grid = int(data.get("storagePgrid", 0))
            charge = int(storage.get("pCharge", 0))
            discharge = int(storage.get("pDischarge", 0))
            battery_net = discharge - charge
            return pv + grid - battery_net

        # -------------------------
        # PLANT / ENVIRONMENTAL
        # -------------------------
        if self._key == "money_today":
            return float(data.get("plantMoneyText", 0))

        if self._key == "money_total":
            return float(data.get("totalMoneyText", 0))

        if self._key == "co2_reduction":
            return float(data.get("Co2Reduction", 0))

        # -------------------------
        # DATALOGGER
        # -------------------------
        if self._key == "datalogger_signal":
            raw = datalog.get("values", [""])[0]
            mapping = {
                "优": "Excellent",
                "良": "Good",
                "中": "Fair",
                "差": "Poor",
            }
            return mapping.get(raw, raw)

        if self._key == "datalogger_status":
            raw = datalog.get("values", ["", ""])[1]
            mapping = {
                "已连接": "Connected",
                "未连接": "Disconnected",
            }
            return mapping.get(raw, raw)

        if self._key == "datalogger_last_update":
            return datalog.get("values", ["", "", ""])[2]

        if self._key == "datalogger_update_interval":
            try:
                return int(datalog.get("values", ["", "", "", "0"])[3])
            except Exception:
                return None


        return None
