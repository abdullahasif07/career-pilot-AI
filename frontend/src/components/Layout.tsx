import { NavLink, Outlet } from "react-router-dom";

const navItems = [
  { to: "/", label: "Dashboard", end: true },
  { to: "/profile", label: "Knowledge Base", end: false },
];

export default function Layout() {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="sidebar__brand">
          <span className="sidebar__logo" aria-hidden="true">
            CP
          </span>
          <div>
            <p className="sidebar__title">CareerPilot</p>
            <p className="sidebar__phase">Phase 1</p>
          </div>
        </div>

        <nav className="sidebar__nav" aria-label="Main navigation">
          {navItems.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `sidebar__link${isActive ? " sidebar__link--active" : ""}`
              }
            >
              {item.label}
            </NavLink>
          ))}
        </nav>

        <p className="sidebar__footnote">
          Your personal knowledge base powers tailored applications.
        </p>
      </aside>

      <div className="app-shell__main">
        <Outlet />
      </div>
    </div>
  );
}
