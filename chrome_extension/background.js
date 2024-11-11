// In background.js or popup.js (depending on where you want the action to happen)
chrome.action.onClicked.addListener(function(tab) {
    chrome.windows.create({
        url: "popup.html", // URL for your extension's page
        type: "popup", // Create a popup type window
        width: 600,
        height: 400
    });
});
