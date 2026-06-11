const API_BASE = '/api/v1';

const statusMeta = {
    green: { label: 'سبز', color: '#24a768' },
    blue: { label: 'آبی', color: '#3478f6' },
    red: { label: 'قرمز', color: '#e65050' }
};

const map = L.map('map', {
    center: [35.6892, 51.3890],
    zoom: 11,
    preferCanvas: true,
    zoomControl: true
});

let tempMarker = null;
let selectedLocation = null;
let allMarkers = {};
let tileErrorNotified = false;

const marketForm = document.getElementById('marketForm');
const deleteForm = document.getElementById('deleteForm');
const submitButton = document.getElementById('submitButton');
const locationCard = document.getElementById('locationCard');
const locationStatus = document.getElementById('locationStatus');
const locationCoords = document.getElementById('locationCoords');
const clearLocationButton = document.getElementById('clearLocation');
const locateButton = document.getElementById('locateButton');

const tileProviders = {
    osm: {
        url: `${API_BASE}/map/tiles/osm/{z}/{x}/{y}.png`,
        options: {
            maxZoom: 19,
            attribution: '&copy; OpenStreetMap contributors',
            tileSize: 256,
            errorTileUrl: ''
        }
    }
};

const tileLayers = {};

function normalizeStatus(status) {
    // Keep old "yellow" records visible as blue after the grade palette change.
    if (status === 'yellow') return 'blue';
    return statusMeta[status] ? status : 'green';
}

function toPersianNumber(value) {
    return new Intl.NumberFormat('fa-IR').format(value);
}

function escapeHtml(value) {
    const element = document.createElement('span');
    element.textContent = value;
    return element.innerHTML;
}

function showNotification(message, type = 'success') {
    const area = document.getElementById('notification-area');
    if (!area) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    area.appendChild(toast);

    window.setTimeout(() => {
        toast.classList.add('is-leaving');
        window.setTimeout(() => toast.remove(), 260);
    }, 3200);
}

function buildTileLayer(providerName) {
    const provider = tileProviders[providerName];
    const layer = L.tileLayer(provider.url, provider.options);

    layer.on('tileerror', () => {
        if (!tileErrorNotified) {
            tileErrorNotified = true;
            showNotification('دریافت نقشه با مشکل روبه‌رو شد. اتصال سرور را بررسی کنید.', 'error');
        }
    });

    return layer;
}

function switchTileProvider(providerName) {
    if (!tileProviders[providerName]) return;

    Object.values(tileLayers).forEach((layer) => {
        if (map.hasLayer(layer)) map.removeLayer(layer);
    });

    if (!tileLayers[providerName]) {
        tileLayers[providerName] = buildTileLayer(providerName);
    }

    tileLayers[providerName].addTo(map);
}

function getSelectedStatus() {
    const selected = document.querySelector('input[name="marketStatus"]:checked');
    return normalizeStatus(selected?.value || 'green');
}

function createMarkerIcon(status, isDraft = false) {
    const normalizedStatus = normalizeStatus(status);
    const draftClass = isDraft ? ' market-pin--draft' : '';

    return L.divIcon({
        className: 'market-pin-wrapper',
        html: `<span class="market-pin market-pin--${normalizedStatus}${draftClass}"></span>`,
        iconSize: [30, 36],
        iconAnchor: [15, 32],
        popupAnchor: [0, -29]
    });
}

function createMarketMarker(lat, lng, status, isDraft = false) {
    return L.marker([lat, lng], {
        icon: createMarkerIcon(status, isDraft),
        keyboard: !isDraft,
        zIndexOffset: isDraft ? 1000 : 0
    });
}

function clearSelectedLocation() {
    selectedLocation = null;
    if (tempMarker) {
        map.removeLayer(tempMarker);
        tempMarker = null;
    }

    locationCard.classList.remove('is-selected');
    locationStatus.textContent = 'هنوز نقطه‌ای انتخاب نشده';
    locationCoords.textContent = 'مختصات پس از انتخاب نمایش داده می‌شود';
    clearLocationButton.hidden = true;
    submitButton.disabled = true;
}

function setSelectedLocation(lat, lng, shouldPan = false) {
    selectedLocation = { lat, lng };

    if (tempMarker) map.removeLayer(tempMarker);
    tempMarker = createMarketMarker(lat, lng, getSelectedStatus(), true).addTo(map);

    locationCard.classList.add('is-selected');
    locationStatus.textContent = 'موقعیت با موفقیت انتخاب شد';
    locationCoords.textContent = `${lat.toFixed(6)}, ${lng.toFixed(6)}`;
    clearLocationButton.hidden = false;
    submitButton.disabled = false;

    if (shouldPan) {
        map.setView([lat, lng], Math.max(map.getZoom(), 16), { animate: true });
    }
}

function updateCounts(markets) {
    const counts = { green: 0, blue: 0, red: 0 };

    markets.forEach((market) => {
        counts[normalizeStatus(market.status)] += 1;
    });

    document.getElementById('marketCount').textContent = toPersianNumber(markets.length);
    document.getElementById('greenCount').textContent = toPersianNumber(counts.green);
    document.getElementById('blueCount').textContent = toPersianNumber(counts.blue);
    document.getElementById('redCount').textContent = toPersianNumber(counts.red);
}

function buildPopup(market) {
    const status = normalizeStatus(market.status);
    const meta = statusMeta[status];

    return `
        <div class="market-popup">
            <strong>${escapeHtml(market.name)}</strong>
            <span><i style="background:${meta.color}"></i> گرید ${meta.label}</span>
        </div>
    `;
}

map.on('click', (event) => {
    setSelectedLocation(event.latlng.lat, event.latlng.lng);
});

document.querySelectorAll('input[name="marketStatus"]').forEach((input) => {
    input.addEventListener('change', () => {
        if (tempMarker && selectedLocation) {
            tempMarker.setIcon(createMarkerIcon(getSelectedStatus(), true));
        }
    });
});

clearLocationButton.addEventListener('click', clearSelectedLocation);

locateButton.addEventListener('click', () => {
    locateButton.disabled = true;
    locateButton.querySelector('span').textContent = 'در حال یافتن...';
    map.locate({ enableHighAccuracy: true, timeout: 10000, maximumAge: 30000 });
});

map.on('locationfound', (event) => {
    locateButton.disabled = false;
    locateButton.querySelector('span').textContent = 'موقعیت من';
    setSelectedLocation(event.latlng.lat, event.latlng.lng, true);
    showNotification('موقعیت فعلی شما انتخاب شد.');
});

map.on('locationerror', () => {
    locateButton.disabled = false;
    locateButton.querySelector('span').textContent = 'موقعیت من';
    showNotification('دسترسی به موقعیت ممکن نشد. روی نقشه کلیک کنید.', 'error');
});

async function fetchJson(url, options = {}) {
    const response = await fetch(url, {
        ...options,
        headers: {
            'Content-Type': 'application/json',
            ...(options.headers || {})
        }
    });

    if (!response.ok) {
        const body = await response.text();
        throw new Error(`${options.method || 'GET'} ${url} failed: ${response.status} ${body}`);
    }

    if (response.status === 204) return null;
    return response.json();
}

async function loadMarkets() {
    Object.values(allMarkers).forEach((marker) => map.removeLayer(marker));
    allMarkers = {};

    try {
        const markets = await fetchJson(`${API_BASE}/markets`);
        updateCounts(markets);

        markets.forEach((market) => {
            const marker = createMarketMarker(
                market.lat,
                market.lng,
                market.status
            ).addTo(map);

            marker.bindPopup(buildPopup(market));
            allMarkers[market.id] = marker;
        });
    } catch (error) {
        console.error('Error loading markets:', error);
        updateCounts([]);
        showNotification('دریافت فهرست سوپرمارکت‌ها انجام نشد.', 'error');
    }
}

marketForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    if (!selectedLocation) {
        showNotification('ابتدا موقعیت سوپرمارکت را روی نقشه انتخاب کنید.', 'error');
        return;
    }

    const data = {
        name: document.getElementById('marketName').value.trim(),
        status: getSelectedStatus(),
        lat: selectedLocation.lat,
        lng: selectedLocation.lng
    };

    if (!data.name) {
        showNotification('نام سوپرمارکت را وارد کنید.', 'error');
        return;
    }

    submitButton.disabled = true;
    submitButton.classList.add('is-loading');
    submitButton.querySelector('span').textContent = 'در حال ثبت...';

    try {
        await fetchJson(`${API_BASE}/markets`, {
            method: 'POST',
            body: JSON.stringify(data)
        });

        showNotification('سوپرمارکت با موفقیت روی نقشه ثبت شد.');
        marketForm.reset();
        clearSelectedLocation();
        await loadMarkets();
    } catch (error) {
        console.error('Error creating market:', error);
        submitButton.disabled = false;
        showNotification('ثبت سوپرمارکت انجام نشد.', 'error');
    } finally {
        submitButton.classList.remove('is-loading');
        submitButton.querySelector('span').textContent = 'ثبت سوپرمارکت روی نقشه';
    }
});

deleteForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const nameInput = document.getElementById('deleteMarketName');
    const name = nameInput.value.trim();
    if (!name) return;

    if (!window.confirm(`سوپرمارکت «${name}» حذف شود؟`)) return;

    const deleteButton = deleteForm.querySelector('button');
    deleteButton.disabled = true;

    try {
        await fetchJson(`${API_BASE}/markets/${encodeURIComponent(name)}`, {
            method: 'DELETE'
        });

        showNotification('سوپرمارکت با موفقیت حذف شد.');
        deleteForm.reset();
        await loadMarkets();
    } catch (error) {
        console.error('Error deleting market:', error);
        showNotification('حذف انجام نشد؛ نام فروشگاه را بررسی کنید.', 'error');
    } finally {
        deleteButton.disabled = false;
    }
});

switchTileProvider('osm');
loadMarkets();
