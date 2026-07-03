import { useState } from "react";
import { Modal } from "../../components/ui/Modal";
import { Button } from "../../components/ui/Button";
import { SegmentedTabs } from "../../components/ui/SegmentedTabs";
import {
  ExerciseCategory,
  type MuscleGroup,
  type ExerciseOut,
} from "../../api/generated/quickfitApi.schemas";
import { MuscleGroupSelect } from "./MuscleGroupSelect";

export interface ExerciseFormValues {
  name: string;
  description: string | null;
  category: ExerciseCategory;
  muscle_group: MuscleGroup | null;
}

interface ExerciseFormModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (values: ExerciseFormValues) => void;
  isSubmitting: boolean;
  exercise?: ExerciseOut | null;
}

const inputClass =
  "border-border bg-surface-2 text-fg placeholder:text-faint focus:border-primary/50 focus-visible:ring-primary/40 h-11 w-full rounded-xl border px-3.5 focus:outline-none focus-visible:ring-2";

export function ExerciseFormModal({
  open,
  onClose,
  onSubmit,
  isSubmitting,
  exercise,
}: ExerciseFormModalProps) {
  const isEdit = !!exercise;
  const [name, setName] = useState(exercise?.name ?? "");
  const [description, setDescription] = useState(exercise?.description ?? "");
  const [category, setCategory] = useState<ExerciseCategory>(
    exercise?.category ?? ExerciseCategory.strength,
  );
  const [muscleGroup, setMuscleGroup] = useState<MuscleGroup | null>(
    exercise?.muscle_group ?? null,
  );

  const isStrength = category === ExerciseCategory.strength;
  const canSubmit =
    name.trim().length > 0 && (!isStrength || muscleGroup !== null);

  const handleSubmit = () => {
    if (!canSubmit) return;
    onSubmit({
      name: name.trim(),
      description: description.trim() || null,
      category,
      muscle_group: isStrength ? muscleGroup : null,
    });
  };

  return (
    <Modal open={open} onClose={onClose} labelledBy="exercise-form-title">
      <h2
        id="exercise-form-title"
        className="font-display text-fg text-2xl font-bold tracking-tight"
      >
        {isEdit ? "Edit exercise" : "New exercise"}
      </h2>

      <div className="mt-4 flex flex-col gap-4">
        <div>
          <label className="text-faint mb-1.5 block font-mono text-[11px] tracking-wide uppercase">
            Name
          </label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="e.g. Romanian Deadlift"
            className={inputClass}
            autoFocus
          />
        </div>

        <div>
          <label className="text-faint mb-1.5 block font-mono text-[11px] tracking-wide uppercase">
            Description (optional)
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Setup or cueing notes…"
            rows={2}
            className={`${inputClass} h-auto resize-none py-2.5`}
          />
        </div>

        <div>
          <label className="text-faint mb-1.5 block font-mono text-[11px] tracking-wide uppercase">
            Category
          </label>
          <SegmentedTabs
            tabs={[
              { id: ExerciseCategory.strength, label: "Strength" },
              { id: ExerciseCategory.cardio, label: "Cardio" },
            ]}
            active={category}
            onChange={(id) => setCategory(id as ExerciseCategory)}
          />
        </div>

        {isStrength && (
          <div>
            <label className="text-faint mb-1.5 block font-mono text-[11px] tracking-wide uppercase">
              Muscle group
            </label>
            <MuscleGroupSelect value={muscleGroup} onChange={setMuscleGroup} />
          </div>
        )}
      </div>

      <div className="mt-5 flex flex-col-reverse gap-2 sm:flex-row sm:justify-end">
        <Button variant="ghost" onClick={onClose}>
          Cancel
        </Button>
        <Button
          onClick={handleSubmit}
          disabled={!canSubmit}
          loading={isSubmitting}
        >
          {isEdit ? "Save changes" : "Create exercise"}
        </Button>
      </div>
    </Modal>
  );
}
