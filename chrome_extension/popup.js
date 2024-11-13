// Initialize an empty object to store network requests
let networkRequests = {};

// Listen for network requests and capture them
document.getElementById("captureNetworkButton").addEventListener("click", () => {
    chrome.webRequest.onCompleted.addListener((details) => {
        let url = details.url;
        let method = details.method;
        let filename = new URL(url).pathname.split('/').pop();

        if (!networkRequests[filename]) {
            networkRequests[filename] = {
                url: url,
                method: method,
            };
        }

        document.getElementById("networkFiles").value += `Key: ${filename}\nURL: ${url}\nMethod: ${method}\n\n`;

    }, { urls: ["<all_urls>"] });
});
// Fetch and display the response for a given key, passing the same body in the POST request
document.getElementById("fetchButton").addEventListener("click", () => {
    let key = document.getElementById("fileinput").value.trim();

    if (networkRequests[key]) {
        let request = networkRequests[key];

        // Prepare fetch options for POST request, sending the captured body
        const fetchOptions = {
            method: 'POST',  // We're using POST because it's a POST request
            headers: {
                'Content-Type': 'application/json', // The body is in JSON format, so Content-Type is set to 'application/json'
            },
            body: request.body, // Send the captured body (payload) from the original request
        };

        // Send the POST request to the URL
        fetch(request.url, fetchOptions)
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Network response was not ok: ${response.statusText}`);
                }

                // Check the content type of the response
                const contentType = response.headers.get('Content-Type');

                if (contentType.includes('application/json')) {
                    return response.json(); // Parse the JSON response
                } else if (contentType.includes('text/html')) {
                    return response.text(); // Parse the HTML response
                } else {
                    throw new Error('Unsupported content type');
                }
            })
            .then(data => {
                if (!request.responses) {
                    request.responses = [];
                }

                // If the response is JSON, display it prettily
                if (typeof data === 'object') {
                    request.responses.push(data);
                    // Show the JSON response in a formatted way
                    document.getElementById("htmlResponse").value = JSON.stringify(data, null, 2);
                } else if (typeof data === 'string') {
                    // If the response is HTML, display the raw HTML
                    request.responses.push(data);
                    document.getElementById("htmlResponse").value = data;
                }
            })
            .catch(error => {
                console.error('Error fetching response:', error);
                document.getElementById("htmlResponse").value = `Failed to fetch response: ${error.message}`;
            });
    } else {
        document.getElementById("htmlResponse").value = `No request found for key: ${key}`;
    }
});

// Export to Excel functionality
document.getElementById("exportExcelButton").addEventListener("click", () => {
    const outputText = document.getElementById("xpathResult").value.trim();

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

        // Iterate over each key in data and prepare the row values
        const row = headers.map((key) => {
            const value = data[key];
            // Check if the value is an array
            if (Array.isArray(value)) {
                return value.join(", "); // Join array elements with a comma
            }
            return value;
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

// Extract and format XPath results using a dynamic key from the input JSON
document.getElementById("submitXPathButton").addEventListener("click", () => {
    let responseText = document.getElementById("htmlResponse").value;
    let xpathInput = document.getElementById("inputText").value.trim();
    let outputArea = document.getElementById("xpathResult");

    let key, xpathExpression;

    try {
        // Attempt to parse the input JSON
        let parsedInput = JSON.parse(xpathInput);

        // Extract the key and XPath expression dynamically
        key = Object.keys(parsedInput)[0];  // Get the first key, which will be dynamic
        xpathExpression = parsedInput[key]; // Use the value of that key as the XPath expression
    } catch (error) {
        // If the input is not valid JSON, treat it as raw XPath and default the key to "key"
        xpathExpression = xpathInput;
        key = "key";
    }

    try {
        // Parse the response HTML
        let parser = new DOMParser();
        let doc = parser.parseFromString(responseText, "text/html");
        let xpathResult = doc.evaluate(xpathExpression, doc, null, XPathResult.ORDERED_NODE_SNAPSHOT_TYPE, null);

        let result = {};
        let values = [];

        // Collect matching node values
        for (let i = 0; i < xpathResult.snapshotLength; i++) {
            let nodeText = xpathResult.snapshotItem(i).textContent.trim();
            values.push(nodeText); // Store values in the array
        }

        // If any values are found, store them under the dynamic key
        if (values.length > 0) {
            result[key] = values; // Use the dynamic key extracted from the input JSON
        } else {
            result[key] = ["No matching nodes found"]; // Add a placeholder message if no results
        }

        // Display the result as a JSON object in the output area
        outputArea.value = JSON.stringify(result, null, 2); // Pretty-print the result
    } catch (error) {
        console.error("Error executing XPath:", error);
        outputArea.value = `Error executing XPath: ${error.message}`; // Display any errors
    }
});

