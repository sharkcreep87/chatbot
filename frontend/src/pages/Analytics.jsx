import { useQuery } from '@tanstack/react-query';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { analyticsAPI } from '@/services/api';
import {
  MessageSquare,
  Zap,
  TrendingUp,
  Database,
  FileText,
  Activity
} from 'lucide-react';
import { format } from 'date-fns';

export function Analytics() {
  const { data: analytics, isLoading } = useQuery({
    queryKey: ['analytics'],
    queryFn: async () => {
      const response = await analyticsAPI.getAnalytics(30);
      return response.data;
    },
  });

  const { data: kbAnalytics } = useQuery({
    queryKey: ['kb-analytics'],
    queryFn: async () => {
      const response = await analyticsAPI.getKnowledgeBaseAnalytics();
      return response.data;
    },
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="text-lg">Loading analytics...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Analytics Dashboard</h1>
            <p className="text-muted-foreground mt-1">
              Track your usage and insights
            </p>
          </div>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Conversations</p>
                  <p className="text-3xl font-bold mt-2">
                    {analytics?.total_conversations || 0}
                  </p>
                </div>
                <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                  <MessageSquare className="h-6 w-6 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Total Messages</p>
                  <p className="text-3xl font-bold mt-2">
                    {analytics?.total_messages || 0}
                  </p>
                </div>
                <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                  <Activity className="h-6 w-6 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Tokens Used</p>
                  <p className="text-3xl font-bold mt-2">
                    {(analytics?.total_tokens_used || 0).toLocaleString()}
                  </p>
                </div>
                <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                  <Zap className="h-6 w-6 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardContent className="p-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Avg Messages/Conv</p>
                  <p className="text-3xl font-bold mt-2">
                    {analytics?.conversation_stats?.avg_messages || 0}
                  </p>
                </div>
                <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                  <TrendingUp className="h-6 w-6 text-primary" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Knowledge Base Stats */}
        {kbAnalytics && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Knowledge Bases</p>
                    <p className="text-3xl font-bold mt-2">
                      {kbAnalytics.total_knowledge_bases || 0}
                    </p>
                  </div>
                  <Database className="h-8 w-8 text-primary" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Documents</p>
                    <p className="text-3xl font-bold mt-2">
                      {kbAnalytics.total_documents || 0}
                    </p>
                  </div>
                  <FileText className="h-8 w-8 text-primary" />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm text-muted-foreground">Storage Used</p>
                    <p className="text-3xl font-bold mt-2">
                      {kbAnalytics.total_size_mb || 0} MB
                    </p>
                  </div>
                  <Database className="h-8 w-8 text-primary" />
                </div>
              </CardContent>
            </Card>
          </div>
        )}

        {/* Activity Chart */}
        <Card>
          <CardHeader>
            <CardTitle>Message Activity (Last 30 Days)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="h-64 flex items-end justify-between gap-2">
              {analytics?.messages_by_day?.map((day, index) => {
                const maxCount = Math.max(...analytics.messages_by_day.map(d => d.count), 1);
                const height = (day.count / maxCount) * 100;

                return (
                  <div key={index} className="flex-1 flex flex-col items-center group">
                    <div
                      className="w-full bg-primary rounded-t transition-all hover:bg-primary/80"
                      style={{ height: `${height}%`, minHeight: day.count > 0 ? '4px' : '0' }}
                      title={`${format(new Date(day.date), 'MMM d')}: ${day.count} messages`}
                    />
                    <p className="text-xs text-muted-foreground mt-2 opacity-0 group-hover:opacity-100 transition-opacity">
                      {day.count}
                    </p>
                  </div>
                );
              })}
            </div>
            <div className="flex justify-between mt-4 text-xs text-muted-foreground">
              <span>{analytics?.messages_by_day?.[0]?.date}</span>
              <span>{analytics?.messages_by_day?.[analytics.messages_by_day.length - 1]?.date}</span>
            </div>
          </CardContent>
        </Card>

        {/* Model Usage & Recent Activity */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Model Usage */}
          <Card>
            <CardHeader>
              <CardTitle>Model Usage</CardTitle>
            </CardHeader>
            <CardContent>
              {analytics?.model_usage && Object.keys(analytics.model_usage).length > 0 ? (
                <div className="space-y-3">
                  {Object.entries(analytics.model_usage).map(([model, count]) => (
                    <div key={model} className="flex items-center justify-between">
                      <span className="text-sm font-medium">{model || 'Unknown'}</span>
                      <span className="text-sm text-muted-foreground">{count} messages</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground text-center py-8">No model usage data yet</p>
              )}
            </CardContent>
          </Card>

          {/* Recent Activity */}
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
            </CardHeader>
            <CardContent>
              {analytics?.recent_activity?.length > 0 ? (
                <div className="space-y-3">
                  {analytics.recent_activity.slice(0, 5).map((activity, index) => (
                    <div key={index} className="flex items-start gap-3 text-sm">
                      <div className={`h-2 w-2 rounded-full mt-1.5 ${
                        activity.role === 'user' ? 'bg-primary' : 'bg-secondary'
                      }`} />
                      <div className="flex-1">
                        <p className="font-medium capitalize">{activity.role} message</p>
                        <p className="text-xs text-muted-foreground">
                          {format(new Date(activity.timestamp), 'MMM d, HH:mm')}
                          {activity.tokens > 0 && ` • ${activity.tokens} tokens`}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="text-muted-foreground text-center py-8">No recent activity</p>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
