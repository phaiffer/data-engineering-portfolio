import type { ReactNode } from "react";

export function SectionCard({
  title,
  eyebrow,
  description,
  children,
  action,
}: {
  title: string;
  eyebrow?: string;
  description: string;
  children: ReactNode;
  action?: ReactNode;
}) {
  return (
    <section className="section-card" aria-labelledby={`${title.replace(/\W+/g, "-")}-heading`}>
      <div className="section-card__header">
        <div>
          {eyebrow ? <span className="eyebrow">{eyebrow}</span> : null}
          <h2 id={`${title.replace(/\W+/g, "-")}-heading`}>{title}</h2>
          <p>{description}</p>
        </div>
        {action ? <div className="section-card__action">{action}</div> : null}
      </div>
      {children}
    </section>
  );
}
