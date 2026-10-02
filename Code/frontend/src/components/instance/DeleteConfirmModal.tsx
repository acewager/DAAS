import { useState } from "react";

interface DeleteConfirmModalProps {
  instanceName: string;
  persistent: boolean;
  onConfirm: (deleteData: boolean) => void;
  onCancel: () => void;
  isPending: boolean;
}

/**
 * Delete confirmation workflow (VS-042, Sprint 6) with the Retain/Delete
 * data option (VS-043). Per 09_User_Experience.md, destructive actions
 * always require confirmation.
 */
export default function DeleteConfirmModal({ instanceName, persistent, onConfirm, onCancel, isPending }: DeleteConfirmModalProps) {
  const [deleteData, setDeleteData] = useState(false);

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4" role="dialog" aria-modal="true" aria-label={`Delete ${instanceName}`}>
      <div className="w-full max-w-md space-y-4 rounded-lg border border-border bg-white p-5 shadow-xl dark:bg-slate-900">
        <div className="space-y-1">
          <h2 className="text-lg font-semibold">Delete instance</h2>
          <p className="text-sm text-slate-600 dark:text-slate-300">
            You are deleting <strong>{instanceName}</strong>. The container will be removed. This cannot be undone.
          </p>
        </div>

        {persistent && (
          <fieldset className="space-y-2 rounded border border-border p-3">
            <legend className="px-1 text-sm font-medium">Persistent data</legend>
            <label className="flex items-center gap-2 text-sm">
              <input type="radio" name="delete-data" checked={!deleteData} onChange={() => setDeleteData(false)} />
              Keep my data (can be re-attached later)
            </label>
            <label className="flex items-center gap-2 text-sm">
              <input type="radio" name="delete-data" checked={deleteData} onChange={() => setDeleteData(true)} />
              Delete my data permanently
            </label>
          </fieldset>
        )}

        <div className="flex items-center justify-end gap-2">
          <button className="rounded border border-border px-4 py-2 text-sm" onClick={onCancel} disabled={isPending} type="button">
            Cancel
          </button>
          <button className="rounded bg-red-600 px-4 py-2 text-sm text-white disabled:opacity-50" onClick={() => onConfirm(deleteData)} disabled={isPending} type="button">
            {isPending ? "Deleting…" : deleteData ? "Delete instance and data" : "Delete instance"}
          </button>
        </div>
      </div>
    </div>
  );
}
