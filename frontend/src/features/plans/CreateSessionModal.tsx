import { useState } from "react";
import { Modal } from "../../components/ui/Modal";
import { Button } from "../../components/ui/Button";

interface CreateSessionModalProps {
  open: boolean;
  onClose: () => void;
  onContinue: (name: string) => void;
}

export function CreateSessionModal({ open, onClose, onContinue }: CreateSessionModalProps) {
  const [name, setName] = useState("");
  const canContinue = name.trim().length > 0;

  return (
    <Modal open={open} onClose={onClose} labelledBy="create-session-title">
      <h2
        id="create-session-title"
        className="font-display text-fg text-2xl font-bold tracking-tight"
      >
        New session
      </h2>
      <p className="text-muted mt-1 text-sm">Name the day, then pick its first exercise.</p>

      <div className="mt-4">
        <label className="text-faint mb-1.5 block font-mono text-[11px] tracking-wide uppercase">
          Name
        </label>
        <input
          value={name}
          onChange={(e) => setName(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && canContinue && onContinue(name.trim())}
          placeholder="e.g. Lower A"
          autoFocus
          className="border-border bg-surface-2 text-fg placeholder:text-faint focus:border-primary/50 focus-visible:ring-primary/40 h-11 w-full rounded-xl border px-3.5 focus:outline-none focus-visible:ring-2"
        />
      </div>

      <div className="mt-5 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <Button variant="ghost" onClick={onClose}>
          Cancel
        </Button>
        <Button onClick={() => onContinue(name.trim())} disabled={!canContinue}>
          Pick first exercise
        </Button>
      </div>
    </Modal>
  );
}
