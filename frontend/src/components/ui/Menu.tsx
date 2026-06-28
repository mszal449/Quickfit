import { useEffect, useLayoutEffect, useRef, useState, type ReactNode } from "react";
import { createPortal } from "react-dom";
import { cn } from "../../lib/cn";

interface MenuItem {
  label: string;
  icon?: ReactNode;
  onSelect: () => void;
  destructive?: boolean;
}

interface MenuProps {
  trigger: ReactNode;
  items: MenuItem[];
  align?: "left" | "right";
  side?: "top" | "bottom";
  label?: string;
  triggerClassName?: string;
  className?: string;
}

/**
 * Lightweight dropdown menu (no dependency). Closes on outside-click and Escape,
 * exposes role="menu"/"menuitem". Used for contextual actions like the
 * in-progress session's finish/discard overflow.
 */
interface Coords {
  top?: number;
  bottom?: number;
  left?: number;
  right?: number;
}

const GAP = 4;

export function Menu({
  trigger,
  items,
  align = "right",
  side = "bottom",
  label = "Open menu",
  triggerClassName,
  className,
}: MenuProps) {
  const [open, setOpen] = useState(false);
  const [coords, setCoords] = useState<Coords | null>(null);
  const wrapperRef = useRef<HTMLDivElement>(null);
  const menuRef = useRef<HTMLDivElement>(null);

  const reposition = () => {
    const rect = wrapperRef.current?.getBoundingClientRect();
    if (!rect) return;
    setCoords({
      ...(side === "top"
        ? { bottom: window.innerHeight - rect.top + GAP }
        : { top: rect.bottom + GAP }),
      ...(align === "right"
        ? { right: window.innerWidth - rect.right }
        : { left: rect.left }),
    });
  };

  useLayoutEffect(() => {
    if (!open) return;
    reposition();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  useEffect(() => {
    if (!open) return;
    const onClick = (e: MouseEvent) => {
      const target = e.target as Node;
      if (
        wrapperRef.current &&
        !wrapperRef.current.contains(target) &&
        menuRef.current &&
        !menuRef.current.contains(target)
      ) {
        setOpen(false);
      }
    };
    const onKey = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpen(false);
    };
    document.addEventListener("mousedown", onClick);
    document.addEventListener("keydown", onKey);
    window.addEventListener("scroll", reposition, true);
    window.addEventListener("resize", reposition);
    return () => {
      document.removeEventListener("mousedown", onClick);
      document.removeEventListener("keydown", onKey);
      window.removeEventListener("scroll", reposition, true);
      window.removeEventListener("resize", reposition);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [open]);

  return (
    <div ref={wrapperRef} className={className}>
      <button
        type="button"
        aria-haspopup="menu"
        aria-expanded={open}
        aria-label={label}
        onClick={() => setOpen((v) => !v)}
        className={cn(
          "text-muted hover:bg-surface-3 hover:text-fg focus-visible:ring-primary/70 flex cursor-pointer items-center justify-center rounded-lg transition-colors focus-visible:ring-2 focus-visible:outline-none",
          triggerClassName ?? "h-10 w-10",
        )}
      >
        {trigger}
      </button>

      {open &&
        coords &&
        createPortal(
          <div
            ref={menuRef}
            role="menu"
            style={coords}
            className="border-border bg-surface-2 fixed z-50 min-w-44 overflow-hidden rounded-xl border p-1 shadow-xl shadow-black/40"
          >
            {items.map((item) => (
              <button
                key={item.label}
                role="menuitem"
                onClick={() => {
                  setOpen(false);
                  item.onSelect();
                }}
                className={cn(
                  "flex w-full cursor-pointer items-center gap-2.5 rounded-lg px-3 py-2 text-left text-sm font-medium transition-colors",
                  item.destructive
                    ? "text-danger hover:bg-danger-soft"
                    : "text-fg hover:bg-surface-3",
                )}
              >
                {item.icon}
                {item.label}
              </button>
            ))}
          </div>,
          document.body,
        )}
    </div>
  );
}
