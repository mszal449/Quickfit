import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useQueryClient } from "@tanstack/react-query";
import { Button } from "../../components/ui/Button";
import { Card, Eyebrow } from "../../components/ui/Card";
import { SegmentedTabs } from "../../components/ui/SegmentedTabs";
import { Skeleton } from "../../components/ui/Skeleton";
import { ConfirmDialog } from "../../components/ui/ConfirmDialog";
import { ChevronLeftIcon, PlusIcon } from "../../components/icons";
import { useToast } from "../../components/ui/useToast";
import { getErrorMessage } from "../../api/client";
import { useGetPlanGet } from "../../api/generated/plan/plan";
import {
  useGetSessionsGet,
  useCreateSessionPost,
  getGetSessionsGetQueryKey,
} from "../../api/generated/plan-session/plan-session";
import { SessionDraftEditor } from "./builder/SessionDraftEditor";
import { CreateSessionModal } from "./CreateSessionModal";
import { ExercisePickerModal } from "./builder/ExercisePickerModal";
import { newDraftExercise, toPrescription } from "./builder/prescriptionDraft";

export function PlanBuilderPage() {
  const { planId = "" } = useParams();
  const navigate = useNavigate();
  const toast = useToast();
  const queryClient = useQueryClient();

  const { data: plan, isLoading: planLoading } = useGetPlanGet(planId);
  const { data: sessionsPage, isLoading: sessionsLoading } = useGetSessionsGet(planId);
  const sessions = sessionsPage?.items ?? [];

  const [activeId, setActiveId] = useState<string | null>(null);
  const [dirty, setDirty] = useState(false);
  const [pendingId, setPendingId] = useState<string | null>(null);
  const [namingSession, setNamingSession] = useState(false);
  const [newSessionName, setNewSessionName] = useState<string | null>(null);

  const activeSession = sessions.find((s) => s.id === activeId) ?? sessions[0] ?? null;

  const createSession = useCreateSessionPost({
    mutation: {
      onSuccess: (session) => {
        queryClient.invalidateQueries({ queryKey: getGetSessionsGetQueryKey(planId) });
        setNewSessionName(null);
        setActiveId(session.id);
      },
      onError: (e) => toast.error(getErrorMessage(e)),
    },
  });

  const createSessionWithExercise = (exerciseId: string) => {
    if (newSessionName === null) return;
    createSession.mutate({
      planId,
      data: {
        name: newSessionName,
        prescription: toPrescription([newDraftExercise(exerciseId)]),
      },
    });
  };

  const selectSession = (id: string) => {
    if (id === activeSession?.id) return;
    if (dirty) setPendingId(id);
    else setActiveId(id);
  };

  if (planLoading || sessionsLoading) {
    return (
      <div className="mx-auto max-w-2xl">
        <Skeleton className="mb-5 h-9 w-48" />
        <Skeleton className="mb-5 h-10 w-full" />
        <Skeleton className="h-40 w-full rounded-2xl" />
      </div>
    );
  }

  if (!plan) {
    return (
      <Card className="text-muted p-10 text-center">
        Plan not found.
        <div className="mt-3">
          <Button variant="secondary" onClick={() => navigate("/plans")}>
            Back to plans
          </Button>
        </div>
      </Card>
    );
  }

  return (
    <div className="mx-auto max-w-2xl">
      <button
        onClick={() => navigate("/plans")}
        className="text-muted hover:text-fg mb-3 flex cursor-pointer items-center gap-1 text-sm font-medium"
      >
        <ChevronLeftIcon size={18} /> Plans
      </button>

      <div className="mb-5">
        <Eyebrow className="mb-1 block">Edit plan</Eyebrow>
        <h1 className="font-display text-fg text-3xl font-bold tracking-tight">{plan.name}</h1>
        {plan.description && <p className="text-faint mt-1 text-sm">{plan.description}</p>}
      </div>

      {sessions.length === 0 ? (
        <Card className="flex flex-col items-center gap-3 p-10 text-center">
          <p className="text-muted">This plan has no sessions yet.</p>
          <Button iconLeft={<PlusIcon size={18} />} onClick={() => setNamingSession(true)}>
            Add a session
          </Button>
        </Card>
      ) : (
        <>
          <div className="mb-5 flex items-center gap-2">
            <SegmentedTabs
              className="min-w-0 flex-1"
              tabs={sessions.map((s) => ({ id: s.id, label: s.name }))}
              active={activeSession!.id}
              onChange={selectSession}
            />
            <button
              type="button"
              aria-label="Add session"
              onClick={() => setNamingSession(true)}
              className="border-border bg-surface-2 text-muted hover:text-fg flex h-10 w-10 shrink-0 cursor-pointer items-center justify-center rounded-lg border"
            >
              <PlusIcon size={18} />
            </button>
          </div>

          <SessionDraftEditor
            key={activeSession!.id}
            planId={planId}
            session={activeSession!}
            onDirtyChange={setDirty}
          />
        </>
      )}

      <ConfirmDialog
        open={pendingId !== null}
        title="Discard unsaved changes?"
        description="You have unsaved edits to this session. Switching will lose them."
        confirmLabel="Discard"
        destructive
        onConfirm={() => {
          if (pendingId) setActiveId(pendingId);
          setPendingId(null);
        }}
        onClose={() => setPendingId(null)}
      />

      <CreateSessionModal
        key={namingSession ? "naming-open" : "naming-closed"}
        open={namingSession}
        onClose={() => setNamingSession(false)}
        onContinue={(name) => {
          setNamingSession(false);
          setNewSessionName(name);
        }}
      />

      <ExercisePickerModal
        open={newSessionName !== null}
        onClose={() => setNewSessionName(null)}
        onPick={createSessionWithExercise}
        usedIds={[]}
      />
    </div>
  );
}
