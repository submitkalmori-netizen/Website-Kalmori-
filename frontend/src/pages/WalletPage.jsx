import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { API } from '../App';
import DashboardLayout from '../components/DashboardLayout';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '../components/ui/dialog';
import { 
  Wallet, 
  CurrencyDollar,
  ArrowDown,
  Clock,
  CheckCircle,
  Warning,
  PaypalLogo,
  Bank
} from '@phosphor-icons/react';
import { toast } from 'sonner';

const WalletPage = () => {
  const [wallet, setWallet] = useState(null);
  const [withdrawals, setWithdrawals] = useState([]);
  const [loading, setLoading] = useState(true);
  const [showWithdraw, setShowWithdraw] = useState(false);
  const [withdrawForm, setWithdrawForm] = useState({
    amount: '',
    method: 'paypal',
    paypal_email: ''
  });
  const [withdrawing, setWithdrawing] = useState(false);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [walletRes, withdrawalsRes] = await Promise.all([
        axios.get(`${API}/wallet`),
        axios.get(`${API}/wallet/withdrawals`)
      ]);
      setWallet(walletRes.data);
      setWithdrawals(withdrawalsRes.data);
    } catch (error) {
      console.error('Failed to fetch wallet data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleWithdraw = async () => {
    const amount = parseFloat(withdrawForm.amount);
    
    if (!amount || amount < 10) {
      toast.error('Minimum withdrawal is $10');
      return;
    }
    
    if (amount > wallet.balance) {
      toast.error('Insufficient balance');
      return;
    }
    
    if (withdrawForm.method === 'paypal' && !withdrawForm.paypal_email) {
      toast.error('Please enter your PayPal email');
      return;
    }
    
    setWithdrawing(true);
    try {
      await axios.post(`${API}/wallet/withdraw`, {
        amount,
        method: withdrawForm.method,
        paypal_email: withdrawForm.paypal_email || null
      });
      toast.success('Withdrawal requested successfully!');
      setShowWithdraw(false);
      setWithdrawForm({ amount: '', method: 'paypal', paypal_email: '' });
      fetchData();
    } catch (error) {
      const msg = error.response?.data?.detail || 'Withdrawal failed';
      toast.error(typeof msg === 'string' ? msg : 'Withdrawal failed');
    } finally {
      setWithdrawing(false);
    }
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-[#22C55E]" />;
      case 'pending':
        return <Clock className="w-4 h-4 text-[#FFCC00]" />;
      case 'failed':
        return <Warning className="w-4 h-4 text-[#FF3B30]" />;
      default:
        return <Clock className="w-4 h-4 text-[#71717A]" />;
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="w-8 h-8 border-2 border-[#FF3B30] border-t-transparent rounded-full animate-spin" />
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-8" data-testid="wallet-page">
        {/* Header */}
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold tracking-tight">Wallet</h1>
          <p className="text-[#A1A1AA] mt-1">Manage your earnings and withdrawals</p>
        </div>

        {/* Balance Cards */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-[#141414] border border-white/10 p-6 rounded-md">
            <div className="flex items-center justify-between mb-4">
              <Wallet className="w-6 h-6 text-[#22C55E]" />
              <span className="text-xs text-[#A1A1AA] uppercase">Available</span>
            </div>
            <p className="text-3xl font-bold font-mono text-[#22C55E]">
              ${wallet?.balance?.toFixed(2) || '0.00'}
            </p>
          </div>

          <div className="bg-[#141414] border border-white/10 p-6 rounded-md">
            <div className="flex items-center justify-between mb-4">
              <Clock className="w-6 h-6 text-[#FFCC00]" />
              <span className="text-xs text-[#A1A1AA] uppercase">Pending</span>
            </div>
            <p className="text-3xl font-bold font-mono text-[#FFCC00]">
              ${wallet?.pending_balance?.toFixed(2) || '0.00'}
            </p>
          </div>

          <div className="bg-[#141414] border border-white/10 p-6 rounded-md">
            <div className="flex items-center justify-between mb-4">
              <CurrencyDollar className="w-6 h-6 text-[#007AFF]" />
              <span className="text-xs text-[#A1A1AA] uppercase">Total Earned</span>
            </div>
            <p className="text-3xl font-bold font-mono">
              ${wallet?.total_earnings?.toFixed(2) || '0.00'}
            </p>
          </div>
        </div>

        {/* Withdraw Button */}
        <div className="flex justify-end">
          <Button 
            onClick={() => setShowWithdraw(true)}
            disabled={!wallet?.balance || wallet.balance < 10}
            className="bg-[#FF3B30] hover:bg-[#FF3B30]/90 text-white"
            data-testid="withdraw-btn"
          >
            <ArrowDown className="w-4 h-4 mr-2" />
            Withdraw Funds
          </Button>
        </div>

        {/* Withdrawal History */}
        <div className="bg-[#141414] border border-white/10 rounded-md">
          <div className="p-6 border-b border-white/10">
            <h2 className="text-lg font-medium">Withdrawal History</h2>
          </div>

          {withdrawals.length === 0 ? (
            <div className="p-12 text-center">
              <ArrowDown className="w-12 h-12 text-[#71717A] mx-auto mb-4" />
              <p className="text-[#A1A1AA]">No withdrawals yet</p>
            </div>
          ) : (
            <div className="divide-y divide-white/5">
              {withdrawals.map((withdrawal) => (
                <div 
                  key={withdrawal.id}
                  className="px-6 py-4 flex items-center justify-between"
                >
                  <div className="flex items-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center">
                      {withdrawal.method === 'paypal' ? (
                        <PaypalLogo className="w-5 h-5 text-[#007AFF]" />
                      ) : (
                        <Bank className="w-5 h-5 text-[#22C55E]" />
                      )}
                    </div>
                    <div>
                      <p className="font-medium capitalize">{withdrawal.method.replace('_', ' ')}</p>
                      <p className="text-xs text-[#71717A]">
                        {new Date(withdrawal.created_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  
                  <div className="flex items-center gap-4">
                    <span className="font-mono font-medium">
                      -${withdrawal.amount.toFixed(2)}
                    </span>
                    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded text-xs capitalize ${
                      withdrawal.status === 'completed' ? 'bg-[#22C55E]/10 text-[#22C55E]' :
                      withdrawal.status === 'pending' ? 'bg-[#FFCC00]/10 text-[#FFCC00]' :
                      'bg-[#FF3B30]/10 text-[#FF3B30]'
                    }`}>
                      {getStatusIcon(withdrawal.status)}
                      {withdrawal.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Info */}
        <div className="bg-[#007AFF]/10 border border-[#007AFF]/30 rounded-md p-4 text-sm">
          <p className="text-[#007AFF] font-medium mb-2">How Payouts Work</p>
          <ul className="text-[#A1A1AA] space-y-1">
            <li>• Minimum withdrawal amount is $10</li>
            <li>• Withdrawals are processed within 3-5 business days</li>
            <li>• PayPal and bank transfer are supported</li>
            <li>• Royalties are updated monthly from streaming platforms</li>
          </ul>
        </div>

        {/* Withdraw Dialog */}
        <Dialog open={showWithdraw} onOpenChange={setShowWithdraw}>
          <DialogContent className="bg-[#141414] border-white/10 text-white">
            <DialogHeader>
              <DialogTitle>Withdraw Funds</DialogTitle>
              <DialogDescription className="text-[#A1A1AA]">
                Enter the amount and payment method
              </DialogDescription>
            </DialogHeader>

            <div className="space-y-4 py-4">
              <div>
                <Label className="text-white mb-2 block">Amount</Label>
                <div className="relative">
                  <span className="absolute left-3 top-1/2 -translate-y-1/2 text-[#71717A]">$</span>
                  <Input
                    type="number"
                    value={withdrawForm.amount}
                    onChange={(e) => setWithdrawForm({ ...withdrawForm, amount: e.target.value })}
                    placeholder="0.00"
                    min="10"
                    max={wallet?.balance}
                    step="0.01"
                    className="pl-8 bg-[#0A0A0A] border-white/10 text-white"
                    data-testid="withdraw-amount-input"
                  />
                </div>
                <p className="text-xs text-[#71717A] mt-1">
                  Available: ${wallet?.balance?.toFixed(2) || '0.00'}
                </p>
              </div>

              <div>
                <Label className="text-white mb-2 block">Payment Method</Label>
                <Select 
                  value={withdrawForm.method} 
                  onValueChange={(v) => setWithdrawForm({ ...withdrawForm, method: v })}
                >
                  <SelectTrigger className="bg-[#0A0A0A] border-white/10 text-white" data-testid="payment-method-select">
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent className="bg-[#141414] border-white/10">
                    <SelectItem value="paypal">
                      <div className="flex items-center gap-2">
                        <PaypalLogo className="w-4 h-4" /> PayPal
                      </div>
                    </SelectItem>
                    <SelectItem value="bank_transfer">
                      <div className="flex items-center gap-2">
                        <Bank className="w-4 h-4" /> Bank Transfer
                      </div>
                    </SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {withdrawForm.method === 'paypal' && (
                <div>
                  <Label className="text-white mb-2 block">PayPal Email</Label>
                  <Input
                    type="email"
                    value={withdrawForm.paypal_email}
                    onChange={(e) => setWithdrawForm({ ...withdrawForm, paypal_email: e.target.value })}
                    placeholder="your@paypal.com"
                    className="bg-[#0A0A0A] border-white/10 text-white"
                    data-testid="paypal-email-input"
                  />
                </div>
              )}
            </div>

            <DialogFooter>
              <Button
                variant="outline"
                onClick={() => setShowWithdraw(false)}
                className="border-white/10 hover:bg-white/5 text-white"
              >
                Cancel
              </Button>
              <Button
                onClick={handleWithdraw}
                disabled={withdrawing}
                className="bg-[#FF3B30] hover:bg-[#FF3B30]/90 text-white"
                data-testid="confirm-withdraw-btn"
              >
                {withdrawing ? (
                  <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                ) : (
                  'Withdraw'
                )}
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>
    </DashboardLayout>
  );
};

export default WalletPage;
