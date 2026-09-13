import React from 'react';
import { Laptop, RetailerLink } from '@/types/domain';
import { ScoreDials } from './ScoreDials';
import { StarIcon, PlusIcon, WalletIcon, ExternalLinkIcon } from '../Icons';

interface LaptopCardProps {
  laptop: Laptop;
  onSave?: (id: number) => void;
  saved?: boolean;
  onAddToCompare?: (id: number) => void;
  onBudgetOptimize?: (id: number) => void;
  retailerLinks?: RetailerLink[];
  extra?: React.ReactNode;
}

export function LaptopCard({ laptop, onSave, saved, onAddToCompare, onBudgetOptimize, retailerLinks, extra }: LaptopCardProps) {
  return (
    <div className="laptop-card">
      <div className="lhead">
        <div>
          <h3>
            {laptop.brand} {laptop.model_name} <span className="id-tag" style={{ fontFamily: 'var(--font-mono)' }}>#{laptop.id}</span>
          </h3>
          <div className="specs-row">
            <span>{laptop.cpu_name || '—'}</span><span className="sep">·</span>
            <span>{laptop.gpu_name || '—'}</span><span className="sep">·</span>
            <span>{laptop.ram_gb}GB RAM</span><span className="sep">·</span>
            <span>{laptop.storage_gb}GB {laptop.storage_type}</span><span className="sep">·</span>
            <span>{laptop.display_size_inch || '—'}&quot; {laptop.display_resolution || ''} @{laptop.refresh_rate_hz || 60}Hz</span><span className="sep">·</span>
            <span>{laptop.battery_life_hours || '—'}h battery</span><span className="sep">·</span>
            <span>{laptop.weight_kg || '—'}kg</span>
          </div>
        </div>
        <div className="price-tag">₹{Math.round(laptop.price_inr).toLocaleString('en-IN')}</div>
      </div>

      <ScoreDials scores={laptop.scores} />
      {extra}

      {retailerLinks && retailerLinks.length > 0 && (
        <div className="retailer-links-row">
          {retailerLinks.map((link) => (
            <a
              key={link.retailer}
              className="btn btn-ghost btn-retailer"
              href={link.url}
              target="_blank"
              rel="noopener noreferrer"
            >
              <ExternalLinkIcon width={14} height={14} /> {link.label}
            </a>
          ))}
        </div>
      )}

      {(onSave || onAddToCompare || onBudgetOptimize) && (
        <div className="actions-row">
          {onSave && (
            <button type="button" className="btn btn-ghost" style={{ width: 'auto' }} onClick={() => onSave(laptop.id)}>
              <StarIcon width={14} height={14} /> {saved ? 'Remove' : 'Save'}
            </button>
          )}
          {onAddToCompare && (
            <button type="button" className="btn btn-ghost" style={{ width: 'auto' }} onClick={() => onAddToCompare(laptop.id)}>
              <PlusIcon width={14} height={14} /> Add to comparison
            </button>
          )}
          {onBudgetOptimize && (
            <button type="button" className="btn btn-ghost" style={{ width: 'auto' }} onClick={() => onBudgetOptimize(laptop.id)}>
              <WalletIcon width={14} height={14} /> Budget optimize
            </button>
          )}
        </div>
      )}
    </div>
  );
}
