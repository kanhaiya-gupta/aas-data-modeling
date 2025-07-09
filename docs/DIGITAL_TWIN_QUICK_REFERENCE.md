# Digital Twin Quick Reference Guide

## 🚀 Quick Start

### Access Twin Registry
```
URL: http://localhost:5000/twin-registry
Navigation: Dashboard → Twin Registry
```

### Create New Twin (5 Steps)
1. **Click "Add Twin"** button
2. **Fill Basic Info** (ID, Name, Type - required)
3. **Configure Asset** (Location, Model, Manufacturer)
4. **Set Data Source** (Type, Format, Endpoints)
5. **Click "Create Digital Twin"**

## 📋 Common Operations

### View Twin Details
- Click **"View"** button in twin table
- See performance metrics and status

### Edit Twin Configuration
- Click **"Edit"** button
- Modify any parameters
- Save changes

### Sync Twin Data
- Click **"Sync"** button
- Monitor sync progress
- Check results

### Save as Draft
- Fill partial information
- Click **"Save as Draft"**
- Complete later

## 🔧 Auto-Generation

### Twin ID Auto-Generation
```
Format: [TYPE]-[NAME]-[TIMESTAMP]
Example: MA-ADDITIVE-1234
```

### Asset ID Auto-Generation
```
Format: [MANUFACTURER]-[MODEL]-[DATE]
Example: IND-3DPRIN-2401
```

## 📊 Performance Metrics

### Key Indicators
- **Uptime**: Operational percentage
- **Efficiency**: Performance score
- **Response Time**: Average response
- **Alerts**: Active alert count

### Status Badges
- 🟢 **Online**: Active and syncing
- 🟡 **Maintenance**: Under maintenance
- 🔴 **Offline**: Not connected
- ⚠️ **Warning**: Issues detected

## 🔌 Data Source Types

### Quick Selection Guide
- **IoT Sensors**: Direct sensor data
- **PLC/SCADA**: Industrial systems
- **Database**: Database connections
- **API**: External APIs
- **Manual**: Human input
- **File**: File uploads

### Data Formats
- **JSON**: Web APIs, modern systems
- **XML**: Legacy systems, documents
- **CSV**: Simple data, spreadsheets
- **OPC UA**: Industrial automation
- **Modbus**: Industrial communication
- **MQTT**: IoT messaging

## 🏷️ Twin Types & Categories

### Twin Types
- **Manufacturing**: Production equipment
- **Energy**: Power systems
- **Transportation**: Vehicles, logistics
- **Healthcare**: Medical equipment
- **Agriculture**: Farming systems
- **Construction**: Building systems
- **Logistics**: Supply chain
- **Smart City**: Urban infrastructure
- **Custom**: User-defined

### Categories
- **Equipment**: Individual machines
- **Facility**: Buildings, plants
- **Process**: Manufacturing processes
- **System**: Complex systems
- **Product**: End products

## ⚙️ Configuration Settings

### Sync Frequencies
- **Real-time**: Continuous
- **1min/5min/15min**: Periodic
- **1hour**: Hourly
- **Daily**: Once per day
- **Manual**: User-controlled

### Data Retention
- **30 days**: Short-term
- **90 days**: Medium-term
- **6months/1year**: Long-term
- **2years**: Archive
- **Indefinite**: Permanent

### Alert Thresholds
- **Low**: Conservative (fewer alerts)
- **Medium**: Standard (balanced)
- **High**: Sensitive (more alerts)
- **Custom**: User-defined

## 🚨 Common Alerts

### Alert Types
- **High Temperature**: Equipment overheating
- **Connection Lost**: Communication failure
- **Maintenance Due**: Scheduled maintenance
- **Performance Degradation**: Efficiency issues
- **Data Quality**: Poor data indicators

### Alert Actions
- **Acknowledge**: Mark as seen
- **Resolve**: Mark as fixed
- **Escalate**: Increase priority
- **Suppress**: Temporarily ignore

## 🔍 Troubleshooting

### Twin Not Syncing?
1. Check data source connectivity
2. Verify endpoint URLs
3. Check authentication
4. Review network settings

### Performance Issues?
1. Adjust sync frequency
2. Check data retention
3. Monitor system resources
4. Optimize data queries

### Too Many Alerts?
1. Adjust alert thresholds
2. Check data quality
3. Review alert configuration
4. Suppress false positives

## 📱 Keyboard Shortcuts

### Modal Navigation
- **Esc**: Close modal
- **Enter**: Submit form
- **Tab**: Navigate fields

### Table Operations
- **Ctrl+F**: Search twins
- **Ctrl+A**: Select all
- **Ctrl+C**: Copy selection

## 🔗 Useful Links

### Platform URLs
- **Dashboard**: `/`
- **Twin Registry**: `/twin-registry`
- **API Docs**: `/docs`
- **Health Check**: `/health`

### External Resources
- **AAS Documentation**: [Asset Administration Shell](https://www.plattform-i40.de/PI40/Redaktion/EN/Standardartikel/specification-administration-shell.html)
- **OPC UA**: [OPC Foundation](https://opcfoundation.org/)
- **MQTT**: [MQTT.org](https://mqtt.org/)

## 📞 Quick Support

### Common Issues
- **Page not loading**: Check if server is running
- **Form not submitting**: Check required fields
- **Data not syncing**: Verify data source configuration
- **Alerts not working**: Check alert threshold settings

### Getting Help
1. Check this Quick Reference
2. Read the full README
3. Check API documentation
4. Review system logs

---

**Quick Reference v1.0** | **QI Digital Platform** | **Digital Twin Registry** 