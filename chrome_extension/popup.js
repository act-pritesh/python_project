document.getElementById("submitButton").addEventListener("click", () => {
    const xpathInput = document.getElementById("inputText").value.trim();
    // Check if the XPath input is provided
    if (xpathInput !== "") {
        // Fix input to ensure XPath expressions are treated as strings by adding quotes around the XPath
        const fixedInput = fixInput(xpathInput);
        // Parse the input into a JavaScript object
        try {
            const parsedInput = JSON.parse(fixedInput);
            // Validate if it's an object and has key-value pairs
            if (typeof parsedInput === 'object' && !Array.isArray(parsedInput)) {
                // Query the active tab
                chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
                    if (tabs.length > 0) {
                        const tabId = tabs[0].id;

                        // Execute script for each XPath and collect results
                        const results = {};
                        for (const [key, xpath] of Object.entries(parsedInput)) {
                            chrome.scripting.executeScript({
                                target: { tabId: tabId },
                                func: extractDataFromXPath,
                                args: [xpath]
                            }, (result) => {
                                if (result && result[0]) {
                                    // Store the result of the XPath in the results object
                                    results[key] = result[0].result || "No matching node found.";
                                }

                                // Check if all results are collected and update output
                                if (Object.keys(results).length === Object.keys(parsedInput).length) {
                                    document.getElementById("outputText").value = JSON.stringify(results, null, 2);
                                }
                            });
                        }
                    }
                });
            } else {
                alert("Invalid input format. Please use {key: xpath, ...}");
            }
        } catch (e) {
            alert("Invalid input format. Please use {key: xpath, ...}");
        }
    } else {
        alert("Please enter a valid XPath expression.");
    }
});

// Function to fix the input by adding quotes around XPath expressions
function fixInput(input) {
    return input.replace(/(\w+):\/\/([^"]+)/g, '"$1":"//$2"');
}

// Function to extract data from XPath
function extractDataFromXPath(xpath) {
    try {
        const xpathResult = document.evaluate(xpath, document, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);
        // If multiple nodes are found, collect all of their text content into an array
        const nodes = [];
        for (let i = 0; i < xpathResult.snapshotLength; i++) {
            nodes.push(xpathResult.snapshotItem(i).textContent.trim());
        }
        // Return the list of nodes or a message if no nodes found
        if (nodes.length > 0) {
            return nodes; // Return an array of text content from the matched nodes
        } else {
            return ["No matching node found."]; // If no node is found
        }
    } catch (error) {
        return ["Error evaluating XPath: " + error.message]; // If error occurs while evaluating XPath
    }
}

document.getElementById("exportExcelButton").addEventListener("click", () => {
    const outputText = document.getElementById("outputText").value.trim();

    // Check if there is data in the outputText box
    if (outputText) {
        let data;

        try {
            // Parse the data as JSON or object format
            data = JSON.parse(outputText);
        } catch (jsonError) {
            try {
                data = new Function("return " + outputText)();
            } catch (dictError) {
                alert("Error: Input format is invalid. Please ensure it's a valid JSON or dictionary format.");
                return;
            }
        }

        // Validate that parsed data is an object with key-value pairs
        if (typeof data !== 'object' || Array.isArray(data) || data === null) {
            alert("Error: Data must be a dictionary-like object with key-value pairs.");
            return;
        }

        // Prepare data for Excel as an array of rows
        // First create headers (keys of the object)
        const headers = Object.keys(data);

        // Create rows based on values, ensure that array values are joined into a single string
        const rows = [headers];  // Initialize with headers as the first row

        // Add values for each key (in the order of headers)
        const row = headers.map((key) => {
            const value = data[key];
            return Array.isArray(value) ? value.join(", ") : value;
        });

        rows.push(row);  // Add the row of values below the headers

        // Create worksheet and workbook
        const ws = XLSX.utils.aoa_to_sheet(rows);  // Convert array of arrays (rows) to worksheet
        const wb = XLSX.utils.book_new();  // Create a new workbook
        XLSX.utils.book_append_sheet(wb, ws, "Extracted Data");  // Append the sheet to the workbook

        // Download the Excel file
        XLSX.writeFile(wb, "extracted_data.xlsx");
    } else {
        alert("No data to export.");
    }
});
