import React, { useState } from 'react';
import { ThumbsUp, ThumbsDown, Star, Send, X } from 'lucide-react';
import { Button } from '@/components/ui/button';
import axios from 'axios';

interface FeedbackWidgetProps {
  feedbackType: 'ai_response' | 'form_usability' | 'document_upload' | 'pdf_generation' | 'general_experience';
  metadata?: Record<string, any>;
  onFeedbackSubmitted?: () => void;
  compact?: boolean;
}

const FeedbackWidget: React.FC<FeedbackWidgetProps> = ({
  feedbackType,
  metadata,
  onFeedbackSubmitted,
  compact = false
}) => {
  const [showFullForm, setShowFullForm] = useState(false);
  const [thumbs, setThumbs] = useState<'up' | 'down' | null>(null);
  const [rating, setRating] = useState<number>(0);
  const [comment, setComment] = useState('');
  const [submitted, setSubmitted] = useState(false);
  const [submitting, setSubmitting] = useState(false);

  const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || process.env.REACT_APP_BACKEND_URL;

  const handleThumbsClick = async (value: 'up' | 'down') => {
    setThumbs(value);
    
    // Se thumbs down, mostrar form completo
    if (value === 'down') {
      setShowFullForm(true);
    } else {
      // Se thumbs up, enviar imediatamente
      await submitFeedback(value, null, '');
    }
  };

  const submitFeedback = async (
    thumbsValue: 'up' | 'down' | null,
    ratingValue: number | null,
    commentValue: string
  ) => {
    try {
      setSubmitting(true);
      
      const token = localStorage.getItem('token');
      
      const payload: any = {
        feedback_type: feedbackType,
        metadata: metadata || {}
      };
      
      if (thumbsValue) payload.thumbs = thumbsValue;
      if (ratingValue && ratingValue > 0) payload.rating = ratingValue;
      if (commentValue) payload.comment = commentValue;
      
      await axios.post(
        `${BACKEND_URL}/feedback/submit`,
        payload,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );
      
      setSubmitted(true);
      
      // Callback
      if (onFeedbackSubmitted) {
        onFeedbackSubmitted();
      }
      
      // Auto-close após 2 segundos
      setTimeout(() => {
        setShowFullForm(false);
      }, 2000);
      
    } catch (error) {
      console.error('Error submitting feedback:', error);
      alert('Erro ao enviar feedback. Tente novamente.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleFullFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await submitFeedback(thumbs, rating, comment);
  };

  // Se já submeteu, mostrar mensagem de sucesso
  if (submitted) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-lg p-3 text-center">
        <p className="text-green-700 font-medium">✅ Obrigado pelo seu feedback!</p>
      </div>
    );
  }

  // Modo compacto: apenas thumbs
  if (compact && !showFullForm) {
    return (
      <div className="flex items-center gap-2 text-sm text-gray-600">
        <span>Isso foi útil?</span>
        <button
          onClick={() => handleThumbsClick('up')}
          className={`p-1.5 rounded hover:bg-gray-100 transition-colors ${
            thumbs === 'up' ? 'bg-green-100 text-green-600' : 'text-gray-400'
          }`}
          disabled={submitting}
        >
          <ThumbsUp className="w-4 h-4" />
        </button>
        <button
          onClick={() => handleThumbsClick('down')}
          className={`p-1.5 rounded hover:bg-gray-100 transition-colors ${
            thumbs === 'down' ? 'bg-red-100 text-red-600' : 'text-gray-400'
          }`}
          disabled={submitting}
        >
          <ThumbsDown className="w-4 h-4" />
        </button>
      </div>
    );
  }

  // Form completo
  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
      <div className="flex justify-between items-start mb-4">
        <h3 className="font-semibold text-gray-900">Como foi sua experiência?</h3>
        <button
          onClick={() => setShowFullForm(false)}
          className="text-gray-400 hover:text-gray-600"
        >
          <X className="w-5 h-5" />
        </button>
      </div>

      <form onSubmit={handleFullFormSubmit} className="space-y-4">
        {/* Thumbs Up/Down */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Avaliação Geral
          </label>
          <div className="flex gap-4">
            <button
              type="button"
              onClick={() => setThumbs('up')}
              className={`flex-1 p-3 rounded-lg border-2 transition-all ${
                thumbs === 'up'
                  ? 'border-green-500 bg-green-50 text-green-700'
                  : 'border-gray-200 hover:border-green-300'
              }`}
            >
              <ThumbsUp className={`w-6 h-6 mx-auto mb-1 ${thumbs === 'up' ? 'fill-current' : ''}`} />
              <span className="text-sm font-medium">Bom</span>
            </button>
            <button
              type="button"
              onClick={() => setThumbs('down')}
              className={`flex-1 p-3 rounded-lg border-2 transition-all ${
                thumbs === 'down'
                  ? 'border-red-500 bg-red-50 text-red-700'
                  : 'border-gray-200 hover:border-red-300'
              }`}
            >
              <ThumbsDown className={`w-6 h-6 mx-auto mb-1 ${thumbs === 'down' ? 'fill-current' : ''}`} />
              <span className="text-sm font-medium">Ruim</span>
            </button>
          </div>
        </div>

        {/* Rating com estrelas */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Nota (1-5 estrelas)
          </label>
          <div className="flex gap-2">
            {[1, 2, 3, 4, 5].map((star) => (
              <button
                key={star}
                type="button"
                onClick={() => setRating(star)}
                className="focus:outline-none transition-transform hover:scale-110"
              >
                <Star
                  className={`w-8 h-8 ${
                    star <= rating
                      ? 'fill-yellow-400 text-yellow-400'
                      : 'text-gray-300'
                  }`}
                />
              </button>
            ))}
          </div>
          {rating > 0 && (
            <p className="text-sm text-gray-600 mt-1">
              {rating === 5 && '⭐ Excelente!'}
              {rating === 4 && '😊 Muito bom!'}
              {rating === 3 && '👍 Bom'}
              {rating === 2 && '😐 Poderia melhorar'}
              {rating === 1 && '😞 Precisa melhorar muito'}
            </p>
          )}
        </div>

        {/* Comentário */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Comentário (opcional)
          </label>
          <textarea
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            placeholder="Conte-nos mais sobre sua experiência..."
            className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
            rows={3}
          />
        </div>

        {/* Botões */}
        <div className="flex gap-3">
          <Button
            type="submit"
            disabled={submitting || (!thumbs && rating === 0)}
            className="flex-1"
          >
            {submitting ? (
              <>Enviando...</>
            ) : (
              <>
                <Send className="w-4 h-4 mr-2" />
                Enviar Feedback
              </>
            )}
          </Button>
          <Button
            type="button"
            variant="outline"
            onClick={() => setShowFullForm(false)}
          >
            Cancelar
          </Button>
        </div>
      </form>
    </div>
  );
};

export default FeedbackWidget;
