chrome.devtools.network.onRequestFinished.addListener((request) => {
  chrome.storage.local.get({ networkRequests: [] }, (data) => {
    const requests = data.networkRequests;
    requests.push(request.request.url);
    chrome.storage.local.set({ networkRequests: requests });
  });
});
