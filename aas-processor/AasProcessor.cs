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
                        }
                        // Process JSON files
                        else if (entry.Name.EndsWith(".json"))
                        {
                            jsonFiles.Add(entry.Name);
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
                        else if (entry.Name.EndsWith(".xml") && !entry.Name.StartsWith("[Content_Types]") && entry.Name.Contains(".aas.xml"))
                        {
                            xmlFiles.Add(entry.Name);
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

                // Create namespace manager
                var nsManager = new System.Xml.XmlNamespaceManager(doc.NameTable);
                nsManager.AddNamespace("aas", "http://www.admin-shell.io/aas/1/0");
                nsManager.AddNamespace("xsi", "http://www.w3.org/2001/XMLSchema-instance");

                // Extract Asset Administration Shells (AAS 1.0 format)
                var aasNodes = doc.SelectNodes("//aas:assetAdministrationShell", nsManager);
                if (aasNodes != null)
                {
                    foreach (System.Xml.XmlNode aasNode in aasNodes)
                    {
                        var asset = new
                        {
                            id = GetXmlElementText(aasNode, "aas:identification"),
                            idShort = GetXmlElementText(aasNode, "aas:idShort"),
                            description = GetXmlDescription(aasNode),
                            kind = GetXmlElementText(aasNode, "aas:category"),
                            source = sourceFile,
                            format = "XML_AAS_1_0"
                        };
                        assets.Add(asset);
                        Console.WriteLine($"Found Asset Administration Shell: {asset.idShort} (ID: {asset.id})");
                    }
                }

                // Extract Assets (AAS 1.0 format)
                var assetNodes = doc.SelectNodes("//aas:asset", nsManager);
                if (assetNodes != null)
                {
                    foreach (System.Xml.XmlNode assetNode in assetNodes)
                    {
                        var asset = new
                        {
                            id = GetXmlElementText(assetNode, "aas:identification"),
                            idShort = GetXmlElementText(assetNode, "aas:idShort"),
                            description = GetXmlDescription(assetNode),
                            kind = GetXmlElementText(assetNode, "aas:kind"),
                            source = sourceFile,
                            format = "XML_AAS_1_0"
                        };
                        assets.Add(asset);
                        Console.WriteLine($"Found Asset: {asset.idShort} (ID: {asset.id})");
                    }
                }

                // Extract Submodels (AAS 1.0 format)
                var submodelNodes = doc.SelectNodes("//aas:submodel", nsManager);
                if (submodelNodes != null)
                {
                    foreach (System.Xml.XmlNode submodelNode in submodelNodes)
                    {
                        var submodelData = new
                        {
                            id = GetXmlElementText(submodelNode, "aas:identification"),
                            idShort = GetXmlElementText(submodelNode, "aas:idShort"),
                            description = GetXmlDescription(submodelNode),
                            kind = GetXmlElementText(submodelNode, "aas:kind"),
                            source = sourceFile,
                            format = "XML_AAS_1_0"
                        };
                        submodels.Add(submodelData);
                        Console.WriteLine($"Found Submodel: {submodelData.idShort} (ID: {submodelData.id})");
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error parsing XML: {ex.Message}");
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
    }
}