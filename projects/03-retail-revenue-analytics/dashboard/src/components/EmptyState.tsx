export function EmptyState({ message }: { message: string }) {
  return (
    <div className="state state--empty">
      <strong>No rows returned</strong>
      <p>{message}</p>
    </div>
  );
}
