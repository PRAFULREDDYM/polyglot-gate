interface ScoreBadgeProps {
  label: string;
  score: number;
}

export function ScoreBadge({ label, score }: ScoreBadgeProps) {
  const level = score >= 0.7 ? "good" : score >= 0.5 ? "warn" : "bad";

  return (
    <span className={`score-badge ${level}`}>
      <span>{label}</span>
      <strong>{Math.round(score * 100)}%</strong>
    </span>
  );
}
