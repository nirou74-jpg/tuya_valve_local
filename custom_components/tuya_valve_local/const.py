"""Constants pour tuya_valve_local."""

DOMAIN = "tuya_valve_local"

# Config entry keys
CONF_DEVICE_ID   = "device_id"
CONF_IP          = "ip_address"
CONF_LOCAL_KEY   = "local_key"
CONF_VERSION     = "protocol_version"
CONF_NODE_ID     = "node_id"
CONF_NAME        = "name"
CONF_DEFAULT_DUR = "default_duration"

# DPS
DPS_VALVE        = 1    # bool : ON/OFF vanne
DPS_FAULT        = 4    # bitfield : défaut
DPS_BATTERY      = 7    # int % : batterie
DPS_ACCUM_TIME   = 9    # int s : temps cumulé
DPS_WEATHER_DLY  = 10   # string : délai météo
DPS_COUNTDOWN    = 11   # int s : countdown arrosage
DPS_OPERATION    = 12   # string : opération en cours
DPS_LAST_TIME    = 15   # int s : durée dernier usage
DPS_SMART_WX     = 14   # bool : smart weather

# Valeurs weather delay
WEATHER_DELAY_OPTIONS = ["cancel", "24h", "48h", "72h"]

# Durée par défaut (secondes)
DEFAULT_DURATION_S = 600  # 10 minutes

# Versions protocole
PROTOCOL_VERSIONS = ["3.3", "3.4", "3.5", "3.1"]

# Polling
SCAN_INTERVAL = 60
