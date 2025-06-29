"""Constants for Traccar client integration."""

DOMAIN = "traccar"

CONF_MAX_ACCURACY = "max_accuracy"
CONF_SKIP_ACCURACY_ON = "skip_accuracy_filter_on"

ATTR_ACCURACY = "accuracy"
ATTR_ADDRESS = "address"
ATTR_ALTITUDE = "altitude"
ATTR_BATTERY = "batt"
ATTR_BEARING = "bearing"
ATTR_CATEGORY = "category"
ATTR_GEOFENCE = "geofence"
ATTR_LATITUDE = "lat"
ATTR_LONGITUDE = "lon"
ATTR_MOTION = "motion"
ATTR_SPEED = "speed"
ATTR_STATUS = "status"
ATTR_TRACKER = "tracker"
ATTR_TRACCAR_ID = "traccar_id"

EVENT_DEVICE_MOVING = "device_moving"
EVENT_COMMAND_RESULT = "command_result"
EVENT_DEVICE_FUEL_DROP = "device_fuel_drop"
EVENT_GEOFENCE_ENTER = "geofence_enter"
EVENT_DEVICE_OFFLINE = "device_offline"
EVENT_DRIVER_CHANGED = "driver_changed"
EVENT_GEOFENCE_EXIT = "geofence_exit"
EVENT_DEVICE_OVERSPEED = "device_overspeed"
EVENT_DEVICE_ONLINE = "device_online"
EVENT_DEVICE_STOPPED = "device_stopped"
EVENT_MAINTENANCE = "maintenance"
EVENT_ALARM = "alarm"
EVENT_TEXT_MESSAGE = "text_message"
EVENT_DEVICE_UNKNOWN = "device_unknown"
EVENT_IGNITION_OFF = "ignition_off"
EVENT_IGNITION_ON = "ignition_on"
EVENT_ALL_EVENTS = "all_events"
