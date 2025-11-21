import React, { createContext, useContext, useState, useEffect } from 'react';

export type SupportedLocale = 'pt' | 'en' | 'es' | 'fr' | 'de' | 'it' | 'zh' | 'ja' | 'ko' | 'ar' | 'ru';

interface LocaleContextType {
  locale: SupportedLocale;
  setLocale: (locale: SupportedLocale) => void;
  localeName: string;
  availableLocales: { code: SupportedLocale; name: string; nativeName: string; flag: string }[];
  translationEnabled: boolean;
}

const locales = [
  { code: 'pt' as SupportedLocale, name: 'Portuguese', nativeName: 'Português (Brasil)', flag: '🇧🇷' },
  { code: 'en' as SupportedLocale, name: 'English', nativeName: 'English (US)', flag: '🇺🇸' },
  { code: 'es' as SupportedLocale, name: 'Spanish', nativeName: 'Español', flag: '🇪🇸' },
  { code: 'fr' as SupportedLocale, name: 'French', nativeName: 'Français', flag: '🇫🇷' },
  { code: 'de' as SupportedLocale, name: 'German', nativeName: 'Deutsch', flag: '🇩🇪' },
  { code: 'it' as SupportedLocale, name: 'Italian', nativeName: 'Italiano', flag: '🇮🇹' },
  { code: 'zh' as SupportedLocale, name: 'Chinese', nativeName: '中文 (简体)', flag: '🇨🇳' },
  { code: 'ja' as SupportedLocale, name: 'Japanese', nativeName: '日本語', flag: '🇯🇵' },
  { code: 'ko' as SupportedLocale, name: 'Korean', nativeName: '한국어', flag: '🇰🇷' },
  { code: 'ar' as SupportedLocale, name: 'Arabic', nativeName: 'العربية', flag: '🇸🇦' },
  { code: 'ru' as SupportedLocale, name: 'Russian', nativeName: 'Русский', flag: '🇷🇺' }
];

const LocaleContext = createContext<LocaleContextType | undefined>(undefined);

export const LocaleProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [locale, setLocaleState] = useState<SupportedLocale>('pt');

  // Carregar idioma salvo do localStorage
  useEffect(() => {
    const saved = localStorage.getItem('osprey_locale');
    if (saved && locales.find(l => l.code === saved)) {
      setLocaleState(saved as SupportedLocale);
    }
  }, []);

  const setLocale = (newLocale: SupportedLocale) => {
    setLocaleState(newLocale);
    localStorage.setItem('osprey_locale', newLocale);
    
    // Log para debug
    console.log(`🌍 Idioma alterado para: ${newLocale}`);
  };

  const currentLocale = locales.find(l => l.code === locale) || locales[0];

  return (
    <LocaleContext.Provider 
      value={{
        locale,
        setLocale,
        localeName: currentLocale.nativeName,
        availableLocales: locales,
        translationEnabled: true
      }}
    >
      {children}
    </LocaleContext.Provider>
  );
};

export const useLocale = () => {
  const context = useContext(LocaleContext);
  if (!context) {
    throw new Error('useLocale must be used within LocaleProvider');
  }
  return context;
};
