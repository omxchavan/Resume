import { Loader2 } from "lucide-react"
import { Badge } from "@/components/ui/badge"

interface Application {
  id: number
  title: string
  company: string
  status: string
}

interface ApplicationListProps {
  applications: Application[]
  loading?: boolean
}

export function ApplicationList({ applications, loading }: ApplicationListProps) {
  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    )
  }

  if (applications.length === 0) {
    return <div className="text-center py-8 text-muted-foreground">No applications yet</div>
  }

  return (
    <div className="space-y-4">
      {applications.map((application) => (
        <div key={application.id} className="rounded-lg border p-4 hover:bg-muted/50 transition-colors">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="font-semibold">{application.title}</h3>
              <p className="text-sm text-muted-foreground">{application.company}</p>
            </div>
            <Badge
              variant={
                application.status === "pending"
                  ? "secondary"
                  : application.status === "accepted"
                    ? "success"
                    : "destructive"
              }
            >
              {application.status}
            </Badge>
          </div>
        </div>
      ))}
    </div>
  )
}

