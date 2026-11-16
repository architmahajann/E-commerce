import React, { useEffect, useState } from 'react'
import { createRoot } from 'react-dom/client'
import { api, login, logout, register } from './api'
import './styles.css'

function App() {
  const [products, setProducts] = useState([])
  const [cart, setCart] = useState(null)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [username, setUsername] = useState('')
  const [isRegistering, setIsRegistering] = useState(false)
  const [message, setMessage] = useState('')
  const [loading, setLoading] = useState(true)
  const [shipping, setShipping] = useState({ address: '', phone: '', city: '', state: '', zipCode: '' })

  const authenticated = Boolean(localStorage.getItem('accessToken'))

  async function load() {
    setLoading(true)
    try {
      setProducts(await api('/products/'))
      if (localStorage.getItem('accessToken')) setCart(await api('/cart/'))
    } catch (error) {
      setMessage(error.message)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => { load() }, [])

  async function add(product) {
    if (!authenticated) return setMessage('Sign in to add items to your cart.')
    try {
      setCart(await api('/cart/add/', { method: 'POST', body: JSON.stringify({ product_id: product.id, quantity: 1 }) }))
      setMessage(`${product.name} added to your cart.`)
    } catch (error) { setMessage(error.message) }
  }

  async function signIn(event) {
    event.preventDefault()
    try {
      if (isRegistering) {
        await register(email, username, password)
        await login(email, password)
        setMessage('Account created. You are signed in.')
      } else {
        await login(email, password)
        setMessage('Signed in.')
      }
      await load()
    }
    catch (error) { setMessage(error.message) }
  }

  function signOut() { logout(); setCart(null); setMessage('Signed out.') }

  async function changeQuantity(itemId, change) {
    try {
      setCart(await api(`/cart/items/${itemId}/`, {
        method: 'PATCH',
        body: JSON.stringify({ change }),
      }))
    } catch (error) { setMessage(error.message) }
  }

  async function placeOrder(event) {
    event.preventDefault()
    try {
      await api('/orders/place/', { method: 'POST', body: JSON.stringify({ shippingAddress: shipping }) })
      setCart({ items: [], grand_total: '0.00' })
      setMessage('Order placed successfully.')
    } catch (error) { setMessage(error.message) }
  }

  return (
    <main>
      <header className="topbar">
        <div><span className="eyebrow">CLICKMART</span><h1>Everything you need, delivered.</h1></div>
        {authenticated ? <button className="secondary" onClick={signOut}>Sign out</button> : null}
      </header>
      <section className="hero"><p>Curated essentials. Secure checkout. No distractions.</p></section>
      {message && <div className="notice">{message}</div>}
      {!authenticated && <form className="login" onSubmit={signIn}>
        {isRegistering && <input aria-label="Username" placeholder="Username" value={username} onChange={event => setUsername(event.target.value)} required />}
        <input aria-label="Email" type="email" placeholder="Email" value={email} onChange={event => setEmail(event.target.value)} required />
        <input aria-label="Password" type="password" placeholder="Password" value={password} onChange={event => setPassword(event.target.value)} required />
        <button type="submit">{isRegistering ? 'Create account' : 'Sign in'}</button>
        <button type="button" className="mode-toggle" onClick={() => { setIsRegistering(!isRegistering); setMessage('') }}>
          {isRegistering ? 'Have an account? Sign in' : 'New here? Create an account'}
        </button>
      </form>}
      <div className="layout">
        <section><div className="section-heading"><span className="eyebrow">THE CATALOG</span><h2>Shop the collection</h2></div>
          {loading ? <p>Loading products...</p> : <div className="grid">{products.map(product =>
            <article className="card" key={product.id}>
              {product.image ? <img src={product.image} alt="" /> : <div className="placeholder">CM</div>}
              <div className="card-body"><span className="muted">{product.stock} in stock</span><h3>{product.name}</h3><p>{product.description}</p><strong>${product.price}</strong><button onClick={() => add(product)} disabled={!product.stock}>Add to cart</button></div>
            </article>)}</div>}
        </section>
        <aside className="cart"><span className="eyebrow">YOUR CART</span><h2>{cart?.items?.length || 0} items</h2>
          {cart?.items?.map(item => <div className="cart-row" key={item.id}><span>{item.product_name} <small><button type="button" onClick={() => changeQuantity(item.id, -1)}>-</button> {item.quantity} <button type="button" onClick={() => changeQuantity(item.id, 1)}>+</button></small></span><strong>${item.total_price}</strong></div>)}
          <div className="total"><span>Total</span><strong>${cart?.grand_total || '0.00'}</strong></div>
          {authenticated && cart?.items?.length > 0 && <form className="checkout" onSubmit={placeOrder}>
            <h3>Shipping details</h3>
            {Object.entries(shipping).map(([field, value]) => <input key={field} required placeholder={field === 'zipCode' ? 'ZIP code' : field[0].toUpperCase() + field.slice(1)} value={value} onChange={event => setShipping({ ...shipping, [field]: event.target.value })} />)}
            <button type="submit">Place order</button>
          </form>}
        </aside>
      </div>
    </main>
  )
}

createRoot(document.getElementById('root')).render(<React.StrictMode><App /></React.StrictMode>)
