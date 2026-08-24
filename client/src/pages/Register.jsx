import React, { useState } from 'react';
import { useNavigate, Link, Navigate } from 'react-router-dom';
import { ShieldAlert } from 'lucide-react';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import { useAuth } from '../hooks/useAuth';
import toast from 'react-hot-toast';

export const Register = () => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: ''
  });
  const [isLoading, setIsLoading] = useState(false);
  const { register, user } = useAuth();
  const navigate = useNavigate();

  if (user) {
    return <Navigate to="/" replace />;
  }

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      await register(formData);
      toast.success('Registration successful!');
      navigate('/');
    } catch (err) {
      toast.error(err.response?.data?.detail || 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.id]: e.target.value });
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-4 py-12">
      <div className="w-full max-w-md space-y-8 rounded-2xl bg-surface/80 border border-border p-8 shadow-xl backdrop-blur-sm">
        <div className="text-center">
          <ShieldAlert className="mx-auto h-12 w-12 text-primary" />
          <h2 className="mt-6 text-3xl font-bold tracking-tight text-text">
            Join ARCDIS
          </h2>
          <p className="mt-2 text-sm text-text_muted">
            Create your SOC operator account
          </p>
        </div>
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="space-y-4">
            <Input
              id="full_name"
              type="text"
              label="Full Name"
              required
              value={formData.full_name}
              onChange={handleChange}
              placeholder="John Doe"
            />
            <Input
              id="email"
              type="email"
              label="Email address"
              required
              value={formData.email}
              onChange={handleChange}
              placeholder="operator@arcdis.local"
            />
            <Input
              id="password"
              type="password"
              label="Password"
              required
              value={formData.password}
              onChange={handleChange}
              placeholder="••••••••"
            />
          </div>
          <Button type="submit" className="w-full" isLoading={isLoading}>
            Create Account
          </Button>
          <p className="text-center text-sm text-text_muted mt-4">
            Already have an account?{' '}
            <Link to="/login" className="font-medium text-primary hover:text-primary_dark transition-colors">
              Sign in
            </Link>
          </p>
        </form>
      </div>
    </div>
  );
};
