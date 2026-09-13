import React, { useEffect, useState } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { useAuth } from '@/context/AuthContext';
import { useTheme } from '@/context/ThemeContext';
import {
  SunIcon, MoonIcon, HomeIcon, SearchIcon, SparkleIcon, ColumnsIcon,
  WalletIcon, BookmarkIcon, UserIcon, ChartIcon, PanelLeftIcon,
} from './Icons';

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Home', icon: HomeIcon, group: 'Explore' },
  { to: '/search', label: 'AI Search', icon: SearchIcon, group: 'Explore' },
  { to: '/recommend', label: 'Recommendations', icon: SparkleIcon, group: 'Explore' },
  { to: '/compare', label: 'Comparison', icon: ColumnsIcon, group: 'Decide' },
  { to: '/budget', label: 'Budget Optimizer', icon: WalletIcon, group: 'Decide' },
  { to: '/saved', label: 'Saved Laptops', icon: BookmarkIcon, group: 'You' },
  { to: '/profile', label: 'Profile', icon: UserIcon, group: 'You' },
];

const ADMIN_NAV_ITEMS = [
  { to: '/analytics', label: 'Analytics', icon: ChartIcon, group: 'Admin' },
  { to: '/admin', label: 'Users & System', icon: UserIcon, group: 'Admin' },
];

const COLLAPSE_STORAGE_KEY = 'ls_sidebar_collapsed';

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(() => {
    try {
      return localStorage.getItem(COLLAPSE_STORAGE_KEY) === '1';
    } catch {
      return false;
    }
  });

  useEffect(() => {
    try {
      localStorage.setItem(COLLAPSE_STORAGE_KEY, collapsed ? '1' : '0');
    } catch {
      /* ignore — sidebar just won't remember its state this session */
    }
  }, [collapsed]);

  async function handleLogout() {
    await logout();
    navigate('/login');
  }

  const items = user?.role === 'admin' ? [...NAV_ITEMS, ...ADMIN_NAV_ITEMS] : NAV_ITEMS;
  let lastGroup = '';

  return (
    <div className="shell">
      <div className={`drawer-backdrop ${drawerOpen ? 'open' : ''}`} onClick={() => setDrawerOpen(false)} />
      <nav className={`shell-sidebar ${drawerOpen ? 'open' : ''} ${collapsed ? 'collapsed' : ''}`} aria-label="Primary">
        <div className="shell-brand-row">
          <Link to="/dashboard" className="shell-brand">
            <span className="brand-mark" aria-hidden="true"><img src="/logo-mark.png" alt="" /></span>
            <strong>LaptopSathi</strong>
          </Link>
          <button
            type="button"
            className="sidebar-collapse-btn"
            onClick={() => setCollapsed((c) => !c)}
            aria-label={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            title={collapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            <PanelLeftIcon width={14} height={14} />
          </button>
        </div>
        {items.map((item) => {
          const showGroup = item.group !== lastGroup;
          lastGroup = item.group;
          const Icon = item.icon;
          const active = location.pathname === item.to;
          return (
            <React.Fragment key={item.to}>
              {showGroup && <div className="shell-nav-group">{item.group}</div>}
              <Link
                to={item.to}
                className={`shell-nav-btn ${active ? 'active' : ''}`}
                aria-current={active ? 'page' : undefined}
                title={item.label}
                onClick={() => setDrawerOpen(false)}
              >
                <Icon width={16} height={16} />
                <span>{item.label}</span>
              </Link>
            </React.Fragment>
          );
        })}
        <div className="shell-sidebar-footer">
          Built by <strong>Harsh Saxena</strong><br />LaptopSathi AI · v1.0
        </div>
      </nav>

      <div className="shell-content">
        <header className="shell-topbar">
          <button
            type="button"
            className="icon-btn hamburger-btn"
            aria-label="Open navigation menu"
            onClick={() => setDrawerOpen((o) => !o)}
          >
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M4 6h16M4 12h16M4 18h16" /></svg>
          </button>
          <div style={{ flex: 1 }} />
          {user?.role === 'admin' && <span className="role-badge">Admin</span>}
          <button className="icon-btn" onClick={toggleTheme} aria-label="Toggle theme">
            {theme === 'dark' ? <SunIcon width={15} height={15} /> : <MoonIcon width={15} height={15} />}
          </button>
          <button className="btn btn-ghost" style={{ width: 'auto' }} onClick={handleLogout}>
            Logout
          </button>
        </header>
        <main className="shell-main">{children}</main>
      </div>
    </div>
  );
}
