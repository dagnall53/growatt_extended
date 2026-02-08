🌞 Growatt Extended – Home Assistant Integration
This custom integration extends the official Growatt Server integration by exposing additional sensors for SPA‑series hybrid inverters (e.g., SPA3000) and ShineWiFi‑S dataloggers.

It adds:

- Battery SOC, charge/discharge power, net power
- Battery energy today / total
- Grid import/export power and state
- PV power, daily energy, lifetime energy
- Home load (derived)
- Money saved today / total
- CO₂ reduction
- Datalogger signal quality (translated from Chinese)
- Datalogger connection status (translated from Chinese)
- Datalogger last update + update interval


This integration is designed to be clean, explicit, and maintainable, with all values derived directly from the Growatt API.

📦 Installation
1. Copy the integration into Home Assistant
Place the folder:

Code
custom_components/growatt_extended/
into your Home Assistant configuration directory.

Your structure should look like:

Code
📁 config/

└── 📁 custom_components/

    └── 📁 growatt_extended/  
    
        ├── __init__.py        
        ├── manifest.json        
        ├── sensor.py        
        └── README.md
        

2. Restart Home Assistant
After restart, the integration will automatically attach itself to the existing Growatt Server device and create the extended sensors.

🔧 Fixing CRLF Line Endings (Windows → Linux)
If you edit files on Windows, you may accidentally introduce CRLF line endings, which can break Python files in Home Assistant.

Use this shell command inside the integration directory to convert all files to LF:

find /homeassistant/custom_components/growatt_extended -type f -exec sed -i "s/\r$//" {} \;

This ensures all Python, JSON, and manifest files use correct Unix line endings.

🧪 Debug Logging
To see the raw Growatt API data returned by the coordinator, add this to your configuration.yaml:

yaml
logger:
  logs:
    custom_components.growatt_extended: debug
Then restart Home Assistant.

📝 Notes
This integration does not replace the official Growatt integration — it extends it.

All sensors are read‑only and derived from the Growatt cloud API.

Datalogger Chinese strings (e.g., 优, 已连接) are automatically translated to English.

Designed for SPA‑series hybrid inverters but may work with others that expose similar fields.

📘 License
MIT License (recommended for Home Assistant custom components)
