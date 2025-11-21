import React from 'react';
import { useLocale } from '@/contexts/LocaleContext';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Globe } from 'lucide-react';

interface LanguageSelectorProps {
  variant?: 'default' | 'compact';
}

const LanguageSelector: React.FC<LanguageSelectorProps> = ({ variant = 'default' }) => {
  const { locale, setLocale, availableLocales, localeName } = useLocale();

  return (
    <div className={`flex items-center gap-2 ${variant === 'compact' ? '' : 'w-full'}`}>
      {variant === 'default' && (
        <Globe className="h-5 w-5 text-gray-600" />
      )}
      
      <Select value={locale} onValueChange={setLocale}>
        <SelectTrigger className={variant === 'compact' ? 'w-[180px]' : 'w-full'}>
          <SelectValue>
            <div className="flex items-center gap-2">
              <span>{availableLocales.find(l => l.code === locale)?.flag}</span>
              <span>{localeName}</span>
            </div>
          </SelectValue>
        </SelectTrigger>
        <SelectContent>
          {availableLocales.map((lang) => (
            <SelectItem key={lang.code} value={lang.code}>
              <div className="flex items-center gap-2">
                <span className="text-lg">{lang.flag}</span>
                <span>{lang.nativeName}</span>
              </div>
            </SelectItem>
          ))}
        </SelectContent>
      </Select>
      
      {variant === 'default' && (
        <p className="text-xs text-gray-500 ml-2">
          {locale !== 'en' && (
            <span className="text-green-600">
              ✓ Tradução automática para inglês
            </span>
          )}
        </p>
      )}
    </div>
  );
};

export default LanguageSelector;
