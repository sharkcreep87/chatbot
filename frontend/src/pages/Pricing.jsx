import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { subscriptionAPI, vendorAPI } from '@/services/api';
import toast from 'react-hot-toast';
import { Check, Zap, Crown, Building2 } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

export function Pricing() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [billingCycle, setBillingCycle] = useState('monthly');

  const { data: plans = [], isLoading } = useQuery({
    queryKey: ['subscription-plans'],
    queryFn: async () => {
      const response = await subscriptionAPI.getPlans();
      return response.data;
    },
  });

  const { data: currentSubscription } = useQuery({
    queryKey: ['current-subscription'],
    queryFn: async () => {
      try {
        const response = await vendorAPI.getSubscription();
        return response.data;
      } catch (error) {
        return null;
      }
    },
  });

  const subscribeMutation = useMutation({
    mutationFn: (planId) =>
      vendorAPI.createOrUpdateSubscription({ plan_id: planId, billing_cycle: billingCycle }),
    onSuccess: () => {
      queryClient.invalidateQueries(['current-subscription']);
      queryClient.invalidateQueries(['usage-limits']);
      toast.success('Subscription updated successfully!');
      navigate('/chat');
    },
    onError: (error) => {
      toast.error(error.response?.data?.detail || 'Failed to update subscription');
    },
  });

  const getPlanIcon = (slug) => {
    switch (slug) {
      case 'free':
        return <Zap className="h-6 w-6" />;
      case 'basic':
        return <Check className="h-6 w-6" />;
      case 'pro':
        return <Crown className="h-6 w-6" />;
      case 'enterprise':
        return <Building2 className="h-6 w-6" />;
      default:
        return <Check className="h-6 w-6" />;
    }
  };

  const formatPrice = (plan) => {
    const price = billingCycle === 'monthly' ? plan.price_monthly : plan.price_yearly;
    if (price === 0) return 'Free';

    const monthlyPrice = billingCycle === 'yearly' ? (price / 12).toFixed(0) : price;
    return (
      <div>
        <span className="text-4xl font-bold">${monthlyPrice}</span>
        <span className="text-muted-foreground">/month</span>
        {billingCycle === 'yearly' && (
          <div className="text-sm text-muted-foreground">
            Billed ${price}/year
          </div>
        )}
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-lg">Loading pricing plans...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-primary/5 to-secondary/5 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Choose Your Plan</h1>
          <p className="text-xl text-muted-foreground mb-8">
            Select the perfect plan for your needs
          </p>

          {/* Billing Toggle */}
          <div className="inline-flex rounded-lg bg-muted p-1">
            <button
              className={`px-6 py-2 rounded-md transition-colors ${
                billingCycle === 'monthly'
                  ? 'bg-background shadow-sm'
                  : 'text-muted-foreground'
              }`}
              onClick={() => setBillingCycle('monthly')}
            >
              Monthly
            </button>
            <button
              className={`px-6 py-2 rounded-md transition-colors ${
                billingCycle === 'yearly'
                  ? 'bg-background shadow-sm'
                  : 'text-muted-foreground'
              }`}
              onClick={() => setBillingCycle('yearly')}
            >
              Yearly
              <span className="ml-2 text-xs text-primary font-semibold">Save 17%</span>
            </button>
          </div>
        </div>

        {/* Plans Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {plans.map((plan) => (
            <Card
              key={plan.id}
              className={`relative ${
                plan.is_popular
                  ? 'border-primary shadow-lg scale-105'
                  : ''
              }`}
            >
              {plan.is_popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2">
                  <span className="bg-primary text-primary-foreground text-xs font-semibold px-3 py-1 rounded-full">
                    Most Popular
                  </span>
                </div>
              )}

              <CardHeader className="text-center pb-8">
                <div className="inline-flex h-12 w-12 items-center justify-center rounded-full bg-primary/10 text-primary mx-auto mb-4">
                  {getPlanIcon(plan.slug)}
                </div>
                <CardTitle className="text-2xl">{plan.name}</CardTitle>
                <p className="text-sm text-muted-foreground mt-2">
                  {plan.description}
                </p>
              </CardHeader>

              <CardContent className="space-y-6">
                {/* Price */}
                <div className="text-center py-4">
                  {formatPrice(plan)}
                </div>

                {/* Features */}
                <div className="space-y-3 text-sm">
                  <div className="flex items-center gap-2">
                    <Check className="h-4 w-4 text-primary" />
                    <span>{plan.max_conversations_per_month.toLocaleString()} conversations/month</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="h-4 w-4 text-primary" />
                    <span>{plan.max_messages_per_month.toLocaleString()} messages/month</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="h-4 w-4 text-primary" />
                    <span>{plan.max_tokens_per_month.toLocaleString()} tokens/month</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="h-4 w-4 text-primary" />
                    <span>{plan.max_knowledge_bases} knowledge bases</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="h-4 w-4 text-primary" />
                    <span>{plan.max_documents} documents</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="h-4 w-4 text-primary" />
                    <span>{plan.max_storage_mb}MB storage</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <Check className="h-4 w-4 text-primary" />
                    <span>{plan.max_users} users</span>
                  </div>

                  {plan.features?.analytics && (
                    <div className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      <span>Advanced Analytics</span>
                    </div>
                  )}
                  {plan.features?.api_access && (
                    <div className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      <span>API Access</span>
                    </div>
                  )}
                  {plan.features?.custom_branding && (
                    <div className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      <span>Custom Branding</span>
                    </div>
                  )}
                  {plan.features?.priority_support && (
                    <div className="flex items-center gap-2">
                      <Check className="h-4 w-4 text-primary" />
                      <span>Priority Support</span>
                    </div>
                  )}
                </div>

                {/* CTA Button */}
                <Button
                  className="w-full"
                  variant={plan.is_popular ? 'default' : 'outline'}
                  onClick={() => subscribeMutation.mutate(plan.id)}
                  disabled={
                    subscribeMutation.isPending ||
                    currentSubscription?.plan_id === plan.id
                  }
                >
                  {currentSubscription?.plan_id === plan.id
                    ? 'Current Plan'
                    : subscribeMutation.isPending
                    ? 'Processing...'
                    : plan.price_monthly === 0
                    ? 'Get Started'
                    : 'Subscribe'}
                </Button>
              </CardContent>
            </Card>
          ))}
        </div>

        {/* FAQ or Additional Info */}
        <div className="mt-16 text-center text-sm text-muted-foreground">
          <p>All plans include 24/7 support and regular updates</p>
          <p className="mt-2">Need a custom plan? Contact us for Enterprise options</p>
        </div>
      </div>
    </div>
  );
}
