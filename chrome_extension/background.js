// In background.js or popup.js (depending on where you want the action to happen)
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'fetchData') {
        fetch(request.url, { method: request.method })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`Network response was not ok: ${response.statusText}`);
                }
                return response.text(); // Or response.json() if expecting JSON
            })
            .then(data => {
                sendResponse({ data: data });
            })
            .catch(error => {
                sendResponse({ error: error.message });
            });

        // Keep the message channel open for asynchronous response
        return true;
    }
});


chrome.action.onClicked.addListener(function(tab) {
    chrome.windows.create({
        url: "popup.html", // URL for your extension's page
        type: "popup", // Create a popup type window
        width: 600,
        height: 400
    });
});