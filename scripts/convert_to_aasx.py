#!/usr/bin/env python3
"""
Convert XML AAS files to proper AASX format

This script converts XML-based AAS files to the standard AASX format
by packaging them as ZIP files with the correct AASX structure.
"""

import os
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
import json
from datetime import datetime
import argparse
import logging

def setup_logging():
    """Setup logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def parse_aas_xml(xml_file_path):
    """Parse AAS XML file and extract basic information"""
    try:
        tree = ET.parse(xml_file_path)
        root = tree.getroot()
        
        # Extract namespace
        namespaces = {
            'aas': 'http://www.admin-shell.io/aas/1/0',
            'xsi': 'http://www.w3.org/2001/XMLSchema-instance'
        }
        
        # Count assets and submodels
        assets = root.findall('.//aas:asset', namespaces)
        submodels = root.findall('.//aas:submodel', namespaces)
        shells = root.findall('.//aas:assetAdministrationShell', namespaces)
        
        return {
            'assets_count': len(assets),
            'submodels_count': len(submodels),
            'shells_count': len(shells),
            'xml_content': ET.tostring(root, encoding='unicode')
        }
    except Exception as e:
        logging.error(f"Error parsing XML file {xml_file_path}: {e}")
        return None

def create_aasx_manifest(asset_info):
    """Create AASX manifest file"""
    manifest = {
        "aasx": {
            "fileVersion": "1.0",
            "aasxOrigin": {
                "aas": {
                    "assetAdministrationShells": [],
                    "assets": [],
                    "submodels": [],
                    "conceptDescriptions": []
                }
            },
            "files": []
        }
    }
    
    # Add file entries
    manifest["aasx"]["files"].append({
        "contentType": "application/xml",
        "path": "aasx/aas.xml"
    })
    
    return manifest

def convert_xml_to_aasx(xml_file_path, output_dir):
    """Convert XML AAS file to AASX format"""
    logger = logging.getLogger(__name__)
    
    xml_path = Path(xml_file_path)
    if not xml_path.exists():
        logger.error(f"XML file not found: {xml_file_path}")
        return False
    
    # Parse the XML file
    asset_info = parse_aas_xml(xml_path)
    if not asset_info:
        return False
    
    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create AASX file name
    aasx_filename = xml_path.stem + "_converted.aasx"
    aasx_path = output_path / aasx_filename
    
    try:
        with zipfile.ZipFile(aasx_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            # Add AASX manifest
            manifest = create_aasx_manifest(asset_info)
            zip_file.writestr('AASX-Origin', json.dumps(manifest, indent=2))
            
            # Add the XML content
            zip_file.writestr('aasx/aas.xml', asset_info['xml_content'])
            
            # Add a simple thumbnail (optional)
            thumbnail_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="200" height="150" xmlns="http://www.w3.org/2000/svg">
  <rect width="200" height="150" fill="#f0f0f0"/>
  <text x="100" y="75" text-anchor="middle" font-family="Arial" font-size="12" fill="#333">
    AAS: {xml_path.stem}
  </text>
  <text x="100" y="95" text-anchor="middle" font-family="Arial" font-size="10" fill="#666">
    Assets: {asset_info['assets_count']} | Submodels: {asset_info['submodels_count']}
  </text>
</svg>"""
            zip_file.writestr('aasx/thumbnail.svg', thumbnail_content)
            
            # Add metadata
            metadata = {
                "conversion_info": {
                    "original_file": str(xml_path),
                    "converted_at": datetime.now().isoformat(),
                    "assets_count": asset_info['assets_count'],
                    "submodels_count": asset_info['submodels_count'],
                    "shells_count": asset_info['shells_count']
                }
            }
            zip_file.writestr('aasx/metadata.json', json.dumps(metadata, indent=2))
        
        logger.info(f"Successfully converted {xml_path.name} to {aasx_filename}")
        logger.info(f"  - Assets: {asset_info['assets_count']}")
        logger.info(f"  - Submodels: {asset_info['submodels_count']}")
        logger.info(f"  - Shells: {asset_info['shells_count']}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating AASX file: {e}")
        return False

def convert_directory(input_dir, output_dir):
    """Convert all XML files in a directory to AASX format"""
    logger = logging.getLogger(__name__)
    
    input_path = Path(input_dir)
    if not input_path.exists():
        logger.error(f"Input directory not found: {input_dir}")
        return False
    
    # Find all XML files
    xml_files = list(input_path.glob("*.xml")) + list(input_path.glob("*.aasx"))
    
    if not xml_files:
        logger.warning(f"No XML or AASX files found in {input_dir}")
        return False
    
    logger.info(f"Found {len(xml_files)} files to convert")
    
    success_count = 0
    for xml_file in xml_files:
        if convert_xml_to_aasx(xml_file, output_dir):
            success_count += 1
    
    logger.info(f"Conversion completed: {success_count}/{len(xml_files)} files converted successfully")
    return success_count > 0

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description='Convert XML AAS files to AASX format')
    parser.add_argument('--input', '-i', required=True, help='Input XML file or directory')
    parser.add_argument('--output', '-o', default='../data/aasx-examples/converted', help='Output directory')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    logger = setup_logging()
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("=" * 60)
    logger.info("AAS XML to AASX Converter")
    logger.info("=" * 60)
    
    input_path = Path(args.input)
    output_path = Path(args.output)
    
    if input_path.is_file():
        # Convert single file
        success = convert_xml_to_aasx(input_path, output_path)
        if success:
            logger.info(f"✅ Successfully converted: {input_path.name}")
        else:
            logger.error(f"❌ Failed to convert: {input_path.name}")
            return 1
    elif input_path.is_dir():
        # Convert directory
        success = convert_directory(input_path, output_path)
        if not success:
            return 1
    else:
        logger.error(f"Input path does not exist: {args.input}")
        return 1
    
    logger.info("=" * 60)
    logger.info("Conversion completed!")
    logger.info(f"Output directory: {output_path}")
    logger.info("=" * 60)
    
    return 0

if __name__ == "__main__":
    exit(main()) 