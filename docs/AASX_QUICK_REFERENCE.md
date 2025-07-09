# AASX Processing Quick Reference

## Quick Start

### 1. Build .NET Processor
```bash
cd aas-processor
dotnet build --configuration Release
```

### 2. Test Processing
```bash
# Test .NET bridge
python test_dotnet_bridge.py

# Test hybrid processing
python test_hybrid_processing.py

# Test full integration
python test_aasx_integration.py
```

### 3. Start Platform
```bash
python main.py
# Open: http://localhost:5000/aasx
```

## Common Operations

### Process AASX File via Command Line
```bash
# Direct .NET processing
cd aas-processor
dotnet run --configuration Release "path/to/file.aasx"

# Via Python bridge
python -c "
from webapp.aasx.dotnet_bridge import DotNetAasProcessor
processor = DotNetAasProcessor()
result = processor.process_aasx_file('path/to/file.aasx')
print(result)
"
```

### Process AASX File in Python Code
```python
from webapp.aasx.aasx_processor import AasxProcessor

processor = AasxProcessor()
result = processor.process_aasx_file("Example_AAS_ServoDCMotor_21.aasx")

# Access results
print(f"Assets: {len(result['assets'])}")
print(f"Submodels: {len(result['submodels'])}")
print(f"Documents: {len(result['documents'])}")
```

### Web Interface Operations
```python
# List available AASX files
GET /aasx/files

# Process specific file
GET /aasx/process/{filename}

# Launch AASX Package Explorer
GET /aasx/explorer

# Upload new file
POST /aasx/upload
```

## Data Structure

### Asset Object
```json
{
  "id": "http://customer.com/aas/9175_7013_7091_9168",
  "idShort": "ExampleMotor",
  "description": "Asset description",
  "kind": "CONSTANT",
  "source": "filename.aas.xml",
  "format": "XML_AAS_1_0"
}
```

### Submodel Object
```json
{
  "id": "http://i40.customer.com/type/1/1/F13E8576F6488342",
  "idShort": "Identification",
  "description": "Identification from Manufacturer",
  "kind": "Instance",
  "source": "filename.aas.xml",
  "format": "XML_AAS_1_0"
}
```

### Document Object
```json
{
  "filename": "OperatingManual.pdf",
  "size": 194061,
  "type": ".pdf"
}
```

## Processing Methods

### 1. Enhanced ZIP Processing (Recommended)
- Uses .NET bridge
- Full AAS parsing
- Multi-format support
- Best performance

### 2. Basic ZIP Processing (Fallback)
- Python-only
- Basic file extraction
- Limited parsing
- Available when .NET not available

### 3. File System Processing
- Direct file access
- No ZIP extraction
- For non-AASX files
- Debug/testing only

## Error Handling

### Common Errors
```python
# .NET processor not found
try:
    result = processor.process_aasx_file("file.aasx")
except FileNotFoundError:
    print("Build .NET processor first")

# Invalid AASX file
try:
    result = processor.process_aasx_file("invalid.aasx")
except Exception as e:
    print(f"Processing error: {e}")
```

### Debug Mode
```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Process with debug output
result = processor.process_aasx_file("file.aasx", debug=True)
```

## Performance Tips

### Large Files
```python
# Process in batches
files = ["file1.aasx", "file2.aasx", "file3.aasx"]
results = []

for file in files:
    result = processor.process_aasx_file(file)
    results.append(result)
```

### Memory Management
```python
# Clear cache after processing
processor.clear_cache()

# Process with memory limits
result = processor.process_aasx_file("large.aasx", max_memory_mb=512)
```

## Integration Examples

### AI/RAG Integration
```python
# Extract data for AI processing
result = processor.process_aasx_file("file.aasx")

# Use assets for knowledge graph
for asset in result['assets']:
    ai_system.add_asset(asset['id'], asset['description'])

# Use submodels for RAG
for submodel in result['submodels']:
    rag_system.add_document(submodel['id'], submodel['description'])
```

### Digital Twin Integration
```python
# Create twin from AASX
result = processor.process_aasx_file("twin.aasx")

# Map assets to twins
for asset in result['assets']:
    twin_registry.create_twin(
        asset_id=asset['id'],
        name=asset['idShort'],
        description=asset['description']
    )
```

### Certificate Management
```python
# Extract certificate data
result = processor.process_aasx_file("certificate.aasx")

# Create certificate from submodel
for submodel in result['submodels']:
    if "certificate" in submodel['idShort'].lower():
        certificate_manager.create_certificate(submodel)
```

## Troubleshooting

### Build Issues
```bash
# Clean and rebuild
cd aas-processor
dotnet clean
dotnet restore
dotnet build --configuration Release
```

### Runtime Issues
```bash
# Check .NET installation
dotnet --version

# Check Python environment
python --version
pip list | grep aas
```

### Processing Issues
```bash
# Test with example file
cd aas-processor
dotnet run --configuration Release "../AasxPackageExplorer/content-for-demo/Example_AAS_ServoDCMotor_21.aasx"

# Check file format
file "your_file.aasx"
unzip -l "your_file.aasx"
```

## Useful Commands

### File Inspection
```bash
# Check AASX structure
unzip -l file.aasx

# Extract and examine
mkdir temp && cd temp
unzip ../file.aasx
ls -la
head -20 *.xml
```

### Performance Testing
```bash
# Time processing
time python -c "
from webapp.aasx.aasx_processor import AasxProcessor
processor = AasxProcessor()
result = processor.process_aasx_file('file.aasx')
"

# Memory usage
python -m memory_profiler -m webapp.aasx.aasx_processor
```

### Batch Processing
```bash
# Process all AASX files
for file in *.aasx; do
    echo "Processing $file..."
    python -c "
from webapp.aasx.aasx_processor import AasxProcessor
processor = AasxProcessor()
result = processor.process_aasx_file('$file')
print(f'Assets: {len(result[\"assets\"])}, Submodels: {len(result[\"submodels\"])}')
"
done
```

## Configuration

### Environment Variables
```bash
# Set .NET processor path
export AAS_PROCESSOR_PATH="./aas-processor/bin/Release/net6.0/AasProcessor.dll"

# Set processing timeout
export AAS_PROCESSING_TIMEOUT=30

# Enable debug mode
export AAS_DEBUG=true
```

### Python Configuration
```python
# Configure processor
processor = AasxProcessor(
    dotnet_path="./aas-processor/bin/Release/net6.0/AasProcessor.dll",
    timeout=30,
    debug=True
)
```

---

**Quick Reference Version:** 1.0.0  
**Last Updated:** July 8, 2025 