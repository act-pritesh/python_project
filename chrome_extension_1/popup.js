document.addEventListener("DOMContentLoaded", () => {
    let networkRequests = {};

    // Button click listener to start capturing network requests
    document.getElementById("captureNetworkButton").addEventListener("click", () => {

        // Listen for the request before it is sent
        chrome.webRequest.onBeforeRequest.addListener((details) => {
            let url = details.url;
            let method = details.method;
            let filename = new URL(url).pathname.split('/').pop();

            // Store request details in the networkRequests object
            if (!networkRequests[filename]) {
                networkRequests[filename] = {
                    url: url,
                    method: method,
                    requestBody: null,
                    responseBody: null,
                    responseHeaders: null,
                    statusCode: null
                };

                // If it's a POST request, capture the body
                if (method === "POST" && details.requestBody && details.requestBody.raw) {
                    let rawBody = new TextDecoder("utf-8").decode(details.requestBody.raw[0].bytes);
                    networkRequests[filename].requestBody = rawBody;
                }
            }
        }, { urls: ["<all_urls>"] }, ['requestBody']);

        // Listen for response headers when received
        chrome.webRequest.onHeadersReceived.addListener((details) => {
            let filename = new URL(details.url).pathname.split('/').pop();
            if (networkRequests[filename]) {
                networkRequests[filename].responseHeaders = details.responseHeaders;
            }
        }, { urls: ["<all_urls>"] }, ["responseHeaders"]);

        // Listen for when a request completes, then fetch the body if necessary
        chrome.webRequest.onCompleted.addListener((details) => {
            let filename = new URL(details.url).pathname.split('/').pop();
            if (networkRequests[filename]) {
                networkRequests[filename].statusCode = details.statusCode;

                // Fetch the response body based on the URL
                fetch(networkRequests[filename].url)
                    .then(response => {
                        if (response.ok) {
                            const contentType = response.headers.get('Content-Type');
                            return contentType.includes('application/json') ? response.json() : response.text();
                        }
                        return null;
                    })
                    .then(responseBody => {
                        if (responseBody) {
                            networkRequests[filename].responseBody = responseBody;
                        }
                    })
                    .catch(err => console.error('Error fetching response body:', err));
            }
        }, { urls: ["<all_urls>"] });
    });

    // New input field listener to capture the key entered by the user
    document.getElementById("keyInput").addEventListener("input", () => {
        let inputKey = document.getElementById("keyInput").value.trim();

        // Clear the network files and output box before displaying new results
        document.getElementById("networkFiles").textContent = '';
        document.getElementById("outputBox").textContent = '';

        if (inputKey && networkRequests[inputKey]) {
            // If the entered key matches a network request, display its details in both boxes
            let networkDetails = networkRequests[inputKey];

            document.getElementById("networkFiles").textContent =
                `\n\nkey: ${inputKey} ---\n` +
                `Method: ${networkDetails.method}\n` +
                `URL: ${networkDetails.url}\n` +
                `Status Code: ${networkDetails.statusCode}\n` +
                `Response: ${typeof networkDetails.responseBody === 'object' ? JSON.stringify(networkDetails.responseBody, null, 2) : networkDetails.responseBody}`;

            document.getElementById("outputBox").textContent =
                `Method: ${networkDetails.method}\n` +
                `URL: ${networkDetails.url}\n` +
                `Status Code: ${networkDetails.statusCode}\n` +
                `Response: ${typeof networkDetails.responseBody === 'object' ? JSON.stringify(networkDetails.responseBody, null, 2) : networkDetails.responseBody}`;
        } else {
            // If no matching key, show an appropriate message
            document.getElementById("networkFiles").textContent = 'No matching key found.';
            document.getElementById("outputBox").textContent = 'No matching key found.';
        }
    });
});
