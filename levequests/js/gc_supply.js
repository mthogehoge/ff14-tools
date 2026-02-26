const CLASS_MAP = {
    8: "木工師 (CRP)",
    9: "鍛冶師 (BSM)",
    10: "甲冑師 (ARM)",
    11: "彫金師 (GSM)",
    12: "革細工師 (LTW)",
    13: "裁縫師 (WVR)",
    14: "錬金術師 (ALC)",
    15: "調理師 (CUL)",
    16: "採掘師 (MIN)",
    17: "園芸師 (BTN)",
    18: "漁師 (FSH)"
};

let gcSupplyData = null;
let itemNamesData = null;
let marketPriceData = null;

const jobTabsContainer = document.getElementById('job-tabs');
const resultsContainer = document.getElementById('results-container');
const loadingMsg = document.getElementById('loading-msg');
const sidebarNav = document.getElementById('sidebar-nav');
const levelNavList = document.getElementById('level-nav-list');

let activeClassId = null;

async function loadData() {
    try {
        const [gcRes, itemsRes, priceRes] = await Promise.all([
            fetch('/levequests/gc-supply.json').then(res => res.json()),
            fetch('/universalis_tools/teamcraft_items.json').then(res => res.json()),
            fetch('/levequests/gc_market_prices.json').catch(() => null).then(res => res ? res.json() : {})
        ]);

        gcSupplyData = gcRes;
        itemNamesData = itemsRes;
        marketPriceData = priceRes;

        loadingMsg.style.display = 'none';

        // initialize tabs
        renderTabs();

        // select first tab by default
        const classIds = Object.keys(CLASS_MAP);
        if (classIds.length > 0) {
            selectTab(classIds[0]);
        }
    } catch (err) {
        loadingMsg.textContent = 'データの読み込みに失敗しました。';
        console.error(err);
    }
}

function renderTabs() {
    jobTabsContainer.innerHTML = '';
    const classIds = Object.keys(CLASS_MAP).sort((a, b) => parseInt(a) - parseInt(b));

    classIds.forEach(id => {
        const btn = document.createElement('button');
        btn.className = 'tab-btn';
        btn.textContent = CLASS_MAP[id];
        btn.dataset.id = id;
        btn.onclick = () => selectTab(id);
        jobTabsContainer.appendChild(btn);
    });
}

function selectTab(classId) {
    activeClassId = classId;

    // Update active state
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.classList.toggle('active', btn.dataset.id === String(classId));
    });

    renderJob(classId);
}

function smoothScroll(e, targetId) {
    e.preventDefault();
    const target = document.getElementById(targetId);
    if (target) {
        window.scrollTo({
            top: target.getBoundingClientRect().top + window.scrollY - 30, // 30px top gutter
            behavior: 'smooth'
        });
    }
}

// Global scope so onclick works
window.smoothScroll = smoothScroll;

function renderJob(classId) {
    resultsContainer.innerHTML = '';
    levelNavList.innerHTML = '';

    if (!gcSupplyData || !itemNamesData) return;

    // Collect all items for this classId across all levels 1-100
    const jobItems = [];
    for (let level = 1; level <= 100; level++) {
        if (gcSupplyData[level] && gcSupplyData[level][classId]) {
            const itemsForLevel = gcSupplyData[level][classId];
            itemsForLevel.forEach(itemInfo => {
                jobItems.push({
                    level: level,
                    data: itemInfo
                });
            });
        }
    }

    if (jobItems.length === 0) {
        sidebarNav.style.display = 'none';
        resultsContainer.innerHTML = `<div class="message" style="grid-column: 1 / -1;">このクラスの納品データは見つかりません。</div>`;
        return;
    }

    sidebarNav.style.display = 'block';

    const ranges = [
        { label: 'Lv 1〜10', max: 10 },
        { label: 'Lv 11〜20', max: 20 },
        { label: 'Lv 21〜30', max: 30 },
        { label: 'Lv 31〜40', max: 40 },
        { label: 'Lv 41〜50', max: 50 },
        { label: 'Lv 51〜60', max: 60 },
        { label: 'Lv 61〜70', max: 70 },
        { label: 'Lv 71〜80', max: 80 },
        { label: 'Lv 81〜90', max: 90 },
        { label: 'Lv 91〜100', max: 100 }
    ];

    let currentRangeIndex = 0;

    // Process and display each item
    jobItems.forEach((bundle, index) => {
        const level = bundle.level;
        const itemData = bundle.data;

        let anchorAttr = '';
        while (currentRangeIndex < ranges.length && level > ranges[currentRangeIndex].max) {
            currentRangeIndex++;
        }

        if (currentRangeIndex < ranges.length && !ranges[currentRangeIndex].hasAnchor) {
            anchorAttr = `id="range-${currentRangeIndex}"`;
            ranges[currentRangeIndex].hasAnchor = true;

            const li = document.createElement('li');
            li.innerHTML = `<a href="#range-${currentRangeIndex}" onclick="window.smoothScroll(event, 'range-${currentRangeIndex}')">${ranges[currentRangeIndex].label}</a>`;
            levelNavList.appendChild(li);
        }

        const itemId = itemData.itemId;
        const count = itemData.count;
        const seals = itemData.reward ? itemData.reward.seals : '???';
        const xp = itemData.reward ? itemData.reward.xp.toLocaleString() : '???';

        const itemNameJa = itemNamesData[itemId] && itemNamesData[itemId].ja ? itemNamesData[itemId].ja : `Unknown (${itemId})`;

        const card = document.createElement('div');
        card.className = 'item-card';
        if (anchorAttr) {
            card.id = `range-${currentRangeIndex}`; // Apply the ID to the card
        }

        let priceHtml = '';
        let matsHtml = '';

        if (marketPriceData && marketPriceData[itemId]) {
            const data = marketPriceData[itemId];
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
            }
        } else if (Object.keys(marketPriceData || {}).length > 0) {
            priceHtml = `<div class="item-price none">計算中... または出品記録なし</div>`;
        }

        card.innerHTML = `
            <div class="item-header">
                <span class="level-badge">Lv ${level}</span>
                <span class="leve-name" title="${itemNameJa}">${itemNameJa}</span>
            </div>
            <div class="item-body">
                <div class="item-info">
                    <a href="https://universalis.app/market/${itemId}" target="_blank" class="item-name item-link">マケボ相場を見る</a>
                    <span class="item-count">×${count}</span>
                </div>
                ${priceHtml}
                <div class="item-price" style="margin-top: 5px; color: #f7ce55;">軍票: ${seals} / 経験値: ${xp}</div>
                <div class="item-id-badge">ID: ${itemId}</div>
            </div>
            ${matsHtml}
        `;
        resultsContainer.appendChild(card);
    });
}

// Init
loadData();
