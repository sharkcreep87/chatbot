import { useQuery } from '@tanstack/react-query';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { vendorAPI } from '@/services/api';
import { useNavigate } from 'react-router-dom';
import {
  Crown,
  Calendar,
  TrendingUp,
  Database,
  MessageSquare,
  Zap,
  FileText,
  HardDrive,
} from 'lucide-react';
import { format } from 'date-fns';

export function Subscription() {
  const navigate = useNavigate();

  const { data: subscription, isLoading: subLoading } = useQuery({
    queryKey: ['current-subscription'],
    queryFn: async () => {
      const response = await vendorAPI.getSubscription();
      return response.data;
    },
  });

  const { data: usageLimits, isLoading: limitsLoading } = useQuery({
    queryKey: ['usage-limits'],
    queryFn: async () => {
      const response = await vendorAPI.getUsageLimits();
      return response.data;
    },
  });

  const UsageBar = ({ label, used, limit, percentage, icon: Icon }) => {
    const isNearLimit = percentage > 80;
    const isAtLimit = percentage >= 100;

    return (
      <div className="space-y-2">
        <div className="flex items-center justify-between text-sm">
          <div className="flex items-center gap-2">
            <Icon className="h-4 w-4 text-muted-foreground" />
            <span className="font-medium">{label}</span>
          </div>
          <span className="text-muted-foreground">
            {used.toLocaleString()} / {limit.toLocaleString()}
          </span>
        </div>
        <div className="h-2 rounded-full bg-muted overflow-hidden">
          <div
            className={`h-full transition-all ${
              isAtLimit
                ? 'bg-destructive'
                : isNearLimit
                ? 'bg-yellow-500'
                : 'bg-primary'
            }`}
            style={{ width: `${Math.min(percentage, 100)}%` }}
          />
        </div>
        <div className="text-xs text-muted-foreground">
          {percentage.toFixed(1)}% used
        </div>
      </div>
    );
  };

  if (subLoading || limitsLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading subscription details...</div>
      </div>
    );
  }

  if (!subscription) {
    return (
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-4xl mx-auto text-center space-y-6">
          <h1 className="text-3xl font-bold">No Active Subscription</h1>
          <p className="text-muted-foreground">
            Choose a plan to get started with ChatterMate Pro
          </p>
          <Button onClick={() => navigate('/pricing')}>
            View Pricing Plans
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-6xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Subscription & Usage</h1>
            <p className="text-muted-foreground mt-1">
              Manage your subscription and track usage
            </p>
          </div>
          <Button onClick={() => navigate('/pricing')}>
            Upgrade Plan
          </Button>
        </div>

        {/* Current Plan */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center">
                  <Crown className="h-6 w-6 text-primary" />
                </div>
                <div>
                  <CardTitle className="text-2xl">{subscription.plan.name} Plan</CardTitle>
                  <p className="text-sm text-muted-foreground">
                    {subscription.plan.description}
                  </p>
                </div>
              </div>
              <div className="text-right">
                <div className="text-3xl font-bold">
                  ${subscription.billing_cycle === 'monthly'
                    ? subscription.plan.price_monthly
                    : subscription.plan.price_yearly}
                </div>
                <div className="text-sm text-muted-foreground">
                  /{subscription.billing_cycle}
                </div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div className="flex items-center gap-2">
                <Calendar className="h-4 w-4 text-muted-foreground" />
                <div>
                  <div className="font-medium">Status</div>
                  <div className="text-muted-foreground capitalize">{subscription.status}</div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <TrendingUp className="h-4 w-4 text-muted-foreground" />
                <div>
                  <div className="font-medium">Current Period</div>
                  <div className="text-muted-foreground">
                    {format(new Date(subscription.current_period_start), 'MMM d')} -{' '}
                    {subscription.current_period_end && format(new Date(subscription.current_period_end), 'MMM d')}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Crown className="h-4 w-4 text-muted-foreground" />
                <div>
                  <div className="font-medium">Billing Cycle</div>
                  <div className="text-muted-foreground capitalize">{subscription.billing_cycle}</div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Usage Stats */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Message Usage</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <UsageBar
                label="Conversations"
                used={usageLimits?.conversations?.used || 0}
                limit={usageLimits?.conversations?.limit || 0}
                percentage={usageLimits?.conversations?.percentage || 0}
                icon={MessageSquare}
              />
              <UsageBar
                label="Messages"
                used={usageLimits?.messages?.used || 0}
                limit={usageLimits?.messages?.limit || 0}
                percentage={usageLimits?.messages?.percentage || 0}
                icon={MessageSquare}
              />
              <UsageBar
                label="Tokens"
                used={usageLimits?.tokens?.used || 0}
                limit={usageLimits?.tokens?.limit || 0}
                percentage={usageLimits?.tokens?.percentage || 0}
                icon={Zap}
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Storage & Knowledge Base</CardTitle>
            </CardHeader>
            <CardContent className="space-y-6">
              <UsageBar
                label="Knowledge Bases"
                used={usageLimits?.knowledge_bases?.used || 0}
                limit={usageLimits?.knowledge_bases?.limit || 0}
                percentage={usageLimits?.knowledge_bases?.percentage || 0}
                icon={Database}
              />
              <UsageBar
                label="Documents"
                used={usageLimits?.documents?.used || 0}
                limit={usageLimits?.documents?.limit || 0}
                percentage={usageLimits?.documents?.percentage || 0}
                icon={FileText}
              />
              <UsageBar
                label="Storage (MB)"
                used={usageLimits?.storage?.used || 0}
                limit={usageLimits?.storage?.limit || 0}
                percentage={usageLimits?.storage?.percentage || 0}
                icon={HardDrive}
              />
            </CardContent>
          </Card>
        </div>

        {/* Plan Features */}
        <Card>
          <CardHeader>
            <CardTitle>Plan Features</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              <div className="flex items-center gap-2 text-sm">
                <div className="h-2 w-2 rounded-full bg-primary" />
                <span>{subscription.plan.max_users} Team Members</span>
              </div>
              {subscription.plan.features?.analytics && (
                <div className="flex items-center gap-2 text-sm">
                  <div className="h-2 w-2 rounded-full bg-primary" />
                  <span>Advanced Analytics</span>
                </div>
              )}
              {subscription.plan.features?.api_access && (
                <div className="flex items-center gap-2 text-sm">
                  <div className="h-2 w-2 rounded-full bg-primary" />
                  <span>API Access</span>
                </div>
              )}
              {subscription.plan.features?.custom_branding && (
                <div className="flex items-center gap-2 text-sm">
                  <div className="h-2 w-2 rounded-full bg-primary" />
                  <span>Custom Branding</span>
                </div>
              )}
              {subscription.plan.features?.priority_support && (
                <div className="flex items-center gap-2 text-sm">
                  <div className="h-2 w-2 rounded-full bg-primary" />
                  <span>Priority Support</span>
                </div>
              )}
              <div className="flex items-center gap-2 text-sm">
                <div className="h-2 w-2 rounded-full bg-primary" />
                <span>AI Models: {subscription.plan.ai_models.length}</span>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Warnings */}
        {Object.values(usageLimits || {}).some((limit) => limit?.percentage > 80) && (
          <Card className="border-yellow-500 bg-yellow-500/5">
            <CardContent className="p-4">
              <div className="flex items-start gap-3">
                <TrendingUp className="h-5 w-5 text-yellow-500 mt-0.5" />
                <div>
                  <h3 className="font-semibold">Approaching Limit</h3>
                  <p className="text-sm text-muted-foreground mt-1">
                    You're approaching your plan limits. Consider upgrading to avoid service
                    interruption.
                  </p>
                  <Button
                    size="sm"
                    className="mt-3"
                    onClick={() => navigate('/pricing')}
                  >
                    Upgrade Now
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
