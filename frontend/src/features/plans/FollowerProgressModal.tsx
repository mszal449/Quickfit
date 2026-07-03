import { Modal } from "../../components/ui/Modal";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Skeleton } from "../../components/ui/Skeleton";
import { useGetShareProgressGet } from "../../api/generated/plan-share/plan-share";
import { formatClock, formatTonnes, relativeTime } from "../../lib/format";

interface FollowerProgressModalProps {
  open: boolean;
  onClose: () => void;
  planShareId: string;
  followerEmail: string;
}

export function FollowerProgressModal({
  open,
  onClose,
  planShareId,
  followerEmail,
}: FollowerProgressModalProps) {
  const { data, isLoading } = useGetShareProgressGet(planShareId, {
    query: { enabled: open },
  });
  const logs = data?.items ?? [];

  return (
    <Modal open={open} onClose={onClose} labelledBy="follower-progress-title">
      <h2
        id="follower-progress-title"
        className="font-display text-fg text-2xl font-bold tracking-tight"
      >
        {followerEmail}'s progress
      </h2>

      <div className="mt-4 max-h-[60vh] overflow-y-auto">
        {isLoading ? (
          <div className="flex flex-col gap-2">
            {Array.from({ length: 3 }).map((_, i) => (
              <Skeleton key={i} className="h-16 w-full rounded-xl" />
            ))}
          </div>
        ) : logs.length === 0 ? (
          <Card className="text-muted p-6 text-center text-sm">
            No workouts logged yet.
          </Card>
        ) : (
          <div className="flex flex-col gap-2">
            {logs.map((log) => {
              const totalVolumeKg = log.sets.reduce((sum, s) => {
                if (s.weight != null && s.reps != null)
                  return sum + s.weight * s.reps;
                return sum;
              }, 0);
              const durationSeconds = log.completed_at
                ? (new Date(log.completed_at).getTime() -
                    new Date(log.started_at).getTime()) /
                  1000
                : null;

              return (
                <Card
                  key={log.id}
                  className="flex items-center justify-between gap-3 p-3"
                >
                  <div className="text-fg text-sm font-semibold">
                    {relativeTime(log.started_at)}
                  </div>
                  <div className="text-faint tabular flex gap-4 font-mono text-xs">
                    <span>
                      {durationSeconds != null
                        ? formatClock(durationSeconds)
                        : "—"}
                    </span>
                    <span>{log.sets.length} sets</span>
                    <span className="text-primary">
                      {formatTonnes(totalVolumeKg)}t
                    </span>
                  </div>
                </Card>
              );
            })}
          </div>
        )}
      </div>

      <div className="mt-5 flex justify-end">
        <Button variant="ghost" onClick={onClose}>
          Close
        </Button>
      </div>
    </Modal>
  );
}
