"use client"

import { useEffect, useState } from "react"
import { toast } from "sonner"
import { Search } from "lucide-react"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { JobList } from "@/components/jobs/job-list"
import { ApplicationList } from "@/components/jobs/application-list"

interface Job {
  id: number
  title: string
  company: string
  location: string
  matchScore: number
  status: string
}

export function CandidateDashboard() {
  const [jobs, setJobs] = useState<Job[]>([])
  const [applications, setApplications] = useState<Job[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const [jobsRes, applicationsRes] = await Promise.all([fetch("/api/jobs/recommended"), fetch("/api/applications")])

      if (jobsRes.ok && applicationsRes.ok) {
        const [jobsData, applicationsData] = await Promise.all([jobsRes.json(), applicationsRes.json()])

        setJobs(jobsData)
        setApplications(applicationsData)
      }
    } catch (error) {
      toast.error("Failed to load dashboard data")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container py-8">
      <div className="grid gap-8">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Candidate Dashboard</h1>
          <Button>
            <Search className="mr-2 h-4 w-4" />
            Search Jobs
          </Button>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          <Card>
            <CardHeader>
              <CardTitle>Recommended Jobs</CardTitle>
              <CardDescription>Jobs matching your profile</CardDescription>
            </CardHeader>
            <CardContent>
              <JobList jobs={jobs} loading={loading} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Your Applications</CardTitle>
              <CardDescription>Track your job applications</CardDescription>
            </CardHeader>
            <CardContent>
              <ApplicationList applications={applications} loading={loading} />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

