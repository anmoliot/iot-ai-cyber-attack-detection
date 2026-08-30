import { AuthWrapper } from './AuthWrapper';
import { DashboardShell } from './DashboardShell';
import './tokens.css';

function App() {
  return (
    <AuthWrapper>
      <DashboardShell />
    </AuthWrapper>
  );
}

export default App;
