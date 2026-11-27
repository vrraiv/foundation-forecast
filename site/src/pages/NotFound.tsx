import { PAGES } from "../routes";

export function NotFound() {
  return (
    <div className="page">
      <div className="prose">
        <h1>Page not found</h1>
        <p>There is no page at this address. The pages of this site are:</p>
        <ul>
          {PAGES.map((p) => (
            <li key={p.id}>
              <a href={p.path}>{p.name}</a>
            </li>
          ))}
        </ul>
      </div>
    </div>
  );
}
