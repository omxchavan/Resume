import PrivateRoute from "@/components/common/private-route"
import CandidateDashboard from "@/components/candidate/candidate-dashboard"
import RecruiterDashboard from "@/components/recruiter/recruiter-dashboard"

export default function DashboardPage() {
  return (
    <PrivateRoute>
      {({ user }) => (user?.userType === "candidate" ? <CandidateDashboard /> : <RecruiterDashboard />)}
    </PrivateRoute>
  )
}

