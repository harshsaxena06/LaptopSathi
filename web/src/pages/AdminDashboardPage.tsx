import React, { useState } from 'react';
import { AppShell } from '@/components/AppShell';
import { DatabaseIcon, UserIcon, SettingsIcon, TerminalIcon } from '@/components/Icons';
import { KnowledgeBasePanel } from '@/components/admin/KnowledgeBasePanel';
import { UsersPanel } from '@/components/admin/UsersPanel';
import { SettingsPanel } from '@/components/admin/SettingsPanel';
import { LogsPanel } from '@/components/admin/LogsPanel';

type Tab = 'kb' | 'users' | 'settings' | 'logs';

const TABS: Array<{ id: Tab; label: string; icon: typeof DatabaseIcon }> = [
  { id: 'kb', label: 'Knowledge Base', icon: DatabaseIcon },
  { id: 'users', label: 'Users', icon: UserIcon },
  { id: 'settings', label: 'Settings', icon: SettingsIcon },
  { id: 'logs', label: 'Logs', icon: TerminalIcon },
];

export function AdminDashboardPage() {
  const [tab, setTab] = useState<Tab>('kb');

  return (
    <AppShell>
      <div className="page-head">
        <div>
          <h1>Admin</h1>
          <p>
            Manage everything from here — update the laptop dataset, promote or deactivate users,
            check live config, and read server logs. No backend or database access needed.
          </p>
        </div>
      </div>

      <div className="tab-row" role="tablist" aria-label="Admin sections">
        {TABS.map((t) => (
          <button
            key={t.id}
            type="button"
            role="tab"
            aria-selected={tab === t.id}
            className={`tab-btn ${tab === t.id ? 'active' : ''}`}
            onClick={() => setTab(t.id)}
          >
            <t.icon width={14} height={14} />
            {t.label}
          </button>
        ))}
      </div>

      {tab === 'kb' && <KnowledgeBasePanel />}
      {tab === 'users' && <UsersPanel />}
      {tab === 'settings' && <SettingsPanel />}
      {tab === 'logs' && <LogsPanel />}
    </AppShell>
  );
}
