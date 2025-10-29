import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { useAdaptiveTexts } from '../contexts/LanguageContext';
import { LanguageModeSelector, LanguageModeFloatingButton } from '../components/LanguageModeSelector';
import { Info, User, Mail, Phone, Calendar, MapPin, FileText } from 'lucide-react';

export const AdaptiveFormExample: React.FC = () => {
  const { t: tPersonal, mode } = useAdaptiveTexts('personal_info');
  const { t: tActions } = useAdaptiveTexts('actions');
  const { t: tValidation } = useAdaptiveTexts('validation');
  const { t: tAlerts } = useAdaptiveTexts('alerts');

  const [formData, setFormData] = useState({
    full_name: '',
    date_of_birth: '',
    place_of_birth: '',
    current_address: '',
    phone: '',
    email: '',
    passport: ''
  });

  const [errors, setErrors] = useState<Record<string, string>>({});

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    // Clear error when user types
    if (errors[field]) {
      setErrors(prev => ({ ...prev, [field]: '' }));
    }
  };

  const validateForm = () => {
    const newErrors: Record<string, string>> = {};

    if (!formData.full_name) newErrors.full_name = tValidation('required');
    if (!formData.email) {
      newErrors.email = tValidation('required');
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = tValidation('invalid_email');
    }
    if (!formData.phone) newErrors.phone = tValidation('required');

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (validateForm()) {
      alert(tAlerts('progress_saved'));
    }
  };

  return (
    <div className="container mx-auto p-6 space-y-6 max-w-4xl">
      {/* Language Mode Selector */}
      <LanguageModeSelector showCard={true} />

      {/* Main Form */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <User className="w-6 h-6 text-blue-600" />
            <span>{tPersonal('section_title')}</span>
          </CardTitle>
          <CardDescription>{tPersonal('section_description')}</CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Full Name */}
            <div className="space-y-2">
              <Label htmlFor="full_name" className="flex items-center space-x-2">
                <FileText className="w-4 h-4" />
                <span>{tPersonal('full_name')} *</span>
              </Label>
              <Input
                id="full_name"
                value={formData.full_name}
                onChange={(e) => handleChange('full_name', e.target.value)}
                placeholder={tPersonal('full_name_help')}
                className={errors.full_name ? 'border-red-500' : ''}
              />
              {errors.full_name && (
                <p className="text-sm text-red-600">{errors.full_name}</p>
              )}
              <p className="text-xs text-gray-600">💡 {tPersonal('full_name_help')}</p>
            </div>

            {/* Date of Birth */}
            <div className="space-y-2">
              <Label htmlFor="date_of_birth" className="flex items-center space-x-2">
                <Calendar className="w-4 h-4" />
                <span>{tPersonal('date_of_birth')}</span>
              </Label>
              <Input
                id="date_of_birth"
                type="date"
                value={formData.date_of_birth}
                onChange={(e) => handleChange('date_of_birth', e.target.value)}
              />
              <p className="text-xs text-gray-600">💡 {tPersonal('date_of_birth_help')}</p>
            </div>

            {/* Place of Birth */}
            <div className="space-y-2">
              <Label htmlFor="place_of_birth" className="flex items-center space-x-2">
                <MapPin className="w-4 h-4" />
                <span>{tPersonal('place_of_birth')}</span>
              </Label>
              <Input
                id="place_of_birth"
                value={formData.place_of_birth}
                onChange={(e) => handleChange('place_of_birth', e.target.value)}
                placeholder={tPersonal('place_of_birth_help')}
              />
              <p className="text-xs text-gray-600">💡 {tPersonal('place_of_birth_help')}</p>
            </div>

            {/* Current Address */}
            <div className="space-y-2">
              <Label htmlFor="current_address" className="flex items-center space-x-2">
                <MapPin className="w-4 h-4" />
                <span>{tPersonal('current_address')}</span>
              </Label>
              <Input
                id="current_address"
                value={formData.current_address}
                onChange={(e) => handleChange('current_address', e.target.value)}
                placeholder={tPersonal('current_address_help')}
              />
              <p className="text-xs text-gray-600">💡 {tPersonal('current_address_help')}</p>
            </div>

            {/* Phone */}
            <div className="space-y-2">
              <Label htmlFor="phone" className="flex items-center space-x-2">
                <Phone className="w-4 h-4" />
                <span>{tPersonal('phone')} *</span>
              </Label>
              <Input
                id="phone"
                type="tel"
                value={formData.phone}
                onChange={(e) => handleChange('phone', e.target.value)}
                placeholder={tPersonal('phone_help')}
                className={errors.phone ? 'border-red-500' : ''}
              />
              {errors.phone && (
                <p className="text-sm text-red-600">{errors.phone}</p>
              )}
              <p className="text-xs text-gray-600">💡 {tPersonal('phone_help')}</p>
            </div>

            {/* Email */}
            <div className="space-y-2">
              <Label htmlFor="email" className="flex items-center space-x-2">
                <Mail className="w-4 h-4" />
                <span>{tPersonal('email')} *</span>
              </Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                placeholder={tPersonal('email_help')}
                className={errors.email ? 'border-red-500' : ''}
              />
              {errors.email && (
                <p className="text-sm text-red-600">{errors.email}</p>
              )}
              <p className="text-xs text-gray-600">💡 {tPersonal('email_help')}</p>
            </div>

            {/* Passport */}
            <div className="space-y-2">
              <Label htmlFor="passport" className="flex items-center space-x-2">
                <FileText className="w-4 h-4" />
                <span>{tPersonal('passport')}</span>
              </Label>
              <Input
                id="passport"
                value={formData.passport}
                onChange={(e) => handleChange('passport', e.target.value)}
                placeholder={tPersonal('passport_help')}
              />
              <p className="text-xs text-gray-600">💡 {tPersonal('passport_help')}</p>
            </div>

            {/* Alerts */}
            <Alert className="border-blue-200 bg-blue-50">
              <Info className="h-4 w-4" />
              <AlertDescription className="text-sm">
                {tAlerts('required_fields')}
              </AlertDescription>
            </Alert>

            <Alert className="border-gray-200 bg-gray-50">
              <Info className="h-4 w-4" />
              <AlertDescription className="text-xs">
                {tAlerts('legal_disclaimer')}
              </AlertDescription>
            </Alert>

            {/* Actions */}
            <div className="flex items-center justify-between pt-4 border-t">
              <Button variant="outline" type="button">
                {tActions('back')}
              </Button>
              <Button type="submit" className="bg-blue-600 hover:bg-blue-700">
                {tActions('continue')}
              </Button>
            </div>
          </form>
        </CardContent>
      </Card>

      {/* Floating Button */}
      <LanguageModeFloatingButton />

      {/* Demo Info */}
      <Card className="border-2 border-green-200 bg-green-50">
        <CardContent className="pt-6">
          <div className="text-center">
            <p className="font-medium text-green-900 mb-2">
              ✨ Modo Atual: {mode === 'simple' ? 'Linguagem Simples' : 'Linguagem Técnica'}
            </p>
            <p className="text-sm text-green-800">
              Todos os textos desta página se adaptam automaticamente ao modo escolhido!
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default AdaptiveFormExample;
