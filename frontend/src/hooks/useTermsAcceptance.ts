import { useState, useEffect } from 'react';

const TERMS_ACCEPTANCE_KEY = 'osprey_terms_accepted';
const TERMS_VERSION = '2025.1'; // Update this when terms change

export const useTermsAcceptance = () => {
  const [showTermsModal, setShowTermsModal] = useState(false);
  const [termsAccepted, setTermsAccepted] = useState(false);

  useEffect(() => {
    // Check if user has already accepted the current version of terms
    const acceptedVersion = localStorage.getItem(TERMS_ACCEPTANCE_KEY);
    
    if (acceptedVersion === TERMS_VERSION) {
      setTermsAccepted(true);
    } else {
      // Show modal if terms haven't been accepted or version is outdated
      setShowTermsModal(true);
    }
  }, []);

  const acceptTerms = () => {
    localStorage.setItem(TERMS_ACCEPTANCE_KEY, TERMS_VERSION);
    setTermsAccepted(true);
    setShowTermsModal(false);
  };

  const declineTerms = () => {
    // Redirect to a different page or show a message
    // For now, we'll just close the modal but keep terms as not accepted
    setShowTermsModal(false);
    // Optionally redirect to an external site or show an alternative page
    window.location.href = 'https://www.uscis.gov/';
  };

  const resetTermsAcceptance = () => {
    localStorage.removeItem(TERMS_ACCEPTANCE_KEY);
    setTermsAccepted(false);
    setShowTermsModal(true);
  };

  return {
    showTermsModal,
    termsAccepted,
    acceptTerms,
    declineTerms,
    resetTermsAcceptance,
  };
};