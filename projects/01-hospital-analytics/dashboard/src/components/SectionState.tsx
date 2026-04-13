interface SectionStateProps {
  message: string;
  tone?: "loading" | "error" | "empty";
}

export function SectionState({ message, tone = "loading" }: SectionStateProps) {
  return <div className={`section-state section-state--${tone}`}>{message}</div>;
}

