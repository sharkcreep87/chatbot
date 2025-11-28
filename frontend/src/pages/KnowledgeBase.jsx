import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { knowledgeBaseAPI } from '@/services/api';
import toast from 'react-hot-toast';
import {
  Plus,
  Trash2,
  Upload,
  FileText,
  Database,
  Loader2,
  Search,
  CheckCircle,
  XCircle,
  Clock
} from 'lucide-react';
import { format } from 'date-fns';

export function KnowledgeBase() {
  const queryClient = useQueryClient();
  const [selectedKB, setSelectedKB] = useState(null);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [showUploadDialog, setShowUploadDialog] = useState(false);
  const [newKBName, setNewKBName] = useState('');
  const [newKBDesc, setNewKBDesc] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);

  // Fetch knowledge bases
  const { data: knowledgeBases = [] } = useQuery({
    queryKey: ['knowledge-bases'],
    queryFn: async () => {
      const response = await knowledgeBaseAPI.getKnowledgeBases();
      return response.data;
    },
  });

  // Fetch documents for selected KB
  const { data: documents = [], isLoading: documentsLoading } = useQuery({
    queryKey: ['documents', selectedKB],
    queryFn: async () => {
      if (!selectedKB) return [];
      const response = await knowledgeBaseAPI.getDocuments(selectedKB);
      return response.data;
    },
    enabled: !!selectedKB,
  });

  // Create KB mutation
  const createKBMutation = useMutation({
    mutationFn: (data) => knowledgeBaseAPI.createKnowledgeBase(data),
    onSuccess: () => {
      queryClient.invalidateQueries(['knowledge-bases']);
      setShowCreateDialog(false);
      setNewKBName('');
      setNewKBDesc('');
      toast.success('Knowledge base created!');
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to create knowledge base');
    },
  });

  // Delete KB mutation
  const deleteKBMutation = useMutation({
    mutationFn: (id) => knowledgeBaseAPI.deleteKnowledgeBase(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['knowledge-bases']);
      if (selectedKB === deleteKBMutation.variables) {
        setSelectedKB(null);
      }
      toast.success('Knowledge base deleted');
    },
  });

  // Upload document mutation
  const uploadMutation = useMutation({
    mutationFn: ({ kbId, file }) => knowledgeBaseAPI.uploadDocument(kbId, file),
    onSuccess: () => {
      queryClient.invalidateQueries(['documents', selectedKB]);
      setShowUploadDialog(false);
      setSelectedFile(null);
      toast.success('Document uploaded and processed!');
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to upload document');
    },
  });

  // Delete document mutation
  const deleteDocMutation = useMutation({
    mutationFn: (id) => knowledgeBaseAPI.deleteDocument(id),
    onSuccess: () => {
      queryClient.invalidateQueries(['documents', selectedKB]);
      toast.success('Document deleted');
    },
  });

  const handleCreateKB = () => {
    if (!newKBName.trim()) {
      toast.error('Please enter a name');
      return;
    }
    createKBMutation.mutate({
      name: newKBName,
      description: newKBDesc,
    });
  };

  const handleUpload = () => {
    if (!selectedFile) {
      toast.error('Please select a file');
      return;
    }
    uploadMutation.mutate({ kbId: selectedKB, file: selectedFile });
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 0: return <Clock className="h-4 w-4 text-yellow-500" />;
      case 1: return <Loader2 className="h-4 w-4 text-blue-500 animate-spin" />;
      case 2: return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 3: return <XCircle className="h-4 w-4 text-red-500" />;
      default: return null;
    }
  };

  const getStatusText = (status) => {
    switch (status) {
      case 0: return 'Pending';
      case 1: return 'Processing';
      case 2: return 'Completed';
      case 3: return 'Failed';
      default: return 'Unknown';
    }
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold">Knowledge Base</h1>
            <p className="text-muted-foreground mt-1">
              Upload and manage your documents
            </p>
          </div>
          <Button onClick={() => setShowCreateDialog(true)}>
            <Plus className="h-4 w-4 mr-2" />
            New Knowledge Base
          </Button>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Knowledge Bases List */}
          <Card className="lg:col-span-1">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Database className="h-5 w-5" />
                Your Knowledge Bases
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-2">
              {knowledgeBases.map((kb) => (
                <div
                  key={kb.id}
                  className={`p-3 rounded-lg border cursor-pointer transition-colors group ${
                    selectedKB === kb.id
                      ? 'bg-accent border-primary'
                      : 'hover:bg-accent/50'
                  }`}
                  onClick={() => setSelectedKB(kb.id)}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1 min-w-0">
                      <p className="font-medium truncate">{kb.name}</p>
                      {kb.description && (
                        <p className="text-xs text-muted-foreground truncate">
                          {kb.description}
                        </p>
                      )}
                      <p className="text-xs text-muted-foreground mt-1">
                        {format(new Date(kb.created_at), 'MMM d, yyyy')}
                      </p>
                    </div>
                    <Button
                      variant="ghost"
                      size="icon"
                      className="h-8 w-8 opacity-0 group-hover:opacity-100"
                      onClick={(e) => {
                        e.stopPropagation();
                        if (confirm('Delete this knowledge base?')) {
                          deleteKBMutation.mutate(kb.id);
                        }
                      }}
                    >
                      <Trash2 className="h-4 w-4 text-destructive" />
                    </Button>
                  </div>
                </div>
              ))}

              {knowledgeBases.length === 0 && (
                <p className="text-center text-muted-foreground py-8 text-sm">
                  No knowledge bases yet. Create one to get started!
                </p>
              )}
            </CardContent>
          </Card>

          {/* Documents List */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2">
                  <FileText className="h-5 w-5" />
                  Documents
                </CardTitle>
                {selectedKB && (
                  <Button onClick={() => setShowUploadDialog(true)} size="sm">
                    <Upload className="h-4 w-4 mr-2" />
                    Upload PDF
                  </Button>
                )}
              </div>
            </CardHeader>
            <CardContent>
              {!selectedKB ? (
                <p className="text-center text-muted-foreground py-12">
                  Select a knowledge base to view documents
                </p>
              ) : documentsLoading ? (
                <div className="flex items-center justify-center py-12">
                  <Loader2 className="h-8 w-8 animate-spin text-primary" />
                </div>
              ) : documents.length === 0 ? (
                <p className="text-center text-muted-foreground py-12">
                  No documents yet. Upload a PDF to get started!
                </p>
              ) : (
                <div className="space-y-3">
                  {documents.map((doc) => (
                    <div
                      key={doc.id}
                      className="flex items-center justify-between p-4 border rounded-lg hover:bg-accent/50 transition-colors group"
                    >
                      <div className="flex items-start gap-3 flex-1">
                        <FileText className="h-5 w-5 text-primary mt-1" />
                        <div className="flex-1 min-w-0">
                          <p className="font-medium truncate">{doc.filename}</p>
                          <div className="flex items-center gap-3 text-xs text-muted-foreground mt-1">
                            <span>{(doc.file_size / 1024).toFixed(1)} KB</span>
                            <span>•</span>
                            <span>{format(new Date(doc.created_at), 'MMM d, yyyy')}</span>
                            <span>•</span>
                            <div className="flex items-center gap-1">
                              {getStatusIcon(doc.processed)}
                              <span>{getStatusText(doc.processed)}</span>
                            </div>
                          </div>
                          {doc.metadata?.num_pages && (
                            <p className="text-xs text-muted-foreground mt-1">
                              {doc.metadata.num_pages} pages
                            </p>
                          )}
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="icon"
                        className="opacity-0 group-hover:opacity-100"
                        onClick={() => {
                          if (confirm('Delete this document?')) {
                            deleteDocMutation.mutate(doc.id);
                          }
                        }}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Create KB Dialog */}
        {showCreateDialog && (
          <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <Card className="w-full max-w-md">
              <CardHeader>
                <CardTitle>Create Knowledge Base</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Name</label>
                  <Input
                    placeholder="My Knowledge Base"
                    value={newKBName}
                    onChange={(e) => setNewKBName(e.target.value)}
                    className="mt-1"
                  />
                </div>
                <div>
                  <label className="text-sm font-medium">Description (Optional)</label>
                  <Input
                    placeholder="Description"
                    value={newKBDesc}
                    onChange={(e) => setNewKBDesc(e.target.value)}
                    className="mt-1"
                  />
                </div>
                <div className="flex gap-2 justify-end">
                  <Button variant="outline" onClick={() => setShowCreateDialog(false)}>
                    Cancel
                  </Button>
                  <Button
                    onClick={handleCreateKB}
                    disabled={createKBMutation.isPending}
                  >
                    {createKBMutation.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Creating...
                      </>
                    ) : (
                      'Create'
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Upload Dialog */}
        {showUploadDialog && (
          <div className="fixed inset-0 bg-background/80 backdrop-blur-sm z-50 flex items-center justify-center p-4">
            <Card className="w-full max-w-md">
              <CardHeader>
                <CardTitle>Upload PDF Document</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <label className="text-sm font-medium">Select PDF File</label>
                  <Input
                    type="file"
                    accept=".pdf"
                    onChange={(e) => setSelectedFile(e.target.files[0])}
                    className="mt-1"
                  />
                  {selectedFile && (
                    <p className="text-sm text-muted-foreground mt-2">
                      {selectedFile.name} ({(selectedFile.size / 1024).toFixed(1)} KB)
                    </p>
                  )}
                </div>
                <div className="flex gap-2 justify-end">
                  <Button
                    variant="outline"
                    onClick={() => {
                      setShowUploadDialog(false);
                      setSelectedFile(null);
                    }}
                  >
                    Cancel
                  </Button>
                  <Button
                    onClick={handleUpload}
                    disabled={uploadMutation.isPending || !selectedFile}
                  >
                    {uploadMutation.isPending ? (
                      <>
                        <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                        Uploading...
                      </>
                    ) : (
                      <>
                        <Upload className="h-4 w-4 mr-2" />
                        Upload
                      </>
                    )}
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        )}
      </div>
    </div>
  );
}
