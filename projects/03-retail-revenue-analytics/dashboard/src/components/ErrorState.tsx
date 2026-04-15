export function ErrorState({ message }: { message: string }) {
  return (
    <div className="state state--error" role="alert">
      <strong>Unable to load this section</strong>
      <p>{message}</p>
    </div>
  );
}
