import { useEffect, useLayoutEffect, useRef, useState } from "react";
import { createPortal } from "react-dom";
import { ChevronDownIcon, CheckIcon } from "../../components/icons";
import { cn } from "../../lib/cn";
import { MuscleGroup } from "../../api/generated/quickfitApi.schemas";

const LABELS: Record<MuscleGroup, string> = {
  chest: "Chest",
  back: "Back",
  shoulders: "Shoulders",
  biceps: "Biceps",
  triceps: "Triceps",
  forearms: "Forearms",
  core: "Core",
  quads: "Quads",
  hamstrings: "Hamstrings",
  glutes: "Glutes",
  calves: "Calves",
  full_body: "Full body",
};

const GAP = 6;
const MAX_PANEL_HEIGHT = 256;
const MIN_PANEL_HEIGHT = 120;

interface Coords {
  left: number;
  width: number;
  maxHeight: number;
  top?: number;
  bottom?: number;
}

interface MuscleGroupSelectProps {
  value: MuscleGroup | null;
  onChange: (value: MuscleGroup) => void;
}

export function MuscleGroupSelect({ value, onChange }: MuscleGroupSelectProps) {
  const [open, setOpen] = useState(false);
  const [coords, setCoords] = useState<Coords | null>(null);
  const triggerRef = useRef<HTMLButtonElement>(null);
  const panelRef = useRef<HTMLDivElement>(null);

  useLayoutEffect(() => {
    if (!open) return;
    const rect = triggerRef.current?.getBoundingClientRect();
    if (!rect) return;
    const spaceBelow = window.innerHeight - rect.bottom - GAP;
    const spaceAbove = rect.top - GAP;
    const openUpward = spaceBelow < MIN_PANEL_HEIGHT && spaceAbove > spaceBelow;

    setCoords({
      left: rect.left,
      width: rect.width,
      maxHeight: Math.max(
        MIN_PANEL_HEIGHT,
        Math.min(MAX_PANEL_HEIGHT, openUpward ? spaceAbove : spaceBelow),
      ),
      ...(openUpward
        ? { bottom: window.innerHeight - rect.top + GAP }
        : { top: rect.bottom + GAP }),
    });
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const onClick = (e: MouseEvent) => {
      const target = e.target as Node;
      if (
        triggerRef.current &&
        !triggerRef.current.contains(target) &&
        panelRef.current &&
        !panelRef.current.contains(target)
      ) {
        setOpen(false);
      }
    };
    const onKey = (e: KeyboardEvent) => e.key === "Escape" && setOpen(false);
    document.addEventListener("mousedown", onClick);
    document.addEventListener("keydown", onKey);
    return () => {
      document.removeEventListener("mousedown", onClick);
      document.removeEventListener("keydown", onKey);
    };
  }, [open]);

  return (
    <>
      <button
        ref={triggerRef}
        type="button"
        aria-haspopup="listbox"
        aria-expanded={open}
        onClick={() => setOpen((v) => !v)}
        className="border-border bg-surface-2 text-fg focus-visible:ring-primary/40 flex h-11 w-full cursor-pointer items-center justify-between rounded-xl border px-3.5 text-left focus:outline-none focus-visible:ring-2"
      >
        <span className={value ? "text-fg" : "text-faint"}>
          {value ? LABELS[value] : "Select a muscle group…"}
        </span>
        <ChevronDownIcon size={18} className="text-faint shrink-0" />
      </button>

      {open &&
        coords &&
        createPortal(
          <div
            ref={panelRef}
            role="listbox"
            style={{
              top: coords.top,
              bottom: coords.bottom,
              left: coords.left,
              width: coords.width,
              maxHeight: coords.maxHeight,
            }}
            className="border-border bg-surface-2 fixed z-[110] overflow-y-auto rounded-xl border p-1 shadow-xl shadow-black/40"
          >
            {Object.values(MuscleGroup).map((mg) => {
              const isSelected = mg === value;
              return (
                <button
                  key={mg}
                  type="button"
                  role="option"
                  aria-selected={isSelected}
                  onClick={() => {
                    onChange(mg);
                    setOpen(false);
                  }}
                  className={cn(
                    "flex w-full cursor-pointer items-center justify-between rounded-lg px-3 py-2 text-left text-sm font-medium transition-colors",
                    isSelected
                      ? "text-primary bg-primary-soft"
                      : "text-fg hover:bg-surface-3",
                  )}
                >
                  {LABELS[mg]}
                  {isSelected && <CheckIcon size={16} />}
                </button>
              );
            })}
          </div>,
          document.body,
        )}
    </>
  );
}
