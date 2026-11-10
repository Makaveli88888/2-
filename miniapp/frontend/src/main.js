const PACKS = [
  { id: "starter", stars: 50, chips: 5000, label: "Starter" },
  { id: "standard", stars: 150, chips: 16500, label: "Standard" },
  { id: "high", stars: 500, chips: 60000, label: "High" },
];

const tg = window.Telegram?.WebApp;
if (tg) tg.ready();

async function buy(packId) {
  const userId = tg?.initDataUnsafe?.user?.id || 0;
  const res = await fetch("http://localhost:8000/cashier/stars-invoice", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ pack: packId, user_id: userId }),
  });
  const data = await res.json();
  if (tg && data.invoice_link) {
    tg.openInvoice(data.invoice_link, (status) => {
      alert("Status: " + status);
    });
  } else {
    alert("Mock invoice: " + data.invoice_link);
  }
}

const container = document.getElementById("packs");
PACKS.forEach(p => {
  const btn = document.createElement("button");
  btn.textContent = `${p.label} — ${p.stars} Stars → ${p.chips} chips`;
  btn.onclick = () => buy(p.id);
  container.appendChild(btn);
  container.appendChild(document.createElement("br"));
});
