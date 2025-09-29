import { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../ui/select';
import { Textarea } from '../ui/textarea';
import { Separator } from '../ui/separator';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from '../ui/dialog';
import { 
  CheckCircle, 
  XCircle, 
  MessageSquare, 
  Search, 
  Filter, 
  Clock, 
  TrendingUp, 
  AlertTriangle, 
  Shield,
  Users,
  DollarSign,
  FileText
} from 'lucide-react';

function PayorDashboard() {
  const [priorityFilter, setPriorityFilter] = useState('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedClaim, setSelectedClaim] = useState(null);

  // Mock data
  const analytics = {
    avgProcessingTime: '2.3 days',
    approvalRatio: 87,
    totalClaimsToday: 45,
    pendingReview: 23,
    totalProcessed: 1247,
    totalAmount: '$2,845,320'
  };

  const claimsQueue = [
    {
      id: 'CLM-2024-001',
      patient: {
        name: 'John Doe',
        id: 'P-12345',
        age: 45,
        policyNumber: 'BC-789-456'
      },
      provider: {
        name: 'City General Hospital',
        id: 'H-5678',
        network: 'In-Network'
      },
      claim: {
        diagnosis: 'Acute Bronchitis',
        amount: '$1,250',
        submittedDate: '2024-01-15',
        priority: 'medium',
        urgency: 'Standard'
      },
      coverage: {
        status: 'Active',
        type: 'Preferred PPO',
        preAuth: 'Not Required'
      }
    },
    {
      id: 'CLM-2024-002',
      patient: {
        name: 'Jane Smith',
        id: 'P-12346',
        age: 32,
        policyNumber: 'BC-456-789'
      },
      provider: {
        name: 'Downtown Clinic',
        id: 'C-2345',
        network: 'In-Network'
      },
      claim: {
        diagnosis: 'Annual Physical',
        amount: '$350',
        submittedDate: '2024-01-14',
        priority: 'low',
        urgency: 'Routine'
      },
      coverage: {
        status: 'Active',
        type: 'Standard PPO',
        preAuth: 'Not Required'
      }
    },
    {
      id: 'CLM-2024-003',
      patient: {
        name: 'Mike Johnson',
        id: 'P-12347',
        age: 58,
        policyNumber: 'BC-321-654'
      },
      provider: {
        name: 'Cardiac Specialists',
        id: 'S-7890',
        network: 'Out-of-Network'
      },
      claim: {
        diagnosis: 'Cardiac Evaluation',
        amount: '$2,800',
        submittedDate: '2024-01-13',
        priority: 'high',
        urgency: 'Expedited'
      },
      coverage: {
        status: 'Active',
        type: 'Premium PPO',
        preAuth: 'Required'
      }
    }
  ];

  const filteredClaims = claimsQueue.filter(claim => {
    const matchesPriority = priorityFilter === 'all' || claim.claim.priority === priorityFilter;
    const matchesSearch = searchTerm === '' || 
      claim.patient.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      claim.id.toLowerCase().includes(searchTerm.toLowerCase()) ||
      claim.provider.name.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesPriority && matchesSearch;
  });

  const getPriorityBadge = (priority) => {
    switch (priority) {
      case 'high':
        return <Badge className="bg-red-100 text-red-800 hover:bg-red-100">High Priority</Badge>;
      case 'medium':
        return <Badge className="bg-yellow-100 text-yellow-800 hover:bg-yellow-100">Medium Priority</Badge>;
      case 'low':
        return <Badge className="bg-green-100 text-green-800 hover:bg-green-100">Low Priority</Badge>;
      default:
        return <Badge className="bg-gray-100 text-gray-800 hover:bg-gray-100">Standard</Badge>;
    }
  };

  const getNetworkColor = (network) => {
    return network === 'In-Network' ? 'text-green-600' : 'text-orange-600';
  };

  return (
    <div className="p-6 space-y-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
        <div className="flex items-center space-x-4">
          <div className="p-3 bg-gradient-to-br from-[#4ea8de] to-purple-500 rounded-2xl shadow-lg">
            <Shield className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl text-gray-900 mb-2">Payor Dashboard</h1>
            <p className="text-[#6b7280]">Review and process insurance claims efficiently</p>
          </div>
        </div>
      </div>

      {/* Analytics Cards: Average Processing Time, Approval Ratio */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card className="rounded-2xl border-0 shadow-sm bg-gradient-to-br from-blue-50 to-blue-100">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-blue-600 mb-1">Average Processing Time</p>
                <p className="text-3xl text-blue-900 font-medium">{analytics.avgProcessingTime}</p>
                <p className="text-xs text-blue-700 mt-1">-0.5 days from last month</p>
              </div>
              <Clock className="h-10 w-10 text-blue-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="rounded-2xl border-0 shadow-sm bg-gradient-to-br from-green-50 to-green-100">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-green-600 mb-1">Approval Ratio</p>
                <p className="text-3xl text-green-900 font-medium">{analytics.approvalRatio}%</p>
                <p className="text-xs text-green-700 mt-1">+2% from last month</p>
              </div>
              <TrendingUp className="h-10 w-10 text-green-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="rounded-2xl border-0 shadow-sm bg-gradient-to-br from-purple-50 to-purple-100">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-purple-600 mb-1">Claims Today</p>
                <p className="text-3xl text-purple-900 font-medium">{analytics.totalClaimsToday}</p>
                <p className="text-xs text-purple-700 mt-1">15 awaiting review</p>
              </div>
              <FileText className="h-10 w-10 text-purple-600" />
            </div>
          </CardContent>
        </Card>

        <Card className="rounded-2xl border-0 shadow-sm bg-gradient-to-br from-amber-50 to-amber-100">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-amber-600 mb-1">Total Amount</p>
                <p className="text-3xl text-amber-900 font-medium">{analytics.totalAmount}</p>
                <p className="text-xs text-amber-700 mt-1">This month processed</p>
              </div>
              <DollarSign className="h-10 w-10 text-amber-600" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Queue List: Submitted claims with patient + provider info */}
      <Card className="rounded-2xl border-0 shadow-sm">
        <CardHeader>
          <CardTitle>Queue List of Submitted Claims</CardTitle>
          <CardDescription>
            Review submitted claims with patient and provider information
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row gap-4 mb-6">
            <div className="flex-1">
              <Input
                placeholder="Search by patient name, claim ID, or provider..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="h-12 bg-gray-50 border-gray-200 rounded-xl focus:border-[#4ea8de] focus:ring-[#4ea8de]"
              />
            </div>
            <Select value={priorityFilter} onValueChange={setPriorityFilter}>
              <SelectTrigger className="w-full md:w-48 h-12 bg-gray-50 border-gray-200 rounded-xl">
                <SelectValue placeholder="Filter by priority" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Priorities</SelectItem>
                <SelectItem value="high">High Priority</SelectItem>
                <SelectItem value="medium">Medium Priority</SelectItem>
                <SelectItem value="low">Low Priority</SelectItem>
              </SelectContent>
            </Select>
            <Button className="h-12 px-8 bg-[#4ea8de] hover:bg-[#3d8bbd] rounded-xl">
              <Search className="w-4 h-4 mr-2" />
              Search
            </Button>
          </div>

          {/* Claims Queue with Action Buttons per Row */}
          <div className="space-y-4">
            {filteredClaims.map((claim) => (
              <Card key={claim.id} className="rounded-2xl border border-gray-200 hover:shadow-md transition-shadow">
                <CardContent className="p-6">
                  <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
                    {/* Patient + Provider Info */}
                    <div className="lg:col-span-2 grid grid-cols-1 md:grid-cols-2 gap-6">
                      {/* Patient Information */}
                      <div>
                        <h4 className="text-sm text-[#6b7280] mb-3">Patient Information</h4>
                        <div className="space-y-2">
                          <p className="text-gray-900 font-medium">{claim.patient.name}</p>
                          <p className="text-sm text-[#6b7280]">Age: {claim.patient.age}</p>
                          <p className="text-sm text-[#6b7280]">ID: {claim.patient.id}</p>
                          <p className="text-sm text-[#6b7280]">Policy: {claim.patient.policyNumber}</p>
                        </div>
                      </div>

                      {/* Provider Information */}
                      <div>
                        <h4 className="text-sm text-[#6b7280] mb-3">Provider Information</h4>
                        <div className="space-y-2">
                          <p className="text-gray-900 font-medium">{claim.provider.name}</p>
                          <p className="text-sm text-[#6b7280]">ID: {claim.provider.id}</p>
                          <p className={`text-sm ${getNetworkColor(claim.provider.network)}`}>
                            {claim.provider.network}
                          </p>
                        </div>
                      </div>
                    </div>

                    {/* Claim Details */}
                    <div>
                      <h4 className="text-sm text-[#6b7280] mb-3">Claim Details</h4>
                      <div className="space-y-2">
                        <p className="text-[#4ea8de] font-medium">{claim.id}</p>
                        <p className="text-sm text-[#6b7280]">{claim.claim.diagnosis}</p>
                        <p className="text-xl text-gray-900 font-medium">{claim.claim.amount}</p>
                        <p className="text-sm text-[#6b7280]">Submitted: {claim.claim.submittedDate}</p>
                        {getPriorityBadge(claim.claim.priority)}
                      </div>
                    </div>

                    {/* Action Buttons per Row: Approve, Reject, Request Info */}
                    <div>
                      <h4 className="text-sm text-[#6b7280] mb-3">Actions</h4>
                      <div className="space-y-3">
                        <Button 
                          size="sm" 
                          className="w-full bg-[#4ade80] hover:bg-green-600 text-white rounded-xl"
                        >
                          <CheckCircle className="h-4 w-4 mr-2" />
                          Approve
                        </Button>
                        <Button 
                          size="sm" 
                          variant="destructive"
                          className="w-full rounded-xl"
                        >
                          <XCircle className="h-4 w-4 mr-2" />
                          Reject
                        </Button>
                        <Dialog>
                          <DialogTrigger asChild>
                            <Button 
                              size="sm" 
                              variant="outline"
                              className="w-full rounded-xl border-[#4ea8de] text-[#4ea8de] hover:bg-[#4ea8de] hover:text-white"
                            >
                              <MessageSquare className="h-4 w-4 mr-2" />
                              Request Info
                            </Button>
                          </DialogTrigger>
                          <DialogContent className="max-w-md rounded-2xl">
                            <DialogHeader>
                              <DialogTitle>Request Additional Information</DialogTitle>
                              <DialogDescription>
                                Send a request for more information about this claim
                              </DialogDescription>
                            </DialogHeader>
                            <div className="space-y-4 py-4">
                              <div className="space-y-2">
                                <Label htmlFor="request-type">Request Type</Label>
                                <Select>
                                  <SelectTrigger className="rounded-xl">
                                    <SelectValue placeholder="Select request type" />
                                  </SelectTrigger>
                                  <SelectContent>
                                    <SelectItem value="documentation">Additional Documentation</SelectItem>
                                    <SelectItem value="clarification">Medical Clarification</SelectItem>
                                    <SelectItem value="authorization">Prior Authorization</SelectItem>
                                  </SelectContent>
                                </Select>
                              </div>
                              <div className="space-y-2">
                                <Label htmlFor="message">Message</Label>
                                <Textarea
                                  id="message"
                                  placeholder="Describe what additional information is needed..."
                                  className="min-h-[100px] rounded-xl"
                                />
                              </div>
                            </div>
                            <div className="flex justify-end space-x-2">
                              <Button variant="outline" className="rounded-xl">Cancel</Button>
                              <Button className="bg-[#4ea8de] hover:bg-[#3d8bbd] rounded-xl">Send Request</Button>
                            </div>
                          </DialogContent>
                        </Dialog>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Coverage Rules & Validation */}
      <Card className="rounded-2xl border-0 shadow-sm">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="w-5 h-5 text-blue-600" />
            Coverage Rules & Validation
          </CardTitle>
          <CardDescription>
            Automated validation status for current claim queue
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-4 border border-green-200 rounded-2xl bg-green-50">
              <div className="flex items-center space-x-3 mb-2">
                <CheckCircle className="h-6 w-6 text-green-600" />
                <h4 className="text-green-800 font-medium">Policy Validation</h4>
              </div>
              <p className="text-sm text-green-700">All claims have active, valid policies</p>
              <p className="text-xs text-green-600 mt-1">3/3 claims validated</p>
            </div>
            
            <div className="p-4 border border-yellow-200 rounded-2xl bg-yellow-50">
              <div className="flex items-center space-x-3 mb-2">
                <AlertTriangle className="h-6 w-6 text-yellow-600" />
                <h4 className="text-yellow-800 font-medium">Pre-Authorization</h4>
              </div>
              <p className="text-sm text-yellow-700">1 claim requires pre-authorization review</p>
              <p className="text-xs text-yellow-600 mt-1">CLM-2024-003 pending approval</p>
            </div>
            
            <div className="p-4 border border-blue-200 rounded-2xl bg-blue-50">
              <div className="flex items-center space-x-3 mb-2">
                <Shield className="h-6 w-6 text-blue-600" />
                <h4 className="text-blue-800 font-medium">Coverage Limits</h4>
              </div>
              <p className="text-sm text-blue-700">All claims within policy coverage limits</p>
              <p className="text-xs text-blue-600 mt-1">No overages detected</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}

export default PayorDashboard;
