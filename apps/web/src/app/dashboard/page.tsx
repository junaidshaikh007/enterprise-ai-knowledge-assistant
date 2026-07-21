import { DocumentUpload } from "@/components/DocumentUpload";

export default function DashboardPage() {
  return (
    <div className="flex flex-col flex-1 p-8 bg-zinc-50 min-h-screen">
      <h1 className="text-3xl font-bold text-gray-800 mb-8">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <h2 className="text-xl font-semibold text-gray-700 mb-4">Knowledge Base</h2>
          <p className="text-gray-500 mb-6">
            Upload documents (PDF, TXT, DOCX) to expand the AI's knowledge base. 
            These documents will be parsed and embedded for retrieval.
          </p>
          <DocumentUpload />
        </div>
        
        <div>
          <h2 className="text-xl font-semibold text-gray-700 mb-4">Recent Documents</h2>
          <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
            <p className="text-gray-500 italic text-sm">No documents uploaded yet.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
