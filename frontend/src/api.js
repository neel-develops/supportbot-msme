const BASE = import.meta.env.VITE_API_URL || ''

export async function fetchHealth() {
  const r = await fetch(`${BASE}/health`)
  return r.json()
}

export async function fetchMessages(limit = 50) {
  const r = await fetch(`${BASE}/messages?limit=${limit}`)
  return r.json()
}

export async function fetchProducts() {
  const r = await fetch(`${BASE}/products`)
  return r.json()
}

export async function simulateMessage(customerNumber, message) {
  const r = await fetch(`${BASE}/simulate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ customer_number: customerNumber, message }),
  })
  return r.json()
}
