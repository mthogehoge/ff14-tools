let itemData = null;
let marketPrices = {};

const MARKET_PRICES_JSON_URL = '/static/market_prices.json';

function getPrice(itemId) {
    try {
        if (!marketPrices || !marketPrices[itemId]) return 0;
        const entry = marketPrices[itemId];
        let p = entry.price;
        if (p === undefined || p === null) return 0;

        // Handle number directly
        if (typeof p === 'number') return p;

        // Handle string with commas
        if (typeof p === 'string') {
            const parsed = parseInt(p.replace(/,/g, ''));
            return isNaN(parsed) ? 0 : parsed;
        }

        // Fallback for objects or other types
        const stringVal = String(p).replace(/,/g, '');
        const finalParsed = parseInt(stringVal);
        return isNaN(finalParsed) ? 0 : finalParsed;
    } catch (e) {
        console.warn(`Error getting price for item ${itemId}:`, e);
        return 0;
    }
}

function flattenPrices(rawPrices) {
    const flattened = { ...rawPrices };

    Object.keys(rawPrices).forEach(id => {
        const item = rawPrices[id];
        if (item.mats) {
            Object.keys(item.mats).forEach(matId => {
                if (!flattened[matId]) {
                    flattened[matId] = {
                        price: item.mats[matId].price,
                        server: item.server,
                        isFlattened: true
                    };
                }
            });
        }
    });

    return flattened;
}

function calculateMaterials(itemId, amount, intermediateTotals, rawTotals, isRoot = false) {
    const sId = String(itemId);
    const recipe = itemData.recipes.find(r => String(r.result) === sId);

    if (!recipe) {
        // Base material (no recipe)
        rawTotals[sId] = (rawTotals[sId] || 0) + amount;
        return;
    }

    // Intermediate material (has recipe)
    if (!isRoot) {
        intermediateTotals[sId] = (intermediateTotals[sId] || 0) + amount;
    }

    recipe.ingredients.forEach(ing => {
        calculateMaterials(ing.id, ing.amount * amount, intermediateTotals, rawTotals);
    });
}

function updateResults() {
    const classId = document.getElementById('classSelect').value;
    const isModified = document.getElementById('modifiedToggle').checked;

    const parts = [
        { id: 'hullCheck', key: 'hull' },
        { id: 'sternCheck', key: 'stern' },
        { id: 'bowCheck', key: 'bow' },
        { id: 'bridgeCheck', key: 'bridge' }
    ];

    const intermediateTotals = {};
    const rawTotals = {};

    parts.forEach(part => {
        if (document.getElementById(part.id).checked) {
            const partData = itemData.submarine_parts[classId][part.key];
            const resultId = isModified ? partData.modified : partData.normal;
            calculateMaterials(resultId, 1, intermediateTotals, rawTotals, true);
        }
    });

    renderTable('intermediateTable', intermediateTotals);
    renderTable('rawTable', rawTotals);

    updateTotal('intermediateTotal', intermediateTotals);
    updateTotal('rawTotal', rawTotals);
}

function renderTable(tableId, data) {
    const tbody = document.querySelector(`#${tableId} tbody`);
    tbody.innerHTML = '';

    const sortedItems = Object.keys(data).sort((a, b) => {
        const priceA = getPrice(a) * data[a];
        const priceB = getPrice(b) * data[b];
        return priceB - priceA || data[b] - data[a];
    });

    sortedItems.forEach(id => {
        const amount = data[id];
        const price = getPrice(id);
        const total = price * amount;

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${itemData.items[id] || 'Unknown Item (' + id + ')'}</td>
            <td style="text-align: right; font-weight: 600;">${amount.toLocaleString()}</td>
            <td style="text-align: right;" class="price-cell">${price > 0 ? price.toLocaleString() : '-'}</td>
            <td style="text-align: right;" class="total-cell">${total > 0 ? total.toLocaleString() : '-'}</td>
        `;
        tbody.appendChild(row);
    });
}

function updateTotal(elementId, data) {
    let grandTotal = 0;
    Object.keys(data).forEach(id => {
        grandTotal += getPrice(id) * data[id];
    });
    document.getElementById(elementId).textContent = grandTotal > 0 ? `${grandTotal.toLocaleString()} gil` : '0 gil';
}

function renderClassSelector() {
    const select = document.getElementById('classSelect');
    select.innerHTML = '';

    const classes = Object.keys(itemData.submarine_parts);
    classes.forEach(cls => {
        const option = document.createElement('option');
        option.value = cls;
        option.textContent = cls.charAt(0).toUpperCase() + cls.slice(1) + '級';
        select.appendChild(option);
    });
}

async function init() {
    try {
        if (typeof MARKET_PRICES !== 'undefined') {
            marketPrices = flattenPrices(MARKET_PRICES);
            console.log("Loaded and flattened market prices from prices.js");
        } else {
            try {
                const priceResponse = await fetch(MARKET_PRICES_JSON_URL);
                if (priceResponse.ok) {
                    const rawPrices = await priceResponse.json();
                    marketPrices = flattenPrices(rawPrices);
                    console.log("Loaded and flattened market prices via fetch.");
                }
            } catch (e) {
                console.warn("Could not load market prices via fetch:", e);
            }
        }

        itemData = SUBMARINE_DATA;
        renderClassSelector();

        // Listeners
        document.getElementById('classSelect').addEventListener('change', updateResults);
        document.getElementById('modifiedToggle').addEventListener('change', updateResults);
        ['hullCheck', 'sternCheck', 'bowCheck', 'bridgeCheck'].forEach(id => {
            document.getElementById(id).addEventListener('change', updateResults);
        });

        document.getElementById('copyRawBtn').addEventListener('click', copyRawToClipboard);

        document.getElementById('loading').style.display = 'none';
        updateResults();

    } catch (error) {
        console.error('Failed to load data:', error);
        document.getElementById('loading').innerHTML = '<p style="color: #ef4444;">データの読み込みに失敗しました。</p>';
    }
}

function copyRawToClipboard() {
    const rows = Array.from(document.querySelectorAll('#rawTable tbody tr'));
    const text = rows.map(r => {
        const cells = r.querySelectorAll('td');
        return `${cells[0].textContent}: ${cells[1].textContent}`;
    }).join('\n');

    navigator.clipboard.writeText(text).then(() => {
        const btn = document.getElementById('copyRawBtn');
        const originalText = btn.textContent;
        btn.textContent = 'コピーしました！';
        setTimeout(() => btn.textContent = originalText, 2000);
    });
}

init();
