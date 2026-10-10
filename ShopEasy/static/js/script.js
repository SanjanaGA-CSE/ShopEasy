// ShopEasy front-end logic: cart stored in the browser's localStorage.
const CART_KEY = "shopeasy_cart";

function getCart() {
  try {
    return JSON.parse(localStorage.getItem(CART_KEY)) || [];
  } catch (e) {
    return [];
  }
}

function saveCart(cart) {
  localStorage.setItem(CART_KEY, JSON.stringify(cart));
  updateBadge();
}

function updateBadge() {
  const count = getCart().reduce((sum, item) => sum + item.quantity, 0);
  document.querySelectorAll(".cart-count").forEach((el) => {
    el.textContent = count;
  });
}

function formatINR(value) {
  return "₹" + Number(value).toLocaleString("en-IN", { maximumFractionDigits: 2 });
}

function getCookie(name) {
  const match = document.cookie.split("; ").find((row) => row.startsWith(name + "="));
  return match ? decodeURIComponent(match.split("=")[1]) : "";
}

function toast(message) {
  const el = document.createElement("div");
  el.className = "toast";
  el.textContent = message;
  document.body.appendChild(el);
  setTimeout(() => el.remove(), 2200);
}

function addToCart(item) {
  const cart = getCart();
  const existing = cart.find((i) => i.id === item.id);
  if (existing) {
    if (existing.quantity >= item.stock) {
      toast("Only " + item.stock + " available in stock");
      return;
    }
    existing.quantity += 1;
    existing.stock = item.stock;
  } else {
    cart.push({ ...item, quantity: 1 });
  }
  saveCart(cart);
  toast(item.name + " added to cart");
}

function changeQuantity(id, delta) {
  const cart = getCart();
  const item = cart.find((i) => i.id === id);
  if (!item) return;
  const next = item.quantity + delta;
  if (next < 1) return;
  if (next > item.stock) {
    toast("Only " + item.stock + " available in stock");
    return;
  }
  item.quantity = next;
  saveCart(cart);
  renderCart();
}

function removeFromCart(id) {
  saveCart(getCart().filter((i) => i.id !== id));
  renderCart();
}

function el(tag, className, text) {
  const node = document.createElement(tag);
  if (className) node.className = className;
  if (text !== undefined) node.textContent = text;
  return node;
}

function renderCart() {
  const root = document.getElementById("cart-root");
  if (!root) return;
  const cart = getCart();
  root.replaceChildren();

  if (cart.length === 0) {
    const empty = el("p", "empty", "Your cart is empty. ");
    const link = el("a", "", "Browse products");
    link.href = "/";
    empty.appendChild(link);
    root.appendChild(empty);
    return;
  }

  let total = 0;
  const list = el("div", "cart-list");
  cart.forEach((item) => {
    const lineTotal = item.price * item.quantity;
    total += lineTotal;

    const row = el("div", "cart-row");
    const img = el("img");
    img.src = item.image;
    img.alt = item.name;

    const info = el("div", "cart-info");
    info.appendChild(el("strong", "", item.name));
    info.appendChild(el("span", "muted", formatINR(item.price) + " each"));

    const qty = el("div", "qty");
    const minus = el("button", "qty-btn", "−");
    minus.type = "button";
    minus.setAttribute("aria-label", "Decrease quantity of " + item.name);
    minus.addEventListener("click", () => changeQuantity(item.id, -1));
    const plus = el("button", "qty-btn", "+");
    plus.type = "button";
    plus.setAttribute("aria-label", "Increase quantity of " + item.name);
    plus.addEventListener("click", () => changeQuantity(item.id, 1));
    qty.append(minus, el("span", "", String(item.quantity)), plus);

    const sub = el("div", "cart-sub", formatINR(lineTotal));
    const remove = el("button", "link-button", "Remove");
    remove.type = "button";
    remove.addEventListener("click", () => removeFromCart(item.id));

    row.append(img, info, qty, sub, remove);
    list.appendChild(row);
  });
  root.appendChild(list);

  const summary = el("div", "cart-summary");
  summary.appendChild(el("p", "total", "Total: " + formatINR(total)));
  const message = el("p", "error");
  message.id = "cart-error";
  const button = el("button", "btn", root.dataset.auth === "true" ? "Place order" : "Log in to place order");
  button.type = "button";
  button.addEventListener("click", () => checkout(root, button));
  summary.append(message, button);
  root.appendChild(summary);
}

async function checkout(root, button) {
  if (root.dataset.auth !== "true") {
    window.location.href = root.dataset.login;
    return;
  }
  const errorBox = document.getElementById("cart-error");
  errorBox.textContent = "";
  button.disabled = true;

  // Send only ids and quantities. The server looks up the real prices.
  const items = getCart().map((i) => ({ id: i.id, quantity: i.quantity }));
  try {
    const response = await fetch(root.dataset.checkout, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": getCookie("csrftoken"),
      },
      body: JSON.stringify({ items }),
    });
    const data = await response.json().catch(() => ({}));
    if (response.ok) {
      localStorage.removeItem(CART_KEY);
      window.location.href = data.redirect;
    } else {
      errorBox.textContent = data.error || "Something went wrong. Please try again.";
      button.disabled = false;
    }
  } catch (e) {
    errorBox.textContent = "Network error. Please try again.";
    button.disabled = false;
  }
}

document.addEventListener("DOMContentLoaded", () => {
  updateBadge();
  document.querySelectorAll(".add-to-cart").forEach((btn) => {
    btn.addEventListener("click", () => {
      addToCart({
        id: Number(btn.dataset.id),
        name: btn.dataset.name,
        price: parseFloat(btn.dataset.price),
        image: btn.dataset.image,
        stock: Number(btn.dataset.stock),
      });
    });
  });
  renderCart();
});
