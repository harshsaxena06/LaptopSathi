import React, { useEffect, useRef, useState } from 'react';
import { adminApi, KBVersion } from '@/api/adminApi';
import { useToast } from '@/context/ToastContext';
import { ApiError } from '@/types/auth';
import { UploadIcon, RefreshIcon, DatabaseIcon } from '@/components/Icons';

export function KnowledgeBasePanel() {
  const { showToast } = useToast();
  const fileInputRef = useRef<HTMLInputElement>(null);

  const [file, setFile] = useState<File | null>(null);
  const [notes, setNotes] = useState('');
  const [uploading, setUploading] = useState(false);
  const [rebuilding, setRebuilding] = useState(false);

  const [versions, setVersions] = useState<KBVersion[] | null>(null);
  const [versionsError, setVersionsError] = useState<string | null>(null);
  const [versionsLoading, setVersionsLoading] = useState(true);

  async function loadVersions() {
    setVersionsLoading(true);
    setVersionsError(null);
    try {
      const data = await adminApi.listVersions();
      setVersions(data.slice().reverse()); // newest first
    } catch (err) {
      setVersionsError(err instanceof ApiError ? err.message : 'Could not load version history.');
    } finally {
      setVersionsLoading(false);
    }
  }

  useEffect(() => {
    loadVersions();
  }, []);

  async function handleUpload(e: React.FormEvent) {
    e.preventDefault();
    if (!file) {
      showToast('Choose a .csv or .json file first.', 'error');
      return;
    }
    setUploading(true);
    try {
      const result = await adminApi.uploadKnowledgeBase(file, notes);
      showToast(
        `Ingested ${result.record_count} laptops as ${result.version_tag}` +
          (result.index_rebuilt ? ' — search index rebuilt.' : ' — search index rebuild FAILED, see logs.'),
        result.index_rebuilt ? 'success' : 'error',
      );
      if (result.invalid_rows > 0 || result.duplicate_rows > 0) {
        showToast(
          `${result.invalid_rows} invalid row(s) and ${result.duplicate_rows} duplicate(s) were skipped.`,
          'info',
        );
      }
      setFile(null);
      setNotes('');
      if (fileInputRef.current) fileInputRef.current.value = '';
      loadVersions();
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : 'Upload failed.', 'error');
    } finally {
      setUploading(false);
    }
  }

  async function handleRebuild() {
    setRebuilding(true);
    try {
      const result = await adminApi.rebuildIndex();
      showToast(`Search index rebuilt — ${result.vectors_indexed} laptops indexed.`, 'success');
    } catch (err) {
      showToast(err instanceof ApiError ? err.message : 'Index rebuild failed.', 'error');
    } finally {
      setRebuilding(false);
    }
  }

  return (
    <div className="grid cols-2" style={{ alignItems: 'start' }}>
      <div className="card">
        <h3 style={{ marginBottom: 4 }}>Update the knowledge base</h3>
        <p style={{ fontSize: 12.5, color: 'var(--text-2)', marginBottom: 18 }}>
          Upload a .csv or .json export of laptops. It's cleaned, scored, saved as a new
          dataset version, and the search index is rebuilt automatically — nothing else to run.
        </p>
        <form onSubmit={handleUpload}>
          <div className="field">
            <label htmlFor="kb-file">Dataset file (.csv or .json)</label>
            <input
              id="kb-file"
              ref={fileInputRef}
              className="control"
              type="file"
              accept=".csv,.json"
              onChange={(e) => setFile(e.target.files?.[0] ?? null)}
            />
          </div>
          <div className="field">
            <label htmlFor="kb-notes">Notes (optional)</label>
            <input
              id="kb-notes"
              className="control"
              type="text"
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              placeholder="e.g. August price refresh"
              maxLength={300}
            />
          </div>
          <button type="submit" className="btn btn-primary" disabled={uploading || !file}>
            <UploadIcon width={15} height={15} />
            {uploading ? 'Uploading…' : 'Upload & ingest'}
          </button>
        </form>

        <div style={{ borderTop: '1px dashed var(--border)', marginTop: 18, paddingTop: 16 }}>
          <p style={{ fontSize: 12, color: 'var(--text-2)', marginBottom: 10 }}>
            Edited data another way, or think the search index is stale? Force a rebuild without
            re-uploading anything.
          </p>
          <button type="button" className="btn btn-ghost" onClick={handleRebuild} disabled={rebuilding}>
            <RefreshIcon width={14} height={14} />
            {rebuilding ? 'Rebuilding…' : 'Rebuild search index'}
          </button>
        </div>
      </div>

      <div className="card">
        <h3 style={{ marginBottom: 12 }}>Version history</h3>
        {versionsLoading && <p style={{ color: 'var(--text-2)', fontSize: 13 }}>Loading…</p>}
        {versionsError && <p className="field-error">{versionsError}</p>}
        {versions && versions.length === 0 && (
          <div className="state-block">
            <div className="state-icon"><DatabaseIcon width={22} height={22} /></div>
            <h3>No versions yet</h3>
            <p>Upload a dataset to create the first version.</p>
          </div>
        )}
        {versions && versions.length > 0 && (
          <div className="table-scroll">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Version</th>
                  <th>Laptops</th>
                  <th>Notes</th>
                  <th>Created</th>
                </tr>
              </thead>
              <tbody>
                {versions.map((v) => (
                  <tr key={v.version_tag}>
                    <td style={{ fontFamily: 'var(--font-mono)', color: 'var(--accent)' }}>{v.version_tag}</td>
                    <td>{v.record_count}</td>
                    <td style={{ color: 'var(--text-2)' }}>{v.notes || '—'}</td>
                    <td style={{ color: 'var(--text-2)', whiteSpace: 'nowrap' }}>
                      {new Date(`${v.created_at}Z`).toLocaleString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
