import './App.css'
import { useHealthApiHealthGet } from './api/generated/health/health'

function App() {
  const { data, isLoading, error } = useHealthApiHealthGet()

  if (isLoading) return <p>Loading...</p>
  if (error) return <p>Error: {String(error)}</p>
  return <pre>{JSON.stringify(data)}</pre>

}

export default App
