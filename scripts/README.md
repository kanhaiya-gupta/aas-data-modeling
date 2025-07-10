# ETL Setup Scripts

Simple, consolidated setup scripts for the AAS Data Modeling ETL environment.

## 🚀 Quick Setup

```bash
# One command setup (recommended)
python setup_etl.py

# Or run directly
python setup_etl_auto.py
```

## 📋 Available Scripts

| Script | Description |
|--------|-------------|
| `setup_etl.py` | Simple wrapper (recommended) |
| `setup_etl_auto.py` | Main setup script with auto-detection |
| `check_python.py` | Python environment diagnostics |

## 🌟 Features

- **Auto-Detection**: Automatically detects Windows, Linux, or macOS
- **Platform Optimized**: Uses the best installation methods for your system
- **Complete Setup**: Installs Python packages, .NET 6.0 SDK, and AAS libraries
- **Error Recovery**: Continues setup even if some steps fail
- **Progress Tracking**: Clear step-by-step feedback

## 📦 What Gets Installed

- **Python Packages**: All required packages from `requirements.txt`
- **.NET 6.0 SDK**: Required for AAS libraries
- **AAS Core 3.0**: Asset Administration Shell core library
- **AASX Package**: AASX file format library
- **.NET Processor**: Custom AAS processing application

## 🎯 For Your Setup

Since you're using Git Bash on Windows, simply run:

```bash
python setup_etl.py
```

The script will automatically detect Windows and use the optimal setup process for your environment.

## 📚 Documentation

- **`README_SETUP.md`** - Detailed setup guide and troubleshooting
- **`check_python.py`** - Python environment diagnostics

---

**Note**: The setup scripts handle all the complexity of setting up the .NET processor with AAS libraries, so you can focus on using the ETL pipeline rather than fighting with environment setup. 