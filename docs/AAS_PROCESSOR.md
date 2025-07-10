# .NET AAS Processor

## Overview

The .NET AAS Processor is a high-performance, production-ready component for processing AASX (Asset Administration Shell Exchange) files. Built using the official AAS Core libraries, it provides robust parsing, data extraction, and metadata generation capabilities for Asset Administration Shell files.

## Features

### Core Capabilities
- **AASX File Processing** - Extract and parse AASX container files
- **Multi-Format Support** - AAS 1.0 XML and AAS 3.0 JSON formats
- **Asset Extraction** - Extract Asset Administration Shells and Assets
- **Submodel Processing** - Parse and extract submodel metadata
- **Document Management** - Extract embedded documents and metadata
- **Multi-Language Support** - Handle internationalized descriptions
- **Error Handling** - Comprehensive error handling and validation

### Performance Features
- **High-Speed Processing** - Optimized for large AASX files
- **Memory Efficient** - Streaming processing for large files
- **Parallel Processing** - Support for concurrent file processing
- **Caching** - Intelligent caching for repeated operations

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    .NET AAS Processor                       │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   ZIP Handler   │  │   XML Parser    │  │ JSON Parser  │ │
│  │                 │  │                 │  │              │ │
│  │ • File Extract  │  │ • AAS 1.0       │  │ • AAS 3.0    │ │
│  │ • Navigation    │  │ • Namespaces    │  │ • Validation │ │
│  │ • Validation    │  │ • Multi-lang    │  │ • Streaming  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  Asset Extractor│  │ Submodel Extractor│ │Doc Extractor │ │
│  │                 │  │                 │  │              │ │
│  │ • AAS Shells    │  │ • Submodels     │  │ • PDFs       │ │
│  │ • Assets        │  │ • Properties    │  │ • Images     │ │
│  │ • References    │  │ • Collections   │  │ • Documents  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  JSON Output    │  │ Error Handler   │  │ Validator    │ │
│  │                 │  │                 │  │              │ │
│  │ • Structured    │  │ • Exceptions    │  │ • Schema     │ │
│  │ • Metadata      │  │ • Logging       │  │ • Format     │ │
│  │ • Timestamps    │  │ • Recovery      │  │ • Integrity  │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Project Structure

```
aas-processor/
├── AasProcessor.cs              # Main processor class
├── Program.cs                   # Command line interface
├── AasProcessor.csproj          # Project configuration
├── bin/
│   └── Release/
│       └── net6.0/
│           ├── AasProcessor.dll # Built executable
│           └── AasProcessor.exe # Windows executable
└── obj/                         # Build artifacts
```

## Dependencies

### NuGet Packages
```xml
<PackageReference Include="AasCore.Aas3.Package" Version="1.0.0" />
<PackageReference Include="System.IO.Compression" Version="4.3.0" />
<PackageReference Include="System.Text.Json" Version="6.0.0" />
```

### Runtime Requirements
- **.NET 6.0 Runtime** or higher
- **Windows/Linux/macOS** support
- **Minimum 512MB RAM** for large files
- **Disk space** for temporary extraction

## Installation

### Prerequisites
1. **Install .NET 6.0 SDK**
   ```bash
   # Download from: https://dotnet.microsoft.com/download/dotnet/6.0
   # Verify installation
   dotnet --version
   ```

2. **Clone or download** the project files

### Build Instructions
```bash
# Navigate to project directory
cd aas-processor

# Restore dependencies
dotnet restore

# Build in Release mode
dotnet build --configuration Release

# Verify build
ls bin/Release/net6.0/
```

### Build Output
After successful build, you'll find:
- `AasProcessor.dll` - Main assembly
- `AasProcessor.exe` - Windows executable
- `AasCore.Aas3.dll` - AAS Core library
- Supporting files and dependencies

## Usage

### Command Line Interface

#### Basic Usage
```bash
# Process a single AASX file
dotnet run --configuration Release "path/to/file.aasx"

# Process with output redirection
dotnet run --configuration Release "file.aasx" > output.json

# Process with error logging
dotnet run --configuration Release "file.aasx" 2> errors.log
```

#### Advanced Usage
```bash
# Process multiple files
for file in *.aasx; do
    dotnet run --configuration Release "$file" > "${file%.aasx}.json"
done

# Process with timeout
timeout 30s dotnet run --configuration Release "large_file.aasx"

# Process in background
nohup dotnet run --configuration Release "file.aasx" > output.json &
```

### Programmatic Usage

#### C# Integration
```csharp
using AasProcessor;

// Create processor instance
var processor = new AasProcessor();

// Process AASX file
string result = processor.ProcessAasxFile("path/to/file.aasx");

// Parse JSON result
var data = JsonSerializer.Deserialize<Dictionary<string, object>>(result);
```

#### Python Integration (via Bridge)
```python
from webapp.aasx.dotnet_bridge import DotNetAasProcessor

# Create processor
processor = DotNetAasProcessor()

# Process file
result = processor.process_aasx_file("path/to/file.aasx")
print(result)
```

## API Reference

### Main Class: `AasProcessor`

#### Constructor
```csharp
public AasProcessor()
```

#### Methods

##### `ProcessAasxFile(string aasxFilePath)`
Processes an AASX file and returns JSON result.

**Parameters:**
- `aasxFilePath` (string): Path to the AASX file

**Returns:**
- `string`: JSON-formatted processing result

**Example:**
```csharp
var processor = new AasProcessor();
string result = processor.ProcessAasxFile("example.aasx");
Console.WriteLine(result);
```

## Output Format

### JSON Structure
```json
{
  "metadata": {
    "processing_time": "2024-01-15T10:30:00Z",
    "file_path": "example.aasx",
    "file_size": 1024000,
    "version": "1.0.0"
  },
  "assets": [
    {
      "id": "asset_001",
      "type": "AssetAdministrationShell",
      "description": "Industrial 3D Printer",
      "properties": {
        "manufacturer": "3D Systems",
        "model": "AM5000-XL",
        "serial_number": "AM5XL-2024-001"
      }
    }
  ],
  "submodels": [
    {
      "id": "submodel_001",
      "type": "TechnicalSpecifications",
      "properties": [
        {
          "name": "build_volume",
          "value": "500x500x500mm",
          "unit": "mm"
        }
      ]
    }
  ],
  "documents": [
    {
      "id": "doc_001",
      "type": "TechnicalManual",
      "filename": "manual.pdf",
      "size": 2048000
    }
  ],
  "statistics": {
    "total_assets": 1,
    "total_submodels": 5,
    "total_properties": 25,
    "total_documents": 3
  }
}
```

## Error Handling

### Common Errors

#### File Not Found
```json
{
  "error": "File not found",
  "file_path": "nonexistent.aasx",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Invalid AASX Format
```json
{
  "error": "Invalid AASX format",
  "details": "Missing required AAS elements",
  "file_path": "invalid.aasx",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Processing Timeout
```json
{
  "error": "Processing timeout",
  "details": "File processing exceeded 30 second limit",
  "file_path": "large_file.aasx",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

## Performance Optimization

### Large File Processing
```bash
# Increase memory limit for large files
dotnet run --configuration Release --max-memory 2GB "large_file.aasx"

# Process in chunks
dotnet run --configuration Release --chunk-size 1000 "large_file.aasx"
```

### Parallel Processing
```bash
# Process multiple files in parallel
parallel -j 4 'dotnet run --configuration Release {} > {.}.json' ::: *.aasx
```

## Integration with Framework

### ETL Pipeline Integration
The .NET AAS Processor is integrated into the AASX Digital Twin Analytics Framework through:

1. **Python Bridge** - `webapp/aasx/dotnet_bridge.py`
2. **ETL Pipeline** - `scripts/run_etl.py`
3. **Web Interface** - File upload and processing
4. **API Endpoints** - RESTful processing endpoints

### Setup Scripts
```bash
# Complete setup including .NET processor
python scripts/setup_etl_auto.py

# Check processor status
python scripts/run_etl.py --check

# Build processor only
python scripts/run_etl.py --build
```

## Troubleshooting

### Build Issues
```bash
# Clean and rebuild
dotnet clean
dotnet restore
dotnet build --configuration Release

# Check .NET version
dotnet --version

# Verify dependencies
dotnet list package
```

### Runtime Issues
```bash
# Check file permissions
chmod +x bin/Release/net6.0/AasProcessor.exe

# Test with sample file
dotnet run --configuration Release "data/aasx-examples/additive-manufacturing-3d-printer.aasx"

# Enable verbose logging
dotnet run --configuration Release --verbosity detailed "file.aasx"
```

## Contributing

### Development Setup
1. Install .NET 6.0 SDK
2. Clone the repository
3. Open in Visual Studio or VS Code
4. Install recommended extensions
5. Run tests: `dotnet test`

### Code Standards
- Follow C# coding conventions
- Add XML documentation comments
- Include unit tests for new features
- Update this documentation

### Testing
```bash
# Run all tests
dotnet test

# Run specific test
dotnet test --filter "TestName"

# Run with coverage
dotnet test --collect:"XPlat Code Coverage"
``` 