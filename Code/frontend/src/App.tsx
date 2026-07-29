import AppRoutes from "./routes";

// Per 08_Frontend_Architecture.md Section 4, App only wires together
// providers and routing. It contains no business logic.
export default function App() {
  return <AppRoutes />;
}
