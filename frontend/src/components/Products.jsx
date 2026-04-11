import { useState, useEffect, useCallback } from 'react'
import { fetchProducts } from '../api.js'

function stockLevel(stock) {
  if (stock === 0) return { label: 'Out of stock', cls: 'badge-red', barCls: 'low' }
  if (stock < 5)  return { label: 'Low stock',    cls: 'badge-yellow', barCls: 'mid' }
  return              { label: 'In stock',         cls: 'badge-green',  barCls: '' }
}

export default function Products() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [sort, setSort] = useState('name')

  const load = useCallback(async () => {
    setLoading(true)
    try {
      const res = await fetchProducts()
      setData(res)
    } catch (e) {
      console.error(e)
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => { load() }, [load])

  const raw = data?.products ?? []
  const maxStock = Math.max(...raw.map(p => p.stock), 1)

  let products = raw.filter(p =>
    !search || p.name?.toLowerCase().includes(search.toLowerCase())
  )

  if (sort === 'name')  products = [...products].sort((a, b) => a.name.localeCompare(b.name))
  if (sort === 'price') products = [...products].sort((a, b) => a.price - b.price)
  if (sort === 'stock') products = [...products].sort((a, b) => b.stock - a.stock)

  return (
    <>
      <div className="page-header">
        <h1>Products</h1>
        <p>Inventory visible to the support bot</p>
        <div className="header-actions">
          <button className="refresh-btn" onClick={load}>↻ Refresh</button>
        </div>
      </div>

      <div className="page-content">
        {/* Toolbar */}
        <div style={{ display: 'flex', gap: 10, marginBottom: 18, alignItems: 'center' }}>
          <input
            placeholder="Search products…"
            value={search}
            onChange={e => setSearch(e.target.value)}
            style={{
              background: 'var(--surface)',
              border: '1px solid var(--border)',
              borderRadius: 7,
              padding: '8px 13px',
              color: 'var(--text)',
              fontSize: 13,
              fontFamily: 'var(--font)',
              width: 220,
              outline: 'none',
            }}
          />
          <div style={{ display: 'flex', gap: 6 }}>
            {['name', 'price', 'stock'].map(s => (
              <button
                key={s}
                className={`badge ${sort === s ? 'badge-green' : 'badge-gray'}`}
                style={{ cursor: 'pointer', border: 'none', textTransform: 'capitalize' }}
                onClick={() => setSort(s)}
              >
                ↕ {s}
              </button>
            ))}
          </div>
          <span style={{ marginLeft: 'auto', fontSize: 12, color: 'var(--muted)', fontFamily: 'var(--mono)' }}>
            {products.length} product{products.length !== 1 ? 's' : ''}
          </span>
        </div>

        {loading && !data ? (
          <div className="loading"><div className="spinner" />Loading products…</div>
        ) : products.length === 0 ? (
          <div className="empty">
            <div className="empty-icon">📦</div>
            No products found
          </div>
        ) : (
          <div className="products-grid">
            {products.map(p => {
              const level = stockLevel(p.stock)
              const pct = Math.min((p.stock / maxStock) * 100, 100)
              return (
                <div className="product-card" key={p.id}>
                  <div className="product-name">{p.name}</div>
                  <div className="product-price">₹{p.price?.toLocaleString('en-IN')}</div>
                  {p.description && (
                    <div className="product-desc">{p.description}</div>
                  )}
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 6 }}>
                    <span className={`badge ${level.cls}`} style={{ fontSize: 10 }}>{level.label}</span>
                    <span style={{ fontSize: 11, color: 'var(--muted)', fontFamily: 'var(--mono)' }}>
                      {p.stock} units
                    </span>
                  </div>
                  <div className="stock-bar">
                    <div
                      className={`stock-bar-fill ${level.barCls}`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              )
            })}
          </div>
        )}

        {/* Summary table */}
        {!loading && products.length > 0 && (
          <div className="card section-gap">
            <div className="card-title">Product Table</div>
            <div className="table-wrap">
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Name</th>
                    <th>Price (₹)</th>
                    <th>Stock</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {products.map(p => {
                    const level = stockLevel(p.stock)
                    return (
                      <tr key={p.id}>
                        <td className="mono" style={{ color: 'var(--muted)' }}>{p.id}</td>
                        <td style={{ fontWeight: 500 }}>{p.name}</td>
                        <td className="mono">₹{p.price?.toLocaleString('en-IN')}</td>
                        <td className="mono">{p.stock}</td>
                        <td><span className={`badge ${level.cls}`} style={{ fontSize: 10 }}>{level.label}</span></td>
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </div>
    </>
  )
}
