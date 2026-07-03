import { Link } from "react-router-dom";
import { Card } from "../../../components/ui/Card";
import { Tag } from "../../../components/ui/Tag";
import { Menu } from "../../../components/ui/Menu";
import {
  ArrowRightIcon,
  LinkIcon,
  MoreIcon,
  CloseIcon,
} from "../../../components/icons";
import { PlanVisibility } from "../../../api/generated/quickfitApi.schemas";
import type { PlanWithSessions } from "../usePlansWithSessions";

interface PlanCardProps {
  plan: PlanWithSessions;
  onDelete?: () => void;
}

const MAX_VISIBLE_SESSIONS = 3;

/** Plan summary tile in the plans list; links to the builder. Every card has the
 * same height regardless of content — each region reserves fixed/min space. */
export function PlanCard({ plan, onDelete }: PlanCardProps) {
  const sessionCount = plan.sessions.length;
  const visibleSessions = plan.sessions.slice(0, MAX_VISIBLE_SESSIONS);
  const hiddenCount = sessionCount - visibleSessions.length;

  return (
    <div className="relative">
      <Link
        to={`/plans/${plan.id}`}
        draggable={false}
        onDragStart={(e) => e.preventDefault()}
        className="group focus-visible:ring-primary/70 block rounded-2xl select-none focus-visible:ring-2 focus-visible:outline-none"
      >
        <Card className="group-hover:border-border-strong flex h-full flex-col p-5 transition-colors">
          <div className="flex items-start gap-2 pr-9">
            <h2 className="font-display text-fg min-w-0 flex-1 truncate text-xl font-bold tracking-tight">
              {plan.name}
            </h2>
            {plan.visibility === PlanVisibility.shared && (
              <Tag tone="primary">
                <LinkIcon size={12} /> Shared
              </Tag>
            )}
          </div>

          <p className="text-muted mt-2 line-clamp-2 min-h-10 text-sm">
            {plan.description}
          </p>

          <div className="mt-1 flex min-h-7 flex-wrap items-start gap-1.5">
            {visibleSessions.map((s) => (
              <Tag key={s.id} tone="muted">
                {s.name}
              </Tag>
            ))}
            {hiddenCount > 0 && <Tag tone="muted">+{hiddenCount}</Tag>}
          </div>

          <div className="border-border mt-4 flex items-center justify-between border-t pt-3 text-sm">
            <span className="text-faint font-mono text-xs">
              {sessionCount} session{sessionCount === 1 ? "" : "s"}
            </span>
            <span className="text-primary flex items-center gap-1 font-semibold">
              Edit plan
              <ArrowRightIcon
                size={16}
                className="transition-transform group-hover:translate-x-0.5"
              />
            </span>
          </div>
        </Card>
      </Link>

      {onDelete && (
        <Menu
          className="absolute top-3 right-3"
          label={`Actions for ${plan.name}`}
          trigger={<MoreIcon size={18} />}
          items={[
            {
              label: "Delete plan",
              icon: <CloseIcon size={16} />,
              destructive: true,
              onSelect: onDelete,
            },
          ]}
        />
      )}
    </div>
  );
}
