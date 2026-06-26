import { NavLink } from "react-router-dom";

const links = [
  { to: "/submit", label: "Submit Prompt" },
  { to: "/results", label: "Evaluation Results" },
  { to: "/moderation", label: "Moderation Flags" },
  { to: "/triage", label: "Triage Dashboard" }
];

export function NavBar() {
  return (
    <nav className="nav-bar" aria-label="Primary navigation">
      {links.map((link) => (
        <NavLink
          key={link.to}
          to={link.to}
          className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
        >
          {link.label}
        </NavLink>
      ))}
    </nav>
  );
}
