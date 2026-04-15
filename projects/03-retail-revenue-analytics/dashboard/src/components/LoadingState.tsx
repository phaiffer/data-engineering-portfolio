export function LoadingState({ message = "Loading data..." }: { message?: string }) {
  return (
    <div className="state state--loading" role="status">
      <span aria-hidden="true" />
      <p>{message}</p>
    </div>
  );
}
