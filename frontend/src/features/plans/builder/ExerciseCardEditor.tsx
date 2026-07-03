import type { PointerEvent } from "react";
import { Card } from "../../../components/ui/Card";
import { GripIcon, CloseIcon } from "../../../components/icons";
import { cn } from "../../../lib/cn";
import { SetsEditor } from "./SetsEditor";
import type { DraftExercise, DraftSet } from "./prescriptionDraft";

interface ExerciseCardEditorProps {
  exercise: DraftExercise;
  name: string;
  index: number;
  onChange: (exercise: DraftExercise) => void;
  onRemove: () => void;
  onHandlePointerDown: (e: PointerEvent) => void;
  isDragging: boolean;
  readOnly?: boolean;
}

export function ExerciseCardEditor({
  exercise,
  name,
  index,
  onChange,
  onRemove,
  onHandlePointerDown,
  isDragging,
  readOnly = false,
}: ExerciseCardEditorProps) {
  const setSets = (sets: DraftSet[]) => onChange({ ...exercise, sets });

  return (
    <Card
      className={cn(
        "p-3 transition-shadow sm:p-4",
        isDragging && "border-primary/50 shadow-2xl shadow-black/50",
      )}
    >
      <div className="mb-3 flex items-center gap-2">
        {!readOnly && (
          <button
            type="button"
            aria-label={`Reorder ${name}`}
            onPointerDown={onHandlePointerDown}
            className="text-faint hover:text-fg -ml-1 flex h-8 w-7 shrink-0 cursor-grab touch-none items-center justify-center active:cursor-grabbing"
          >
            <GripIcon size={18} />
          </button>
        )}

        <span className="bg-surface-3 text-muted flex h-6 w-6 shrink-0 items-center justify-center rounded-md font-mono text-xs font-semibold">
          {index + 1}
        </span>

        <h3 className="text-fg min-w-0 flex-1 truncate font-semibold">
          {name}
        </h3>

        {!readOnly && (
          <button
            type="button"
            aria-label={`Remove ${name}`}
            onClick={onRemove}
            className="text-faint hover:text-danger flex h-8 w-8 shrink-0 items-center justify-center rounded-lg"
          >
            <CloseIcon size={18} />
          </button>
        )}
      </div>

      <SetsEditor sets={exercise.sets} onChange={setSets} readOnly={readOnly} />
    </Card>
  );
}
