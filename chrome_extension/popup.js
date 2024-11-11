document.getElementById("fetchButton").addEventListener("click", async () => {
    const url = document.getElementById("fileinput").value.trim();

    if (url !== "") {
        try {
            // Fetch HTML content from the provided URL
            const response = await fetch(url);
            const html = await response.text();

            // Display the HTML content in the HTML response textarea
            document.getElementById("htmlResponse").value = html;
        } catch (error) {
            alert("Error fetching the URL: " + error.message);
        }
    } else {
        alert("Please enter a valid URL.");
    }
});

document.getElementById("submitButton").addEventListener("click", () => {
    const xpathInput = document.getElementById("inputText").value.trim();
    const htmlContent = document.getElementById("htmlResponse").value.trim();

    // Check if HTML content and XPath input are provided
    if (htmlContent !== "" && xpathInput !== "") {
        let xpathExpression = "";

        try {
            // Try to parse the input as JSON to extract the XPath expression
            const parsedInput = JSON.parse(xpathInput);
            // Assuming the parsed input is an object with key-value pairs
            if (parsedInput && typeof parsedInput === "object" && Object.keys(parsedInput).length >= 1) {
                // Extract the XPath expressions from the JSON object
                const results = {};
                for (const [key, xpath] of Object.entries(parsedInput)) {
                    // Apply the XPath to the fetched HTML content
                    const parser = new DOMParser();
                    const doc = parser.parseFromString(htmlContent, "text/html");

                    const extractedData = extractDataFromXPath(doc, xpath);
                    results[key] = extractedData.length === 1 ? extractedData[0] : extractedData;
                }

                // Format and display the results
                document.getElementById("outputText").value = JSON.stringify(results, null, 2);
            } else {
                alert("Invalid JSON structure. Expected a key-value pair.");
                return;
            }
        } catch (jsonError) {
            alert("Error parsing the JSON input: " + jsonError.message);
        }
    } else {
        alert("Please provide both HTML content and a valid XPath expression.");
    }
});

// Function to extract data using XPath
function extractDataFromXPath(doc, xpath) {
    try {
        const xpathResult = doc.evaluate(xpath, doc, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
        const nodes = [];

        for (let i = 0; i < xpathResult.snapshotLength; i++) {
            nodes.push(xpathResult.snapshotItem(i).textContent.trim());
        }

        return nodes.length > 0 ? nodes : ["No matching node found."];
    } catch (error) {
        return ["Error evaluating XPath: " + error.message];
    }
}

// Export to Excel functionality
document.getElementById("exportExcelButton").addEventListener("click", () => {
    const outputText = document.getElementById("outputText").value.trim();

    if (outputText) {
        let data;

        try {
            data = JSON.parse(outputText);
        } catch (jsonError) {
            alert("Error: Invalid output format.");
            return;
        }

        // Prepare data for Excel as an array of rows
        const headers = Object.keys(data);
        const rows = [headers];

        const row = headers.map((key) => {
            const value = data[key];
            return Array.isArray(value) ? value.join(", ") : value;
        });

        rows.push(row);

        // Create worksheet and workbook
        const ws = XLSX.utils.aoa_to_sheet(rows);
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, "Extracted Data");

        // Download the Excel file
        XLSX.writeFile(wb, "extracted_data.xlsx");
    } else {
        alert("No data to export.");
    }
});
