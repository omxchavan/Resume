import { Loader2 } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"

interface Job {
  id: number
  title: string
  company: string
  location: string
  matchScore: number
}

interface JobListProps {
  jobs: Job[]
  loading?: boolean
}

export function JobList({ jobs, loading }: JobListProps) {
  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    )
  }

  if (jobs.length === 0) {
    return <div className="text-center py-8 text-muted-foreground">No jobs found</div>
  }

  return (
    <div className="space-y-4">
      {jobs.map((job) => (
        <div key={job.id} className="rounded-lg border p-4 hover:bg-muted/50 transition-colors">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="font-semibold">{job.title}</h3>
              <p className="text-sm text-muted-foreground">{job.company}</p>
              <p className="text-sm text-muted-foreground">{job.location}</p>
            </div>
            <div className="text-right">
              <div className="text-sm font-medium">Match Score: {job.matchScore}%</div>
              <Progress value={job.matchScore} className="mt-2" />
            </div>
          </div>
          <div className="mt-4">
            <Button size="sm">View Details</Button>
          </div>
        </div>
      ))}
    </div>
  )
}

