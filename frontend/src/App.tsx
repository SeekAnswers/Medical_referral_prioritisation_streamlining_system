import { useState } from 'react'
import { useMutation } from 'react-query'
import axios from 'axios'

interface AnalysisResponse {
  llama: string
  llava: string
}

export default function App() {
  const [selectedImage, setSelectedImage] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string>('')
  const [query, setQuery] = useState('')

  const analysisMutation = useMutation<AnalysisResponse, Error, FormData>(
    async (formData) => {
      const response = await axios.post('http://localhost:8000/analyze', formData)
      return response.data
    }
  )

  const handleImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (file) {
      setSelectedImage(file)
      const reader = new FileReader()
      reader.onload = (e) => setImagePreview(e.target?.result as string)
      reader.readAsDataURL(file)
    }
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault()
    if (!selectedImage || !query) return

    const formData = new FormData()
    formData.append('image', selectedImage)
    formData.append('query', query)

    analysisMutation.mutate(formData)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 to-gray-800 text-gray-300">
      <div className="container mx-auto p-6">
        <div className="flex items-center justify-center mb-12">
          <h1 className="text-4xl font-bold text-purple-300 shadow-md">
            Medical Image Analysis
          </h1>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          {/* Upload Section */}
          <div className="bg-white/10 backdrop-blur-md p-6 rounded-xl shadow-lg border border-white/20">
            <h2 className="text-xl font-semibold text-purple-400 mb-4">
              Upload Image
            </h2>
            <input
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              className="hidden"
              id="image-upload"
            />
            <label
              htmlFor="image-upload"
              className="w-full py-3 bg-purple-500 hover:bg-purple-600 text-white font-bold rounded-md transition-all flex items-center justify-center cursor-pointer"
            >
              {selectedImage ? 'Change Image' : 'Select Image'}
            </label>
            {imagePreview && (
              <div className="mt-4">
                <img
                  src={imagePreview}
                  alt="Preview"
                  className="w-full rounded-lg shadow-lg"
                />
              </div>
            )}
          </div>

          {/* Query Section */}
          <div className="bg-white/10 backdrop-blur-md p-6 rounded-xl shadow-lg border border-white/20">
            <h2 className="text-xl font-semibold text-blue-400 mb-4">
              Ask Question
            </h2>
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your question about the image"
              className="w-full p-3 bg-gray-800 text-gray-300 rounded-lg shadow mb-4"
              rows={4}
            />
            <button
              onClick={handleSubmit}
              disabled={analysisMutation.isLoading || !selectedImage || !query}
              className="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-gray-500 text-white font-bold py-2 px-4 rounded-lg transition-all"
            >
              {analysisMutation.isLoading ? 'Analyzing...' : 'Analyze Image'}
            </button>
          </div>
        </div>

        {/* Results Section */}
        {(analysisMutation.data || analysisMutation.error) && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            {analysisMutation.data && (
              <>
                <div className="bg-white/10 backdrop-blur-md p-6 rounded-xl shadow-lg border border-white/20">
                  <h2 className="text-xl font-semibold text-green-400 mb-4">
                    Llama Analysis
                  </h2>
                  <div className="prose prose-invert">
                    {analysisMutation.data.llama}
                  </div>
                </div>
                <div className="bg-white/10 backdrop-blur-md p-6 rounded-xl shadow-lg border border-white/20">
                  <h2 className="text-xl font-semibold text-green-400 mb-4">
                    Llava Analysis
                  </h2>
                  <div className="prose prose-invert">
                    {analysisMutation.data.llava}
                  </div>
                </div>
              </>
            )}
            {analysisMutation.error && (
              <div className="col-span-2 bg-red-500/10 border border-red-500 rounded-xl p-6">
                <h2 className="text-xl font-semibold text-red-400 mb-2">Error</h2>
                <p>{analysisMutation.error.message}</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
