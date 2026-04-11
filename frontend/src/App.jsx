import { useState } from 'react'
import './App.css'
import Sidebar from './components/Sidebar.jsx'
import Overview from './components/Overview.jsx'
import Conversations from './components/Conversations.jsx'
import Products from './components/Products.jsx'
import TestBot from './components/TestBot.jsx'

const PAGES = {
  overview:      Overview,
  conversations: Conversations,
  products:      Products,
  testbot:       TestBot,
}

export default function App() {
  const [active, setActive] = useState('overview')
  const Page = PAGES[active] ?? Overview

  return (
    <div className="layout">
      <Sidebar active={active} setActive={setActive} />
      <main className="main">
        <Page />
      </main>
    </div>
  )
}
