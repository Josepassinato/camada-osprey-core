import React, { useState } from 'react';

interface OnboardingWizardProps {
  firmName: string;
  onComplete: () => void;
}

const VISA_TYPES = [
  'H-1B', 'L-1', 'O-1', 'EB-1', 'EB-2 NIW', 'EB-3',
  'E-2', 'TN', 'H-2B', 'PERM', 'I-485', 'I-130',
  'K-1', 'Asylum', 'DACA', 'Naturalization',
];

const TEAM_SIZES = [
  'Just me',
  '2–5 attorneys',
  '6–15 attorneys',
  '16–50 attorneys',
  '50+ attorneys',
];

const REFERRAL_SOURCES = [
  'Google search',
  'LinkedIn',
  'Colleague referral',
  'Conference / event',
  'Legal publication',
  'Other',
];

const API_URL = import.meta.env.VITE_BACKEND_URL || '';

export default function OnboardingWizard({ firmName, onComplete }: OnboardingWizardProps) {
  const [step, setStep] = useState(0);
  const [selectedVisas, setSelectedVisas] = useState<string[]>([]);
  const [teamSize, setTeamSize] = useState('');
  const [referral, setReferral] = useState('');
  const [saving, setSaving] = useState(false);

  const totalSteps = 4;

  const toggleVisa = (v: string) => {
    setSelectedVisas((prev) =>
      prev.includes(v) ? prev.filter((x) => x !== v) : [...prev, v]
    );
  };

  const canAdvance = () => {
    if (step === 1) return selectedVisas.length > 0;
    if (step === 2) return !!teamSize;
    if (step === 3) return !!referral;
    return true;
  };

  const handleFinish = async () => {
    setSaving(true);
    try {
      const token = localStorage.getItem('imigrai_token');
      await fetch(`${API_URL}/api/auth/b2b/onboarding-complete`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          visa_types: selectedVisas,
          team_size: teamSize,
          referral_source: referral,
        }),
      });
      onComplete();
    } catch {
      onComplete();
    }
  };

  const renderStep = () => {
    switch (step) {
      case 0:
        return (
          <div style={{ textAlign: 'center' }}>
            <div style={s.iconCircle}>
              <span style={{ fontSize: 32 }}>I</span>
            </div>
            <h2 style={s.heading}>Welcome, {firmName}</h2>
            <p style={s.desc}>
              Let's set up your Imigrai workspace. This takes about 30 seconds
              and helps us tailor the experience to your practice.
            </p>
          </div>
        );

      case 1:
        return (
          <>
            <h2 style={s.heading}>What visa types does your firm handle?</h2>
            <p style={s.desc}>Select all that apply. You can change this later.</p>
            <div style={s.chipGrid}>
              {VISA_TYPES.map((v) => (
                <button
                  key={v}
                  onClick={() => toggleVisa(v)}
                  style={{
                    ...s.chip,
                    ...(selectedVisas.includes(v) ? s.chipActive : {}),
                  }}
                >
                  {v}
                </button>
              ))}
            </div>
          </>
        );

      case 2:
        return (
          <>
            <h2 style={s.heading}>How large is your team?</h2>
            <p style={s.desc}>This helps us configure collaboration features.</p>
            <div style={s.optionList}>
              {TEAM_SIZES.map((size) => (
                <button
                  key={size}
                  onClick={() => setTeamSize(size)}
                  style={{
                    ...s.optionBtn,
                    ...(teamSize === size ? s.optionActive : {}),
                  }}
                >
                  {size}
                </button>
              ))}
            </div>
          </>
        );

      case 3:
        return (
          <>
            <h2 style={s.heading}>How did you hear about Imigrai?</h2>
            <p style={s.desc}>Just curious — helps us reach more firms like yours.</p>
            <div style={s.optionList}>
              {REFERRAL_SOURCES.map((src) => (
                <button
                  key={src}
                  onClick={() => setReferral(src)}
                  style={{
                    ...s.optionBtn,
                    ...(referral === src ? s.optionActive : {}),
                  }}
                >
                  {src}
                </button>
              ))}
            </div>
          </>
        );

      default:
        return null;
    }
  };

  return (
    <div style={s.container}>
      <div style={s.card}>
        {/* Progress bar */}
        <div style={s.progressTrack}>
          <div
            style={{
              ...s.progressFill,
              width: `${((step + 1) / totalSteps) * 100}%`,
            }}
          />
        </div>

        <div style={{ padding: '36px 32px 32px' }}>
          {renderStep()}

          <div style={s.actions}>
            {step > 0 && (
              <button onClick={() => setStep(step - 1)} style={s.backBtn}>
                Back
              </button>
            )}
            {step < totalSteps - 1 ? (
              <button
                onClick={() => setStep(step + 1)}
                disabled={!canAdvance()}
                style={{
                  ...s.nextBtn,
                  opacity: canAdvance() ? 1 : 0.4,
                  cursor: canAdvance() ? 'pointer' : 'not-allowed',
                }}
              >
                {step === 0 ? "Let's go" : 'Next'}
              </button>
            ) : (
              <button
                onClick={handleFinish}
                disabled={!canAdvance() || saving}
                style={{
                  ...s.nextBtn,
                  opacity: canAdvance() && !saving ? 1 : 0.4,
                  cursor: canAdvance() && !saving ? 'pointer' : 'not-allowed',
                }}
              >
                {saving ? 'Setting up...' : 'Enter dashboard'}
              </button>
            )}
          </div>
        </div>
      </div>

      <style>{`
        @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;500;600;700&display=swap');
        body { margin: 0; }
        button:hover:not(:disabled) { opacity: 0.9; }
      `}</style>
    </div>
  );
}

const s: Record<string, React.CSSProperties> = {
  container: {
    minHeight: '100vh',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#060d14',
    padding: 20,
  },
  card: {
    width: '100%',
    maxWidth: 520,
    backgroundColor: 'rgba(255,255,255,0.03)',
    border: '1px solid rgba(201,168,76,0.15)',
    borderRadius: 16,
    overflow: 'hidden',
  },
  progressTrack: {
    height: 3,
    backgroundColor: 'rgba(255,255,255,0.06)',
  },
  progressFill: {
    height: '100%',
    backgroundColor: '#C9A84C',
    transition: 'width 0.3s ease',
  },
  iconCircle: {
    width: 64,
    height: 64,
    borderRadius: 16,
    backgroundColor: '#C9A84C',
    color: '#060d14',
    display: 'inline-flex',
    alignItems: 'center',
    justifyContent: 'center',
    fontWeight: 700,
    fontFamily: "'Playfair Display', serif",
    marginBottom: 20,
  },
  heading: {
    fontFamily: "'Playfair Display', serif",
    fontSize: 22,
    fontWeight: 600,
    color: '#C9A84C',
    margin: '0 0 8px',
  },
  desc: {
    fontSize: 14,
    color: 'rgba(255,255,255,0.5)',
    margin: '0 0 24px',
    lineHeight: 1.5,
  },
  chipGrid: {
    display: 'flex',
    flexWrap: 'wrap' as const,
    gap: 8,
  },
  chip: {
    padding: '8px 16px',
    borderRadius: 20,
    border: '1px solid rgba(255,255,255,0.12)',
    backgroundColor: 'rgba(255,255,255,0.04)',
    color: 'rgba(255,255,255,0.7)',
    fontSize: 13,
    cursor: 'pointer',
    transition: 'all 0.15s ease',
  },
  chipActive: {
    backgroundColor: 'rgba(201,168,76,0.15)',
    borderColor: '#C9A84C',
    color: '#C9A84C',
  },
  optionList: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: 8,
  },
  optionBtn: {
    padding: '14px 18px',
    borderRadius: 10,
    border: '1px solid rgba(255,255,255,0.1)',
    backgroundColor: 'rgba(255,255,255,0.03)',
    color: 'rgba(255,255,255,0.7)',
    fontSize: 14,
    cursor: 'pointer',
    textAlign: 'left' as const,
    transition: 'all 0.15s ease',
  },
  optionActive: {
    backgroundColor: 'rgba(201,168,76,0.12)',
    borderColor: '#C9A84C',
    color: '#C9A84C',
  },
  actions: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 32,
    gap: 12,
  },
  backBtn: {
    padding: '12px 20px',
    borderRadius: 8,
    border: '1px solid rgba(255,255,255,0.1)',
    backgroundColor: 'transparent',
    color: 'rgba(255,255,255,0.5)',
    fontSize: 14,
    cursor: 'pointer',
  },
  nextBtn: {
    padding: '12px 28px',
    borderRadius: 8,
    border: 'none',
    backgroundColor: '#C9A84C',
    color: '#060d14',
    fontSize: 15,
    fontWeight: 600,
    cursor: 'pointer',
    marginLeft: 'auto',
  },
};
