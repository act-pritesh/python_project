
// Optional: Open the popup when the extension icon is clicked
chrome.action.onClicked.addListener(function(tab) {
    chrome.windows.create({
        url: "popup.html", // URL for your extension's popup page
        type: "popup", // Create a popup window
        width: 600,
        height: 400
    });
});
