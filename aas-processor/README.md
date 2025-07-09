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
├── README.md                    # This file
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
```

##### `ExtractAasFromXml(string xmlContent, List<object> assets, List<object> submodels, string sourceFile)`
Extracts AAS data from XML content.

**Parameters:**
- `xmlContent` (string): XML content to parse
- `assets` (List<object>): Collection to store extracted assets
- `submodels` (List<object>): Collection to store extracted submodels
- `sourceFile` (string): Source file name for reference

##### `ExtractAasFromJson(JsonElement jsonData, List<object> assets, List<object> submodels, string sourceFile)`
Extracts AAS data from JSON content.

**Parameters:**
- `jsonData` (JsonElement): JSON data to parse
- `assets` (List<object>): Collection to store extracted assets
- `submodels` (List<object>): Collection to store extracted submodels
- `sourceFile` (string): Source file name for reference

### Output Format

#### JSON Response Structure
```json
{
  "processing_method": "enhanced_zip_processing",
  "file_path": "example.aasx",
  "file_size": 203968,
  "processing_timestamp": "2025-07-08T23:54:01Z",
  "libraries_used": [
    "System.IO.Compression",
    "System.Text.Json",
    "System.Xml"
  ],
  "assets": [
    {
      "id": "http://customer.com/aas/9175_7013_7091_9168",
      "idShort": "ExampleMotor",
      "description": "Asset description",
      "kind": "CONSTANT",
      "source": "filename.aas.xml",
      "format": "XML_AAS_1_0"
    }
  ],
  "submodels": [
    {
      "id": "http://i40.customer.com/type/1/1/F13E8576F6488342",
      "idShort": "Identification",
      "description": "Identification from Manufacturer",
      "kind": "Instance",
      "source": "filename.aas.xml",
      "format": "XML_AAS_1_0"
    }
  ],
  "documents": [
    {
      "filename": "OperatingManual.pdf",
      "size": 194061,
      "type": ".pdf"
    }
  ],
  "raw_data": {
    "json_files": [],
    "xml_files": ["filename.aas.xml"]
  }
}
```

## Supported Formats

### AASX File Structure
- **ZIP Container** - Standard ZIP format
- **AAS 1.0 XML** - XML-based Asset Administration Shell
- **AAS 3.0 JSON** - JSON-based Asset Administration Shell
- **Embedded Documents** - PDF, images, text files
- **Relationship Files** - OPC relationships

### XML Namespaces
- `http://www.admin-shell.io/aas/1/0` - AAS 1.0 namespace
- `http://www.admin-shell.io/aas/3/0` - AAS 3.0 namespace
- `http://www.admin-shell.io/IEC61360/1/0` - IEC61360 namespace

### Document Types
- **PDF Files** - `.pdf` extension
- **Image Files** - `.jpg`, `.png`, `.gif`, `.bmp`
- **Text Files** - `.txt`, `.xml`, `.json`
- **Binary Files** - Any binary format

## Performance

### Processing Speed
| File Size | Processing Time | Memory Usage |
|-----------|----------------|--------------|
| < 1MB     | 100-500ms      | 50-100MB     |
| 1-10MB    | 500ms-2s       | 100-200MB    |
| 10-50MB   | 2-10s          | 200-500MB    |
| > 50MB    | 10s+           | 500MB+       |

### Optimization Tips
1. **Use Release Build** - Significantly faster than Debug
2. **Adequate Memory** - Ensure sufficient RAM for large files
3. **SSD Storage** - Faster file I/O operations
4. **Parallel Processing** - Process multiple files concurrently

## Error Handling

### Common Errors

#### File Not Found
```
Error: Could not find file 'nonexistent.aasx'
```
**Solution:** Verify file path and permissions

#### Invalid ZIP Format
```
Error: Invalid ZIP file format
```
**Solution:** Ensure file is a valid AASX/ZIP file

#### XML Parsing Error
```
Error: XML parsing failed: [details]
```
**Solution:** Check XML format and namespace declarations

#### Memory Error
```
Error: Insufficient memory for processing
```
**Solution:** Increase available memory or process smaller files

### Error Recovery
```csharp
try
{
    var processor = new AasProcessor();
    string result = processor.ProcessAasxFile("file.aasx");
}
catch (FileNotFoundException ex)
{
    Console.WriteLine($"File not found: {ex.Message}");
}
catch (Exception ex)
{
    Console.WriteLine($"Processing error: {ex.Message}");
}
```

## Testing

### Unit Tests
```bash
# Run unit tests
dotnet test

# Run with coverage
dotnet test --collect:"XPlat Code Coverage"
```

### Integration Tests
```bash
# Test with sample files
dotnet run --configuration Release "../AasxPackageExplorer/content-for-demo/Example_AAS_ServoDCMotor_21.aasx"

# Test error conditions
dotnet run --configuration Release "nonexistent.aasx"
```

### Performance Tests
```bash
# Time processing
time dotnet run --configuration Release "large_file.aasx"

# Memory profiling
dotnet run --configuration Release "file.aasx" --memory-profile
```

## Deployment

### Standalone Deployment
```bash
# Publish self-contained
dotnet publish --configuration Release --self-contained true --runtime win-x64

# Publish single file
dotnet publish --configuration Release --self-contained true --runtime win-x64 -p:PublishSingleFile=true
```

### Docker Deployment
```dockerfile
FROM mcr.microsoft.com/dotnet/runtime:6.0
COPY bin/Release/net6.0/ /app/
WORKDIR /app
ENTRYPOINT ["dotnet", "AasProcessor.dll"]
```

### CI/CD Integration
```yaml
# GitHub Actions example
- name: Build AAS Processor
  run: |
    cd aas-processor
    dotnet build --configuration Release
    
- name: Test AAS Processor
  run: |
    cd aas-processor
    dotnet test
    
- name: Deploy AAS Processor
  run: |
    cd aas-processor
    dotnet publish --configuration Release
```

## Troubleshooting

### Build Issues

#### Missing Dependencies
```bash
# Restore packages
dotnet restore

# Clear cache
dotnet clean
dotnet restore
```

#### Version Conflicts
```bash
# Update packages
dotnet add package AasCore.Aas3.Package --version 1.0.0
dotnet restore
```

### Runtime Issues

#### .NET Runtime Not Found
```bash
# Install .NET 6.0 Runtime
# Download from: https://dotnet.microsoft.com/download/dotnet/6.0
```

#### Permission Denied
```bash
# Check file permissions
chmod +x bin/Release/net6.0/AasProcessor.dll

# Run with elevated privileges (if needed)
sudo dotnet run --configuration Release "file.aasx"
```

### Performance Issues

#### Slow Processing
```bash
# Use Release build
dotnet build --configuration Release

# Check system resources
top
free -h
```

#### Memory Issues
```bash
# Monitor memory usage
dotnet run --configuration Release "file.aasx" --memory-profile

# Process smaller files
split -b 10M large_file.aasx
```

## Contributing

### Development Setup
1. **Clone repository**
2. **Install .NET 6.0 SDK**
3. **Open in IDE** (Visual Studio, VS Code, Rider)
4. **Restore dependencies**
5. **Build project**

### Coding Standards
- **C# Coding Conventions** - Follow Microsoft guidelines
- **XML Documentation** - Document public APIs
- **Error Handling** - Comprehensive exception handling
- **Performance** - Optimize for large files
- **Testing** - Unit tests for new features

### Testing Guidelines
- **Unit Tests** - Test individual methods
- **Integration Tests** - Test file processing
- **Performance Tests** - Test with large files
- **Error Tests** - Test error conditions

## License

This project is part of the QI Digital Platform and follows the same licensing terms.

## Support

### Documentation
- [AAS Specification](https://www.plattform-i40.de/I40/Redaktion/EN/Downloads/Publikation/Details_of_the_Asset_Administration_Shell_Part1_V3.html)
- [AAS Core Libraries](https://github.com/admin-shell-io/aas-core-dotnet)
- [.NET Documentation](https://docs.microsoft.com/dotnet/)

### Issues and Questions
1. **Check troubleshooting section**
2. **Review error logs**
3. **Test with sample files**
4. **Create detailed bug reports**

---

**Version:** 1.0.0  
**Last Updated:** July 8, 2025  
**Status:** Production Ready 