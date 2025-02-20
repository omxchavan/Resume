"use client"

import { useEffect, useState } from "react"
import { toast } from "sonner"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import Link from "next/link"

interface JobPosting {
  id: number
  title: string
  description: string
  status: string
  applicants: number
  createdAt: string
}

export default function RecruiterDashboard() {
  const [jobPostings, setJobPostings] = useState<JobPosting[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchJobPostings()
  }, [])

  const fetchJobPostings = async () => {
    try {
      const res = await fetch("/api/jobs/postings")
      if (res.ok) {
        const data = await res.json()
        setJobPostings(data)
      }
    } catch (error) {
      toast.error("Failed to load job postings")
    } finally {
      setLoading(false)
    }
  }

  const handleStatusChange = async (jobId: number, newStatus: string) => {
    try {
      const res = await fetch(`/api/jobs/${jobId}/status`, {
        method: "PATCH",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ status: newStatus }),
      })
      if (res.ok) {
        toast.success("Job status updated")
        fetchJobPostings()
      }
    } catch (error) {
      toast.error("Failed to update job status")
    }
  }

  if (loading) {
    return <div>Loading...</div>
  }

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">Recruiter Dashboard</h1>
        <Link href="/jobs/post">
          <Button>Post New Job</Button>
        </Link>
      </div>

      <Card className="p-6">
        <h2 className="text-xl font-semibold mb-4">Your Job Postings</h2>
        <div className="space-y-4">
          {jobPostings.map((job) => (
            <div key={job.id} className="border p-4 rounded-lg">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="font-semibold">{job.title}</h3>
                  <p className="text-sm text-gray-600">Posted: {new Date(job.createdAt).toLocaleDateString()}</p>
                  <p className="text-sm text-gray-600">Applicants: {job.applicants}</p>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    onClick={() => handleStatusChange(job.id, job.status === "active" ? "closed" : "active")}
                  >
                    {job.status === "active" ? "Close" : "Reopen"}
                  </Button>
                  <Link href={`/jobs/${job.id}/applications`}>
                    <Button variant="secondary">View Applications</Button>
                  </Link>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  )
}

