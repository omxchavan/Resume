"use client"

import { useEffect, useState } from "react"
import { toast } from "sonner"
import { Plus } from "lucide-react"
import Link from "next/link"

import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { JobPostingList } from "@/components/jobs/job-posting-list"

interface JobPosting {
  id: number
  title: string
  applications: number
  status: string
  createdAt: string
}

export function RecruiterDashboard() {
  const [jobPostings, setJobPostings] = useState<JobPosting[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchJobPostings()
  }, [])

  const fetchJobPostings = async () => {
    try {
      const response = await fetch("/api/jobs/postings")
      if (response.ok) {
        const data = await response.json()
        setJobPostings(data)
      }
    } catch (error) {
      toast.error("Failed to load job postings")
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="container py-8">
      <div className="grid gap-8">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold">Recruiter Dashboard</h1>
          <Link href="/jobs/post">
            <Button>
              <Plus className="mr-2 h-4 w-4" />
              Post New Job
            </Button>
          </Link>
        </div>

        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Your Job Postings</CardTitle>
              <CardDescription>Manage your active job listings</CardDescription>
            </CardHeader>
            <CardContent>
              <JobPostingList postings={jobPostings} loading={loading} />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  )
}

