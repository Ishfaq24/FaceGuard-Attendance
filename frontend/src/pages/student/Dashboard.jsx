export default function StudentDashboard() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Student Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div className="glassmorphism rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Attendance Status</h2>
          <p className="text-3xl font-bold text-blue-500">92%</p>
        </div>
      </div>
    </div>
  )
}
