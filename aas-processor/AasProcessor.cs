using System;
using System.IO;
using System.Text.Json;
using System.Collections.Generic;
using System.Linq;

namespace AasProcessor
{
    /// <summary>
    /// AASX Package Processor using official AasCore.Aas3.Package library
    /// </summary>
    public class AasProcessor
    {
        /// <summary>
        /// Process an AASX file and return structured data
        /// </summary>
        /// <param name="aasxFilePath">Path to the AASX file</param>
        /// <returns>JSON string containing processed AAS data</returns>
        public string ProcessAasxFile(string aasxFilePath)
        {
            try
            {
                if (!File.Exists(aasxFilePath))
                {
                    throw new FileNotFoundException($"AASX file not found: {aasxFilePath}");
                }

                // For now, we'll use basic ZIP processing since the AAS Core library
                // has namespace issues with .NET 6.0
                var result = ProcessAasxBasic(aasxFilePath);
                
                return JsonSerializer.Serialize(result, new JsonSerializerOptions
                {
                    WriteIndented = true,
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase
                });
            }
            catch (Exception ex)
            {
                var error = new
                {
                    error = ex.Message,
                    processing_method = "basic_zip_processing",
                    file_path = aasxFilePath,
                    processing_timestamp = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ")
                };

                return JsonSerializer.Serialize(error, new JsonSerializerOptions
                {
                    WriteIndented = true,
                    PropertyNamingPolicy = JsonNamingPolicy.CamelCase
                });
            }
        }

        /// <summary>
        /// Basic AASX processing using ZIP file operations
        /// </summary>
        private object ProcessAasxBasic(string aasxFilePath)
        {
            var fileInfo = new FileInfo(aasxFilePath);
            var documents = new List<object>();
            var assets = new List<object>();
            var submodels = new List<object>();
            var jsonFiles = new List<string>();
            var xmlFiles = new List<string>();

            try
            {
                using (var zip = System.IO.Compression.ZipFile.OpenRead(aasxFilePath))
                {
                    foreach (var entry in zip.Entries)
                    {
                        Console.WriteLine($"Found entry: {entry.Name}");
                        
                        // Extract documents
                        if (entry.Name.EndsWith(".pdf") || entry.Name.EndsWith(".doc") || 
                            entry.Name.EndsWith(".docx") || entry.Name.EndsWith(".txt"))
                        {
                            documents.Add(new
                            {
                                filename = entry.Name,
                                size = entry.Length,
                                type = Path.GetExtension(entry.Name)
                            });
                            Console.WriteLine($"Added document: {entry.Name}");
                        }
                        // Process JSON files
                        else if (entry.Name.EndsWith(".json"))
                        {
                            jsonFiles.Add(entry.Name);
                            Console.WriteLine($"Processing JSON file: {entry.Name}");
                            try
                            {
                                using (var stream = entry.Open())
                                using (var reader = new StreamReader(stream))
                                {
                                    var content = reader.ReadToEnd();
                                    var jsonData = JsonSerializer.Deserialize<JsonElement>(content);
                                    
                                    // Extract AAS data from JSON
                                    ExtractAasFromJson(jsonData, assets, submodels, entry.Name);
                                }
                            }
                            catch (Exception ex)
                            {
                                Console.WriteLine($"Error processing JSON {entry.Name}: {ex.Message}");
                            }
                        }
                        // Process XML files (AAS data)
                        else if (entry.Name.EndsWith(".xml") && !entry.Name.StartsWith("[Content_Types]"))
                        {
                            Console.WriteLine($"Found XML file: {entry.Name}");
                            // Check if it's an AAS XML file
                            if (entry.Name.Contains(".aas.xml") || entry.Name.Contains("/aas.xml") || entry.Name.Contains("\\aas.xml") || entry.Name.Contains("aas.xml"))
                            {
                                xmlFiles.Add(entry.Name);
                                Console.WriteLine($"Processing AAS XML file: {entry.Name}");
                                try
                                {
                                    using (var stream = entry.Open())
                                    using (var reader = new StreamReader(stream))
                                    {
                                        var content = reader.ReadToEnd();
                                        Console.WriteLine($"Processing XML file: {entry.Name}");
                                        
                                        // Extract AAS data from XML
                                        ExtractAasFromXml(content, assets, submodels, entry.Name);
                                    }
                                }
                                catch (Exception ex)
                                {
                                    Console.WriteLine($"Error processing XML {entry.Name}: {ex.Message}");
                                }
                            }
                            else
                            {
                                Console.WriteLine($"Skipping non-AAS XML file: {entry.Name}");
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                throw new Exception($"Error processing AASX file: {ex.Message}");
            }

            return new
            {
                processing_method = "enhanced_zip_processing",
                file_path = aasxFilePath,
                file_size = fileInfo.Length,
                processing_timestamp = DateTime.UtcNow.ToString("yyyy-MM-ddTHH:mm:ssZ"),
                libraries_used = new[] { "System.IO.Compression", "System.Text.Json", "System.Xml" },
                assets = assets,
                submodels = submodels,
                documents = documents,
                raw_data = new
                {
                    json_files = jsonFiles,
                    xml_files = xmlFiles
                }
            };
        }

        private void ExtractAasFromJson(JsonElement jsonData, List<object> assets, List<object> submodels, string sourceFile)
        {
            // Try to extract AAS data from JSON
            if (jsonData.TryGetProperty("assetAdministrationShells", out var aasArray))
            {
                foreach (var aas in aasArray.EnumerateArray())
                {
                    var asset = new
                    {
                        id = GetJsonProperty(aas, "id"),
                        idShort = GetJsonProperty(aas, "idShort"),
                        description = GetDescription(aas),
                        kind = GetJsonProperty(aas, "kind"),
                        source = sourceFile,
                        format = "JSON"
                    };
                    assets.Add(asset);
                }
            }
            
            if (jsonData.TryGetProperty("submodels", out var submodelArray))
            {
                foreach (var submodel in submodelArray.EnumerateArray())
                {
                    var submodelData = new
                    {
                        id = GetJsonProperty(submodel, "id"),
                        idShort = GetJsonProperty(submodel, "idShort"),
                        description = GetDescription(submodel),
                        kind = GetJsonProperty(submodel, "kind"),
                        source = sourceFile,
                        format = "JSON"
                    };
                    submodels.Add(submodelData);
                }
            }
        }

        private void ExtractAasFromXml(string xmlContent, List<object> assets, List<object> submodels, string sourceFile)
        {
            try
            {
                var doc = new System.Xml.XmlDocument();
                doc.LoadXml(xmlContent);

                // Detect AAS version and namespace from the XML
                var aasVersion = DetectAasVersion(doc);
                Console.WriteLine($"Detected AAS version: {aasVersion}");

                // Create comprehensive namespace manager
                var nsManager = CreateComprehensiveNamespaceManager(doc);

                // Extract data based on detected version
                switch (aasVersion)
                {
                    case "AAS_1_0":
                        ExtractAas10Data(doc, nsManager, assets, submodels, sourceFile);
                        break;
                    case "AAS_3_0":
                        ExtractAas30Data(doc, nsManager, assets, submodels, sourceFile);
                        break;
                    default:
                        // Try all known formats
                        ExtractAas10Data(doc, nsManager, assets, submodels, sourceFile);
                        ExtractAas30Data(doc, nsManager, assets, submodels, sourceFile);
                        break;
                }

                // If no data found, try generic extraction
                if (assets.Count == 0 && submodels.Count == 0)
                {
                    ExtractGenericAasData(doc, assets, submodels, sourceFile);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error parsing XML: {ex.Message}");
            }
        }

        private string DetectAasVersion(System.Xml.XmlDocument doc)
        {
            try
            {
                // Check root element for AAS version indicators
                var root = doc.DocumentElement;
                if (root != null)
                {
                    var rootName = root.Name.ToLower();
                    var rootNamespace = root.NamespaceURI;

                    if (rootNamespace.Contains("aas/3/0") || rootName.Contains("aasenv3"))
                        return "AAS_3_0";
                    else if (rootNamespace.Contains("aas/1/0") || rootName.Contains("aasenv"))
                        return "AAS_1_0";
                }

                // Check for version-specific elements
                var aas3Nodes = doc.SelectNodes("//*[contains(local-name(), 'assetAdministrationShell')]");
                var aas1Nodes = doc.SelectNodes("//*[contains(local-name(), 'assetAdministrationShell')]");

                if (aas3Nodes != null && aas3Nodes.Count > 0)
                    return "AAS_3_0";
                else if (aas1Nodes != null && aas1Nodes.Count > 0)
                    return "AAS_1_0";

                return "UNKNOWN";
            }
            catch
            {
                return "UNKNOWN";
            }
        }

        private System.Xml.XmlNamespaceManager CreateComprehensiveNamespaceManager(System.Xml.XmlDocument doc)
        {
            var nsManager = new System.Xml.XmlNamespaceManager(doc.NameTable);
            
            // Add all possible AAS namespaces and prefixes
            nsManager.AddNamespace("aas", "http://www.admin-shell.io/aas/1/0");
            nsManager.AddNamespace("aas3", "http://www.admin-shell.io/aas/3/0");
            nsManager.AddNamespace("ns0", "http://www.admin-shell.io/aas/1/0");
            nsManager.AddNamespace("ns1", "http://www.admin-shell.io/aas/3/0");
            nsManager.AddNamespace("xsi", "http://www.w3.org/2001/XMLSchema-instance");
            
            // Add any namespaces found in the document
            try
            {
                var root = doc.DocumentElement;
                if (root != null && root.Attributes != null)
                {
                    foreach (System.Xml.XmlAttribute attr in root.Attributes)
                    {
                        if (attr.Name.StartsWith("xmlns:"))
                        {
                            var prefix = attr.Name.Substring(6); // Remove "xmlns:"
                            nsManager.AddNamespace(prefix, attr.Value);
                        }
                    }
                }
            }
            catch
            {
                // Ignore namespace extraction errors
            }

            return nsManager;
        }

        private void ExtractAas10Data(System.Xml.XmlDocument doc, System.Xml.XmlNamespaceManager nsManager, 
            List<object> assets, List<object> submodels, string sourceFile)
        {
            // Use a HashSet to track processed IDs to avoid duplicates
            var processedAssetIds = new HashSet<string>();
            var processedSubmodelIds = new HashSet<string>();
            
            // Try multiple prefixes for AAS 1.0
            var prefixes = new[] { "aas", "ns0" };
            
            foreach (var prefix in prefixes)
            {
                // Extract Asset Administration Shells
                var aasNodes = doc.SelectNodes($"//{prefix}:assetAdministrationShell", nsManager);
                if (aasNodes != null)
                {
                    foreach (System.Xml.XmlNode aasNode in aasNodes)
                    {
                        var assetId = GetXmlElementTextWithPrefixes(aasNode, "identification");
                        if (!string.IsNullOrEmpty(assetId) && !processedAssetIds.Contains(assetId))
                        {
                            var asset = new
                            {
                                id = assetId,
                                idShort = GetXmlElementTextWithPrefixes(aasNode, "idShort"),
                                description = GetXmlDescriptionWithPrefixes(aasNode),
                                kind = GetXmlElementTextWithPrefixes(aasNode, "category"),
                                source = sourceFile,
                                format = "XML_AAS_1_0"
                            };
                            assets.Add(asset);
                            processedAssetIds.Add(assetId);
                            Console.WriteLine($"Found AAS 1.0 Asset Administration Shell: {asset.idShort} (ID: {asset.id})");
                        }
                    }
                }

                // Extract Assets
                var assetNodes = doc.SelectNodes($"//{prefix}:asset", nsManager);
                if (assetNodes != null)
                {
                    foreach (System.Xml.XmlNode assetNode in assetNodes)
                    {
                        var assetId = GetXmlElementTextWithPrefixes(assetNode, "identification");
                        if (!string.IsNullOrEmpty(assetId) && !processedAssetIds.Contains(assetId))
                        {
                            var asset = new
                            {
                                id = assetId,
                                idShort = GetXmlElementTextWithPrefixes(assetNode, "idShort"),
                                description = GetXmlDescriptionWithPrefixes(assetNode),
                                kind = GetXmlElementTextWithPrefixes(assetNode, "kind"),
                                source = sourceFile,
                                format = "XML_AAS_1_0"
                            };
                            assets.Add(asset);
                            processedAssetIds.Add(assetId);
                            Console.WriteLine($"Found AAS 1.0 Asset: {asset.idShort} (ID: {asset.id})");
                        }
                    }
                }

                // Extract Submodels
                var submodelNodes = doc.SelectNodes($"//{prefix}:submodel", nsManager);
                if (submodelNodes != null)
                {
                    foreach (System.Xml.XmlNode submodelNode in submodelNodes)
                    {
                        var submodelId = GetXmlElementTextWithPrefixes(submodelNode, "identification");
                        if (!string.IsNullOrEmpty(submodelId) && !processedSubmodelIds.Contains(submodelId))
                        {
                            var submodelData = new
                            {
                                id = submodelId,
                                idShort = GetXmlElementTextWithPrefixes(submodelNode, "idShort"),
                                description = GetXmlDescriptionWithPrefixes(submodelNode),
                                kind = GetXmlElementTextWithPrefixes(submodelNode, "kind"),
                                source = sourceFile,
                                format = "XML_AAS_1_0"
                            };
                            submodels.Add(submodelData);
                            processedSubmodelIds.Add(submodelId);
                            Console.WriteLine($"Found AAS 1.0 Submodel: {submodelData.idShort} (ID: {submodelData.id})");
                        }
                    }
                }
            }
        }

        private void ExtractAas30Data(System.Xml.XmlDocument doc, System.Xml.XmlNamespaceManager nsManager,
            List<object> assets, List<object> submodels, string sourceFile)
        {
            // Try multiple prefixes for AAS 3.0
            var prefixes = new[] { "aas3", "ns1" };
            
            foreach (var prefix in prefixes)
            {
                // Extract Asset Administration Shells (AAS 3.0)
                var aasNodes = doc.SelectNodes($"//{prefix}:assetAdministrationShell", nsManager);
                if (aasNodes != null)
                {
                    foreach (System.Xml.XmlNode aasNode in aasNodes)
                    {
                        var asset = new
                        {
                            id = GetXmlElementTextWithPrefixes(aasNode, "id"),
                            idShort = GetXmlElementTextWithPrefixes(aasNode, "idShort"),
                            description = GetXmlDescriptionWithPrefixes(aasNode),
                            kind = GetXmlElementTextWithPrefixes(aasNode, "kind"),
                            source = sourceFile,
                            format = "XML_AAS_3_0"
                        };
                        assets.Add(asset);
                        Console.WriteLine($"Found AAS 3.0 Asset Administration Shell: {asset.idShort} (ID: {asset.id})");
                    }
                }

                // Extract Submodels (AAS 3.0)
                var submodelNodes = doc.SelectNodes($"//{prefix}:submodel", nsManager);
                if (submodelNodes != null)
                {
                    foreach (System.Xml.XmlNode submodelNode in submodelNodes)
                    {
                        var submodelData = new
                        {
                            id = GetXmlElementTextWithPrefixes(submodelNode, "id"),
                            idShort = GetXmlElementTextWithPrefixes(submodelNode, "idShort"),
                            description = GetXmlDescriptionWithPrefixes(submodelNode),
                            kind = GetXmlElementTextWithPrefixes(submodelNode, "kind"),
                            source = sourceFile,
                            format = "XML_AAS_3_0"
                        };
                        submodels.Add(submodelData);
                        Console.WriteLine($"Found AAS 3.0 Submodel: {submodelData.idShort} (ID: {submodelData.id})");
                    }
                }
            }
        }

        private void ExtractGenericAasData(System.Xml.XmlDocument doc, List<object> assets, List<object> submodels, string sourceFile)
        {
            // Generic extraction using XPath without namespace prefixes
            try
            {
                // Find any element that might be an asset administration shell
                var aasNodes = doc.SelectNodes("//*[contains(local-name(), 'assetAdministrationShell')]");
                if (aasNodes != null)
                {
                    foreach (System.Xml.XmlNode aasNode in aasNodes)
                    {
                        var asset = new
                        {
                            id = GetGenericElementText(aasNode, "identification") ?? GetGenericElementText(aasNode, "id"),
                            idShort = GetGenericElementText(aasNode, "idShort"),
                            description = GetGenericDescription(aasNode),
                            kind = GetGenericElementText(aasNode, "category") ?? GetGenericElementText(aasNode, "kind"),
                            source = sourceFile,
                            format = "XML_GENERIC"
                        };
                        assets.Add(asset);
                        Console.WriteLine($"Found Generic Asset Administration Shell: {asset.idShort} (ID: {asset.id})");
                    }
                }

                // Find any element that might be a submodel
                var submodelNodes = doc.SelectNodes("//*[contains(local-name(), 'submodel')]");
                if (submodelNodes != null)
                {
                    foreach (System.Xml.XmlNode submodelNode in submodelNodes)
                    {
                        var submodelData = new
                        {
                            id = GetGenericElementText(submodelNode, "identification") ?? GetGenericElementText(submodelNode, "id"),
                            idShort = GetGenericElementText(submodelNode, "idShort"),
                            description = GetGenericDescription(submodelNode),
                            kind = GetGenericElementText(submodelNode, "kind"),
                            source = sourceFile,
                            format = "XML_GENERIC"
                        };
                        submodels.Add(submodelData);
                        Console.WriteLine($"Found Generic Submodel: {submodelData.idShort} (ID: {submodelData.id})");
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error in generic extraction: {ex.Message}");
            }
        }

        private System.Xml.XmlNamespaceManager CreateNamespaceManager(System.Xml.XmlDocument doc)
        {
            var nsManager = new System.Xml.XmlNamespaceManager(doc.NameTable);
            // Support both AAS 1.0 and 3.0 namespaces
            nsManager.AddNamespace("aas", "http://www.admin-shell.io/aas/1/0");
            nsManager.AddNamespace("aas3", "http://www.admin-shell.io/aas/3/0");
            nsManager.AddNamespace("xsi", "http://www.w3.org/2001/XMLSchema-instance");
            return nsManager;
        }

        private string GetXmlAttribute(System.Xml.XmlNode node, string attributeName)
        {
            var attr = node.Attributes?[attributeName];
            return attr?.Value ?? "";
        }

        private string GetXmlElementText(System.Xml.XmlNode node, string elementName)
        {
            try
            {
                var element = node.SelectSingleNode(elementName, CreateNamespaceManager(node.OwnerDocument));
                if (element != null)
                {
                    // For identification elements, get the text content
                    if (elementName == "aas:identification")
                    {
                        return element.InnerText ?? "";
                    }
                    return element.InnerText ?? "";
                }
            }
            catch
            {
                // If namespace query fails, try without namespace
                try
                {
                    var elementNameWithoutNs = elementName.Replace("aas:", "");
                    var element = node.SelectSingleNode(elementNameWithoutNs);
                    if (element != null)
                    {
                        return element.InnerText ?? "";
                    }
                }
                catch
                {
                    // Ignore errors
                }
            }
            return "";
        }

        private string GetJsonProperty(JsonElement element, string propertyName)
        {
            if (element.TryGetProperty(propertyName, out var property))
            {
                return property.GetString() ?? "";
            }
            return "";
        }

        private string GetDescription(JsonElement element)
        {
            if (element.TryGetProperty("description", out var description))
            {
                if (description.ValueKind == JsonValueKind.String)
                {
                    return description.GetString() ?? "";
                }
                else if (description.ValueKind == JsonValueKind.Object)
                {
                    // Try to get English description
                    if (description.TryGetProperty("en", out var enDesc))
                    {
                        return enDesc.GetString() ?? "";
                    }
                    // Get first available description
                    foreach (var prop in description.EnumerateObject())
                    {
                        return prop.Value.GetString() ?? "";
                    }
                }
            }
            return "";
        }

        private string GetXmlDescription(System.Xml.XmlNode node)
        {
            try
            {
                var descriptionNode = node.SelectSingleNode("aas:description", CreateNamespaceManager(node.OwnerDocument));
                if (descriptionNode != null)
                {
                    var langStringNode = descriptionNode.SelectSingleNode("aas:langString[@lang='EN']", CreateNamespaceManager(node.OwnerDocument));
                    if (langStringNode != null)
                    {
                        return langStringNode.InnerText ?? "";
                    }
                    // Fallback to any langString
                    var anyLangString = descriptionNode.SelectSingleNode("aas:langString", CreateNamespaceManager(node.OwnerDocument));
                    return anyLangString?.InnerText ?? "";
                }
            }
            catch
            {
                // Ignore errors and return empty string
            }
            return "";
        }

        private string GetXmlElementTextWithPrefixes(System.Xml.XmlNode node, string elementName)
        {
            // Try with aas: prefix first
            var result = GetXmlElementText(node, "aas:" + elementName);
            if (!string.IsNullOrEmpty(result))
                return result;
            
            // Try with ns0: prefix
            result = GetXmlElementText(node, "ns0:" + elementName);
            if (!string.IsNullOrEmpty(result))
                return result;
            
            // Try without prefix
            return GetXmlElementText(node, elementName);
        }

        private string GetXmlDescriptionWithPrefixes(System.Xml.XmlNode node)
        {
            // Try with aas: prefix first
            try
            {
                var descriptionNode = node.SelectSingleNode("aas:description", CreateNamespaceManager(node.OwnerDocument));
                if (descriptionNode != null)
                {
                    var langStringNode = descriptionNode.SelectSingleNode("aas:langString[@lang='EN']", CreateNamespaceManager(node.OwnerDocument));
                    if (langStringNode != null)
                    {
                        return langStringNode.InnerText ?? "";
                    }
                    // Fallback to any langString
                    var anyLangString = descriptionNode.SelectSingleNode("aas:langString", CreateNamespaceManager(node.OwnerDocument));
                    return anyLangString?.InnerText ?? "";
                }
            }
            catch
            {
                // Ignore errors and continue
            }
            
            // Try with ns0: prefix
            try
            {
                var descriptionNode = node.SelectSingleNode("ns0:description", CreateNamespaceManager(node.OwnerDocument));
                if (descriptionNode != null)
                {
                    var langStringNode = descriptionNode.SelectSingleNode("ns0:langString[@lang='EN']", CreateNamespaceManager(node.OwnerDocument));
                    if (langStringNode != null)
                    {
                        return langStringNode.InnerText ?? "";
                    }
                    // Fallback to any langString
                    var anyLangString = descriptionNode.SelectSingleNode("ns0:langString", CreateNamespaceManager(node.OwnerDocument));
                    return anyLangString?.InnerText ?? "";
                }
            }
            catch
            {
                // Ignore errors and continue
            }
            
            return "";
        }

        private string GetGenericElementText(System.Xml.XmlNode node, string elementName)
        {
            try
            {
                // Try to find element by local name (ignoring namespace)
                var element = node.SelectSingleNode($"*[local-name()='{elementName}']");
                if (element != null)
                {
                    return element.InnerText ?? "";
                }
            }
            catch
            {
                // Ignore errors
            }
            return null;
        }

        private string GetGenericDescription(System.Xml.XmlNode node)
        {
            try
            {
                // Try to find description element
                var descriptionNode = node.SelectSingleNode("*[local-name()='description']");
                if (descriptionNode != null)
                {
                    // Try to find English langString
                    var langStringNode = descriptionNode.SelectSingleNode("*[local-name()='langString'][@lang='EN']");
                    if (langStringNode != null)
                    {
                        return langStringNode.InnerText ?? "";
                    }
                    
                    // Fallback to any langString
                    var anyLangString = descriptionNode.SelectSingleNode("*[local-name()='langString']");
                    if (anyLangString != null)
                    {
                        return anyLangString.InnerText ?? "";
                    }
                    
                    // Fallback to direct text content
                    return descriptionNode.InnerText ?? "";
                }
            }
            catch
            {
                // Ignore errors
            }
            return "";
        }
    }
}