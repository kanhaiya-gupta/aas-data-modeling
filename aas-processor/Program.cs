using System;
using System.IO;

namespace AasProcessor
{
    class Program
    {
        static void Main(string[] args)
        {
            if (args.Length < 1)
            {
                Console.WriteLine("Usage: AasProcessor <aasx-file-path> [output-json-path]");
                Console.WriteLine("Example: AasProcessor Example_AAS_ServoDCMotor_21.aasx output.json");
                return;
            }

            string aasxFilePath = args[0];
            string outputPath = args.Length > 1 ? args[1] : null;

            try
            {
                var processor = new AasProcessor();
                string result = processor.ProcessAasxFile(aasxFilePath);

                if (outputPath != null)
                {
                    File.WriteAllText(outputPath, result);
                    Console.WriteLine($"AASX data exported to: {outputPath}");
                }
                else
                {
                    Console.WriteLine(result);
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
                Environment.Exit(1);
            }
        }
    }
} 