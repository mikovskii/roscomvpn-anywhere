const base =
  "https://raw.githubusercontent.com/mikovskii/roscomvpn-anywhere/main/ANYWHERE";

const profiles = {
  default: {
    code: "PROFILE / DEFAULT",
    title: "Сбалансированный режим",
    description:
      "RU/BY и доверенные сервисы напрямую. YouTube, Telegram, GitHub и другие выбранные сервисы через VPN. Реклама и телеметрия блокируются.",
    rules: [
      ["DIRECT Domains", "DIRECT", `${base}/DEFAULT/DIRECT_DOMAINS.arrs`],
      ["DIRECT IP 1", "DIRECT", `${base}/DEFAULT/DIRECT_IP_1.arrs`],
      ["DIRECT IP 2", "DIRECT", `${base}/DEFAULT/DIRECT_IP_2.arrs`],
      ["DIRECT IP 3", "DIRECT", `${base}/DEFAULT/DIRECT_IP_3.arrs`],
      ["DIRECT IP 4", "DIRECT", `${base}/DEFAULT/DIRECT_IP_4.arrs`],
      ["PROXY", "ВАШ VPN", `${base}/DEFAULT/PROXY.arrs`],
      ["REJECT", "REJECT", `${base}/DEFAULT/REJECT.arrs`],
    ],
  },
  whitelist: {
    code: "PROFILE / WHITELIST",
    title: "Строгий белый список",
    description:
      "Только доверенные ресурсы работают напрямую. Весь остальной трафик использует выбранный в Anywhere маршрут по умолчанию.",
    rules: [
      ["DIRECT", "DIRECT", `${base}/WHITELIST/DIRECT.arrs`],
      ["REJECT", "REJECT", `${base}/WHITELIST/REJECT.arrs`],
    ],
  },
};

const list = document.querySelector("#rule-list");
const description = document.querySelector("#profile-description");
const toast = document.querySelector("#toast");
let toastTimer;

function showToast() {
  toast.classList.add("visible");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => toast.classList.remove("visible"), 1800);
}

async function copyLink(url) {
  await navigator.clipboard.writeText(url);
  showToast();
}

function renderProfile(name) {
  const profile = profiles[name];
  description.innerHTML = `
    <div>
      <span class="profile-code">${profile.code}</span>
      <h2>${profile.title}</h2>
    </div>
    <p>${profile.description}</p>
  `;

  list.replaceChildren(
    ...profile.rules.map(([ruleName, action, url], index) => {
      const row = document.createElement("article");
      row.className = "rule-row";
      row.innerHTML = `
        <span class="rule-index">${String(index + 1).padStart(2, "0")}</span>
        <span class="rule-name">${ruleName}</span>
        <span class="rule-action">${action}</span>
      `;
      const button = document.createElement("button");
      button.className = "copy-button";
      button.type = "button";
      button.textContent = "КОПИРОВАТЬ ССЫЛКУ";
      button.addEventListener("click", () => copyLink(url));
      row.append(button);
      return row;
    }),
  );
}

document.querySelectorAll(".profile-tab").forEach((tab) => {
  tab.addEventListener("click", () => {
    document.querySelectorAll(".profile-tab").forEach((item) => {
      const active = item === tab;
      item.classList.toggle("active", active);
      item.setAttribute("aria-selected", String(active));
    });
    renderProfile(tab.dataset.profile);
  });
});

fetch("stats.json")
  .then((response) => {
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return response.json();
  })
  .then((stats) => {
    document.querySelector("#geoip-version").textContent =
      stats.sources.geoip.tag;
    document.querySelector("#geosite-version").textContent =
      stats.sources.geosite.tag;
    document.querySelector("#default-rules").textContent =
      `${stats.profiles.DEFAULT.rules.toLocaleString("ru-RU")} правил`;
    document.querySelector("#whitelist-rules").textContent =
      `${stats.profiles.WHITELIST.rules.toLocaleString("ru-RU")} правил`;
  })
  .catch(() => {
    document.querySelector("#geoip-version").textContent = "см. GitHub";
    document.querySelector("#geosite-version").textContent = "см. GitHub";
  });

renderProfile("default");
