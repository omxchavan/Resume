"use client"

import { useEffect, useState } from "react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"

interface Job {
  id: number
  title: string
  company: string
  description: string
  matchScore: number
}

interface Application {
  id: number
  jobId: number
  status: string
  appliedAt: string
}

export default function CandidateDashboard() {
  const [recommendedJobs, setRecommendedJobs] = useState<Job[]>([])
  const [applications, setApplications] = useState<Application[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    try {
      const [jobsRes, applicationsRes] = await Promise.all([fetch("/api/jobs/recommended"), fetch("/api/applications")])

      if (jobsRes.ok && applicationsRes.ok) {
        const [jobs, apps] = await Promise.all([jobsRes.json(), applicationsRes.json()])
        setRecommendedJobs(jobs)
        setApplications(apps)
      }
    } catch (error) {
      toast.error("Failed to load dashboard data")
    } finally {
      setLoading(false)
    }
  }

  const handleApply = async (jobId: number) => {
    try {
      const res = await fetch(`/api/jobs/${jobId}/apply`, {
        method: "POST",
      })
      if (res.ok) {
        toast.success("Application submitted successfully")
        fetchDashboardData()
      }
    } catch (error) {
      toast.error("Failed to submit application")
    }
  }

  if (loading) {
    return <div>Loading...</div>
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Candidate Dashboard</h1>

      <div className="grid md:grid-cols-2 gap-6">
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Recommended Jobs</h2>
          <div className="space-y-4">
            {recommendedJobs.map((job) => (
              <div key={job.id} className="border p-4 rounded-lg">
                <h3 className="font-semibold">{job.title}</h3>
                <p className="text-sm text-gray-600">{job.company}</p>
                <p className="text-sm mt-2">{job.description}</p>
                <div className="mt-4 flex items-center justify-between">
                  <span className="text-sm">Match Score: {job.matchScore}%</span>
                  <Button onClick={() => handleApply(job.id)}>Apply Now</Button>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Your Applications</h2>
          <div className="space-y-4">
            {applications.map((app) => (
              <div key={app.id} className="border p-4 rounded-lg">
                <div className="flex justify-between items-center">
                  <div>
                    <p className="font-medium">Application #{app.id}</p>
                    <p className="text-sm text-gray-600">Applied: {new Date(app.appliedAt).toLocaleDateString()}</p>
                  </div>
                  <span className="px-3 py-1 rounded-full text-sm bg-primary/10">{app.status}</span>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>
    </div>
  )
}

