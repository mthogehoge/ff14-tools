const LEVEQUEST_JSON_URL = 'levequests.json';
const MARKET_PRICES_JSON_URL = 'market_prices.json';

// DOM elements
const expansionTabs = document.getElementById('expansion-tabs');
const jobTabs = document.getElementById('job-tabs');
const itemsGrid = document.getElementById('items-grid');

let levequestData = {};
let marketPriceData = {};
let currentExpansion = '';
let currentJob = '';

async function init() {
    try {
        const response = await fetch(LEVEQUEST_JSON_URL);
        levequestData = await response.json();

        // Attempt to load market prices (may not exist immediately if background pull is still running)
        try {
            const priceResponse = await fetch(MARKET_PRICES_JSON_URL);
            if (priceResponse.ok) {
                marketPriceData = await priceResponse.json();
                console.log("Loaded market prices data.");
            }
        } catch (e) {
            console.log("Market prices not available yet.");
        }

        setupExpansionTabs();

        // Select first expansion and job by default
        const expansions = Object.keys(levequestData);
        if (expansions.length > 0) {
            selectExpansion(expansions[0]);
        }

    } catch (error) {
        console.error("Failed to load levequest data:", error);
        itemsGrid.innerHTML = '<div class="error-msg">Failed to load data. Please ensure levequests.json exists.</div>';
    }
}

function setupExpansionTabs() {
    expansionTabs.innerHTML = '';
    const expansions = Object.keys(levequestData);

    expansions.forEach(exp => {
        const btn = document.createElement('button');
        btn.className = 'tab-btn expansion-tab';
        // Extract just the Japanese part in () if it exists
        const match = exp.match(/\((.*?)\)/);
        btn.textContent = match ? match[1] : exp;
        btn.onclick = () => selectExpansion(exp);
        expansionTabs.appendChild(btn);
    });
}

function selectExpansion(expansion) {
    currentExpansion = expansion;

    // Update active state
    document.querySelectorAll('.expansion-tab').forEach(btn => {
        const match = expansion.match(/\((.*?)\)/);
        const name = match ? match[1] : expansion;
        if (btn.textContent === name) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    setupJobTabs();
}

function setupJobTabs() {
    jobTabs.innerHTML = '';

    if (!levequestData[currentExpansion]) return;

    const jobs = Object.keys(levequestData[currentExpansion]);

    jobs.forEach(job => {
        const btn = document.createElement('button');
        btn.className = 'tab-btn job-tab';
        btn.textContent = job;
        btn.onclick = () => selectJob(job);
        jobTabs.appendChild(btn);
    });

    // Select first job
    if (jobs.length > 0) {
        selectJob(jobs[0]);
    }
}

function selectJob(job) {
    currentJob = job;

    // Update active state
    document.querySelectorAll('.job-tab').forEach(btn => {
        if (btn.textContent === job) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });

    renderItems();
}

function renderItems() {
    itemsGrid.innerHTML = '';

    if (!levequestData[currentExpansion] || !levequestData[currentExpansion][currentJob]) {
        return;
    }

    const items = levequestData[currentExpansion][currentJob];

    if (items.length === 0) {
        itemsGrid.innerHTML = '<div class="no-data">この拡張・クラスのリーヴデータはありません。</div>';
        return;
    }

    items.forEach(item => {
        const card = document.createElement('div');
        card.className = 'item-card';

        let priceHtml = '';
        let matsHtml = '';

        if (marketPriceData && marketPriceData[item.item_id]) {
            const data = marketPriceData[item.item_id];

            // Check if parsing new complex format
            if (typeof data === 'object' && data !== null && 'price' in data) {
                const priceVal = data.price || 0;
                const serverName = data.server || 'Japan';

                if (priceVal > 0) {
                    priceHtml = `<div class="item-price">最安値(HQ): <strong>${priceVal.toLocaleString()}</strong> gil <span class="server-badge">${serverName}</span></div>`;
                } else {
                    priceHtml = `<div class="item-price none">出品なし <span class="server-badge">${serverName}</span></div>`;
                }

                if (data.mats && Object.keys(data.mats).length > 0) {
                    let matListHtml = '';
                    for (const [mid, mData] of Object.entries(data.mats)) {
                        matListHtml += `
                            <div class="mat-row">
                                <span class="mat-name"><a href="https://universalis.app/market/${mid}" target="_blank" class="mat-link">${mData.name}</a></span>
                                <span class="mat-amount">x${mData.amount}</span>
                                <span class="mat-price">${(mData.price * mData.amount).toLocaleString()} gil</span>
                            </div>
                        `;
                    }

                    const expectedProfit = priceVal - data.craft_cost;
                    const profitClass = expectedProfit > 0 ? 'profit-good' : 'profit-bad';

                    matsHtml = `
                        <details class="mats-accordion">
                            <summary>素材内訳を見る (合計原価: ${data.craft_cost.toLocaleString()} gil)</summary>
                            <div class="mats-content">
                                ${matListHtml}
                                <div class="mats-total ${profitClass}">
                                    想定利益: ${expectedProfit.toLocaleString()} gil
                                </div>
                            </div>
                        </details>
                    `;
                }
            } else {
                // Fallback to old number format
                priceHtml = `<div class="item-price">最安値: <strong>${data.toLocaleString()}</strong> gil</div>`;
            }
        } else if (Object.keys(marketPriceData).length > 0) {
            priceHtml = `<div class="item-price none">出品なし</div>`;
        }

        card.innerHTML = `
            <div class="item-header">
                <span class="item-level">Lv ${item.level}</span>
                <span class="leve-name" title="${item.leve_name}">${item.leve_name}</span>
            </div>
            <div class="item-body">
                <div class="item-info">
                    <a href="https://universalis.app/market/${item.item_id}" target="_blank" class="item-name item-link">${item.item_name}</a>
                    <span class="item-count">×${item.item_count}</span>
                </div>
                ${priceHtml}
                <div class="item-id-badge">ID: ${item.item_id}</div>
            </div>
            <div class="item-footer">
                <button class="action-btn copy-btn" onclick="copyToClipboard('${item.item_name}')">
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path></svg>
                    名前をコピー
                </button>
            </div>
            ${matsHtml}
        `;
        itemsGrid.appendChild(card);
    });
}

function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        // Find the button and show visual feedback
        const btns = document.querySelectorAll('.copy-btn');
        btns.forEach(btn => {
            if (btn.getAttribute('onclick').includes(text)) {
                const originalHTML = btn.innerHTML;
                btn.innerHTML = 'コピーしました!';
                btn.classList.add('success');
                setTimeout(() => {
                    btn.innerHTML = originalHTML;
                    btn.classList.remove('success');
                }, 1500);
            }
        });
    });
}

// Start the app
document.addEventListener('DOMContentLoaded', init);
