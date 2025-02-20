import { Loader2, MoreVertical } from "lucide-react"
import { Button } from "@/components/ui/button"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"
import { Badge } from "@/components/ui/badge"

interface JobPosting {
  id: number
  title: string
  applications: number
  status: string
  createdAt: string
}

interface JobPostingListProps {
  postings: JobPosting[]
  loading?: boolean
}

export function JobPostingList({ postings, loading }: JobPostingListProps) {
  if (loading) {
    return (
      <div className="flex justify-center py-8">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    )
  }

  if (postings.length === 0) {
    return <div className="text-center py-8 text-muted-foreground">No job postings yet</div>
  }

  return (
    <div className="space-y-4">
      {postings.map((posting) => (
        <div key={posting.id} className="rounded-lg border p-4 hover:bg-muted/50 transition-colors">
          <div className="flex items-start justify-between">
            <div>
              <h3 className="font-semibold">{posting.title}</h3>
              <p className="text-sm text-muted-foreground">{posting.applications} applications</p>
              <p className="text-sm text-muted-foreground">
                Posted on {new Date(posting.createdAt).toLocaleDateString()}
              </p>
            </div>
            <div className="flex items-center gap-2">
              <Badge variant={posting.status === "active" ? "success" : "secondary"}>{posting.status}</Badge>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button variant="ghost" size="icon">
                    <MoreVertical className="h-4 w-4" />
                    <span className="sr-only">Actions</span>
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem>View Applications</DropdownMenuItem>
                  <DropdownMenuItem>Edit Posting</DropdownMenuItem>
                  <DropdownMenuItem className="text-destructive">Delete Posting</DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

