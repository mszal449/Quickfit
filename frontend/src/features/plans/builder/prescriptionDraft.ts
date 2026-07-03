import type {
  SessionPrescription,
  ExercisePrescription,
  SetPrescription,
} from "../../../api/generated/quickfitApi.schemas";

export interface DraftSet {
  min_reps: number;
  max_reps: number | null;
}

export interface DraftExercise {
  uid: string;
  exercise_id: string;
  sets: DraftSet[];
  description: string | null;
}

let uidCounter = 0;
function nextUid(): string {
  uidCounter += 1;
  return `ex-${Date.now()}-${uidCounter}`;
}

export function newDraftSet(from?: DraftSet): DraftSet {
  return from ? { ...from } : { min_reps: 8, max_reps: 12 };
}

export function newDraftExercise(exerciseId: string): DraftExercise {
  return {
    uid: nextUid(),
    exercise_id: exerciseId,
    sets: [newDraftSet(), newDraftSet(), newDraftSet()],
    description: null,
  };
}

export function toDraft(prescription: SessionPrescription): DraftExercise[] {
  return prescription.exercises.map((ex) => ({
    uid: nextUid(),
    exercise_id: ex.exercise_id,
    sets: ex.sets.map((s) => ({
      min_reps: s.min_reps,
      max_reps: s.max_reps ?? null,
    })),
    description: ex.description ?? null,
  }));
}

export function toPrescription(draft: DraftExercise[]): SessionPrescription {
  return {
    exercises: draft.map<ExercisePrescription>((ex) => ({
      exercise_id: ex.exercise_id,
      sets: ex.sets.map<SetPrescription>((s) => ({
        min_reps: s.min_reps,
        max_reps: s.max_reps,
      })),
      description: ex.description,
    })),
  };
}

export function isDraftValid(draft: DraftExercise[]): boolean {
  return draft.length > 0 && draft.every((ex) => ex.sets.length > 0);
}

export function draftEquals(a: DraftExercise[], b: DraftExercise[]): boolean {
  if (a.length !== b.length) return false;
  return a.every((ex, i) => {
    const o = b[i];
    return (
      ex.exercise_id === o.exercise_id &&
      ex.description === o.description &&
      ex.sets.length === o.sets.length &&
      ex.sets.every(
        (s, j) =>
          s.min_reps === o.sets[j].min_reps &&
          s.max_reps === o.sets[j].max_reps,
      )
    );
  });
}
