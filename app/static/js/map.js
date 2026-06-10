const API_BASE = '/api/v1';

const map = L.map('map', {
    center: [35.6892, 51.3890],
    zoom: 11,
    preferCanvas: true
});

let tempMarker = null;
let allMarkers = {};
let activeTileProvider = 'mapir';
let fallbackActivated = false;

const tileProviders = {
    mapir: {
        url: `${API_BASE}/map/tiles/mapir/{z}/{x}/{y}.png`,
        options: {
            maxZoom: 19,
            attribution: '© map.ir',
            tileSize: 256,
            errorTileUrl: ''
        }
    },
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

function showNotification(message, type = 'success') {
    const area = document.getElementById('notification-area');
    if (!area) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerText = message;
    area.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => {
            if (toast.parentNode === area) {
                area.removeChild(toast);
            }
        }, 500);
    }, 3500);
}

function buildTileLayer(providerName) {
    const provider = tileProviders[providerName];
    const layer = L.tileLayer(provider.url, provider.options);

    layer.on('tileerror', () => {
        if (providerName === 'mapir' && !fallbackActivated) {
            fallbackActivated = true;
            showNotification(
                'اتصال به نقشه map.ir برقرار نشد؛ در حال تلاش با لایه جایگزین...',
                'error'
            );
            switchTileProvider('osm');
            return;
        }

        if (providerName === 'osm') {
            showNotification(
                'کاشی‌های نقشه از شبکه فعلی دریافت نمی‌شوند. اتصال backend به provider را بررسی کنید.',
                'error'
            );
        }
    });

    return layer;
}

function switchTileProvider(providerName) {
    if (!tileProviders[providerName]) return;

    Object.values(tileLayers).forEach((layer) => {
        if (map.hasLayer(layer)) {
            map.removeLayer(layer);
        }
    });

    if (!tileLayers[providerName]) {
        tileLayers[providerName] = buildTileLayer(providerName);
    }

    activeTileProvider = providerName;
    tileLayers[providerName].addTo(map);
}

const colorMap = {
    green: 'green',
    yellow: 'gold',
    red: 'red'
};

function getMarkerColor(status) {
    return colorMap[status] || 'gray';
}

function createMarketMarker(lat, lng, status) {
    return L.circleMarker([lat, lng], {
        radius: 8,
        fillColor: getMarkerColor(status),
        color: '#000',
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8
    });
}

map.on('click', (event) => {
    document.getElementById('marketLat').value = event.latlng.lat.toFixed(7);
    document.getElementById('marketLng').value = event.latlng.lng.toFixed(7);

    if (tempMarker) {
        map.removeLayer(tempMarker);
    }

    const status = document.getElementById('marketStatus').value || 'green';
    tempMarker = createMarketMarker(
        event.latlng.lat,
        event.latlng.lng,
        status
    ).addTo(map);
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

    if (response.status === 204) {
        return null;
    }

    return response.json();
}

async function loadMarkets() {
    Object.values(allMarkers).forEach((marker) => map.removeLayer(marker));
    allMarkers = {};

    try {
        const markets = await fetchJson(`${API_BASE}/markets`);

        markets.forEach((market) => {
            const marker = createMarketMarker(
                market.lat,
                market.lng,
                market.status
            ).addTo(map);

            marker.bindPopup(`<b>${market.name}</b><br>گرید: ${market.status}`);
            allMarkers[market.id] = marker;
        });
    } catch (error) {
        console.error('Error loading markets:', error);
        showNotification('خطا در دریافت سوپرمارکت‌ها از سرور', 'error');
    }
}

document.getElementById('marketForm').addEventListener('submit', async (event) => {
    event.preventDefault();

    const lat = Number.parseFloat(document.getElementById('marketLat').value);
    const lng = Number.parseFloat(document.getElementById('marketLng').value);

    if (Number.isNaN(lat) || Number.isNaN(lng)) {
        showNotification('اول یک نقطه از نقشه انتخاب کنید', 'error');
        return;
    }

    const data = {
        name: document.getElementById('marketName').value.trim(),
        status: document.getElementById('marketStatus').value,
        lat,
        lng
    };

    try {
        await fetchJson(`${API_BASE}/markets`, {
            method: 'POST',
            body: JSON.stringify(data)
        });

        showNotification('ثبت با موفقیت انجام شد', 'success');
        if (tempMarker) map.removeLayer(tempMarker);
        tempMarker = null;
        document.getElementById('marketForm').reset();
        await loadMarkets();
    } catch (error) {
        console.error('Error creating market:', error);
        showNotification('خطا در ثبت سوپرمارکت', 'error');
    }
});

document.getElementById('deleteForm').addEventListener('submit', async (event) => {
    event.preventDefault();

    const name = document.getElementById('deleteMarketName').value.trim();
    if (!name) return;

    try {
        await fetchJson(`${API_BASE}/markets/${encodeURIComponent(name)}`, {
            method: 'DELETE'
        });

        showNotification('حذف با موفقیت انجام شد', 'success');
        document.getElementById('deleteForm').reset();
        await loadMarkets();
    } catch (error) {
        console.error('Error deleting market:', error);
        showNotification('حذف انجام نشد؛ نام را دقیق بررسی کنید', 'error');
    }
});

switchTileProvider(activeTileProvider);
loadMarkets();
