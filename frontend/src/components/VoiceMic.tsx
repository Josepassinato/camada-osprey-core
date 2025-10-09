import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Mic, MicOff, Volume2, VolumeX, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface VoiceMicProps {
  onTranscription?: (text: string, isPartial: boolean) => void;
  onAdvice?: (advice: any) => void;
  onError?: (error: string) => void;
  sessionId?: string;
  isEnabled?: boolean;
  className?: string;
}

interface AudioChunk {
  data: ArrayBuffer;
  timestamp: number;
}

export const VoiceMic: React.FC<VoiceMicProps> = ({
  onTranscription,
  onAdvice,
  onError,
  sessionId,
  isEnabled = true,
  className = ""
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isConnected, setIsConnected] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);
  const [connectionStatus, setConnectionStatus] = useState<'disconnected' | 'connecting' | 'connected'>('disconnected');
  
  const webSocketRef = useRef<WebSocket | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const audioChunksRef = useRef<AudioChunk[]>([]);
  
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectAttempts = useRef(0);
  const maxReconnectAttempts = 5;

  // Robust backend URL detection for preview environment
  const isPreview = typeof window !== 'undefined' && window.location.hostname.includes('preview.emergentagent.com');
  const backendUrl = isPreview 
    ? 'https://formfill-aid.preview.emergentagent.com'
    : (import.meta.env.VITE_BACKEND_URL || 'https://formfill-aid.preview.emergentagent.com');
  const wsUrl = `${backendUrl.replace('http', 'ws')}/ws/voice/${sessionId || 'default'}`;

  // Initialize WebSocket connection
  const connectWebSocket = useCallback(() => {
    if (webSocketRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setConnectionStatus('connecting');
    
    try {
      const ws = new WebSocket(wsUrl);
      
      ws.onopen = () => {
        console.log('Voice WebSocket connected');
        setIsConnected(true);
        setConnectionStatus('connected');
        reconnectAttempts.current = 0;
        
        if (reconnectTimeoutRef.current) {
          clearTimeout(reconnectTimeoutRef.current);
          reconnectTimeoutRef.current = null;
        }
      };
      
      ws.onmessage = (event) => {
        try {
          const message = JSON.parse(event.data);
          handleWebSocketMessage(message);
        } catch (error) {
          console.error('Error parsing WebSocket message:', error);
        }
      };
      
      ws.onclose = () => {
        console.log('Voice WebSocket disconnected');
        setIsConnected(false);
        setConnectionStatus('disconnected');
        webSocketRef.current = null;
        
        // Auto-reconnect
        if (reconnectAttempts.current < maxReconnectAttempts) {
          reconnectAttempts.current++;
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 10000);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connectWebSocket();
          }, delay);
        } else {
          onError?.('Conexão perdida. Recarregue a página para tentar novamente.');
        }
      };
      
      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
        onError?.('Erro de conexão com assistente de voz');
      };
      
      webSocketRef.current = ws;
      
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      setConnectionStatus('disconnected');
      onError?.('Falha ao conectar com assistente de voz');
    }
  }, [wsUrl, onError]);

  // Handle WebSocket messages
  const handleWebSocketMessage = (message: any) => {
    console.log('Received voice message:', message);
    
    switch (message.type) {
      case 'connection_established':
        console.log('Voice agent ready:', message.message);
        break;
        
      case 'voice_response':
      case 'guidance_response':
      case 'snapshot_received':
        if (message.advice) {
          onAdvice?.(message.advice);
          
          // Speak the advice if available
          if (message.advice.say) {
            speakText(message.advice.say);
          }
        }
        break;
        
      case 'transcription':
        onTranscription?.(message.text, message.isPartial);
        break;
        
      case 'error':
        console.error('Voice agent error:', message.message);
        onError?.(message.message || 'Erro no assistente de voz');
        break;
        
      default:
        console.log('Unknown message type:', message.type);
    }
  };

  // Send message to voice agent
  const sendMessage = useCallback((message: any) => {
    if (webSocketRef.current?.readyState === WebSocket.OPEN) {
      webSocketRef.current.send(JSON.stringify(message));
    } else {
      console.warn('WebSocket not connected, cannot send message');
    }
  }, []);

  // Start audio recording
  const startRecording = useCallback(async () => {
    try {
      // Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          sampleRate: 16000,
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true
        }
      });
      
      streamRef.current = stream;
      
      // Create audio context for processing
      audioContextRef.current = new (window.AudioContext || (window as any).webkitAudioContext)({
        sampleRate: 16000
      });
      
      // Create media recorder
      const mediaRecorder = new MediaRecorder(stream, {
        mimeType: 'audio/webm;codecs=opus'
      });
      
      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          // Convert to ArrayBuffer and store
          event.data.arrayBuffer().then(buffer => {
            audioChunksRef.current.push({
              data: buffer,
              timestamp: Date.now()
            });
            
            // Send audio data to backend (simplified for MVP)
            // In full implementation, would convert to PCM and stream in chunks
            if (audioChunksRef.current.length > 10) { // Send every ~1 second
              processAudioChunks();
            }
          });
        }
      };
      
      mediaRecorderRef.current = mediaRecorder;
      mediaRecorder.start(100); // Collect data every 100ms
      setIsRecording(true);
      
    } catch (error) {
      console.error('Failed to start recording:', error);
      onError?.('Falha ao acessar microfone. Verifique as permissões.');
    }
  }, [onError]);

  // Stop audio recording  
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      // Process remaining chunks
      if (audioChunksRef.current.length > 0) {
        processAudioChunks();
      }
    }
    
    // Clean up stream
    if (streamRef.current) {
      streamRef.current.getTracks().forEach(track => track.stop());
      streamRef.current = null;
    }
    
    // Clean up audio context
    if (audioContextRef.current) {
      audioContextRef.current.close();
      audioContextRef.current = null;
    }
  }, [isRecording]);

  // Process accumulated audio chunks
  const processAudioChunks = () => {
    if (audioChunksRef.current.length === 0) return;
    
    // Simulate audio processing and transcription
    // In full implementation, would convert audio and send via WebSocket
    const mockTranscription = "Audio recebido e processado"; // Placeholder
    
    // Send mock voice input to backend
    sendMessage({
      type: 'voice_input',
      transcription: mockTranscription,
      timestamp: Date.now()
    });
    
    // Clear processed chunks
    audioChunksRef.current = [];
  };

  // Text-to-speech using Web Speech API
  const speakText = useCallback((text: string) => {
    if ('speechSynthesis' in window) {
      // Cancel any ongoing speech
      window.speechSynthesis.cancel();
      
      const utterance = new SpeechSynthesisUtterance(text);
      utterance.lang = 'pt-BR';
      utterance.rate = 1.0;
      utterance.pitch = 1.0;
      utterance.volume = 1.0;
      
      utterance.onstart = () => {
        setIsPlaying(true);
      };
      
      utterance.onend = () => {
        setIsPlaying(false);
      };
      
      utterance.onerror = (error) => {
        console.error('Speech synthesis error:', error);
        setIsPlaying(false);
      };
      
      window.speechSynthesis.speak(utterance);
    } else {
      console.warn('Speech synthesis not supported');
      onError?.('Síntese de voz não suportada neste navegador');
    }
  }, [onError]);

  // Stop text-to-speech (barge-in)
  const stopSpeaking = useCallback(() => {
    if ('speechSynthesis' in window) {
      window.speechSynthesis.cancel();
      setIsPlaying(false);
    }
  }, []);

  // Send form snapshot to voice agent
  const sendSnapshot = useCallback((snapshot: any) => {
    sendMessage({
      type: 'snapshot',
      snapshot: snapshot,
      timestamp: Date.now()
    });
  }, [sendMessage]);

  // Request guidance from voice agent
  const requestGuidance = useCallback((requestType: string = 'general') => {
    sendMessage({
      type: 'request_guidance',
      request_type: requestType,
      timestamp: Date.now()
    });
  }, [sendMessage]);

  // Initialize connection on mount
  useEffect(() => {
    if (isEnabled && sessionId) {
      connectWebSocket();
    }
    
    return () => {
      // Cleanup on unmount
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      
      if (webSocketRef.current) {
        webSocketRef.current.close();
      }
      
      stopRecording();
      stopSpeaking();
    };
  }, [isEnabled, sessionId, connectWebSocket]);

  // Auto-reconnect on connection loss
  useEffect(() => {
    if (isEnabled && !isConnected && connectionStatus === 'disconnected') {
      const timer = setTimeout(() => {
        connectWebSocket();
      }, 2000);
      
      return () => clearTimeout(timer);
    }
  }, [isEnabled, isConnected, connectionStatus, connectWebSocket]);

  // Expose methods for parent components
  React.useImperativeHandle(React.forwardRef(() => null), () => ({
    sendSnapshot,
    requestGuidance,
    speakText,
    stopSpeaking,
    startRecording,
    stopRecording,
    isConnected,
    isRecording,
    isPlaying
  }), [sendSnapshot, requestGuidance, speakText, stopSpeaking, startRecording, stopRecording, isConnected, isRecording, isPlaying]);

  if (!isEnabled) {
    return null;
  }

  return (
    <div className={`voice-mic-component ${className}`}>
      <div className="flex items-center gap-2 p-2 bg-white border border-gray-200 rounded-lg shadow-sm">
        
        {/* Connection Status */}
        <div className="flex items-center gap-2">
          <div className={`w-2 h-2 rounded-full ${
            connectionStatus === 'connected' ? 'bg-green-500' : 
            connectionStatus === 'connecting' ? 'bg-orange-500' : 
            'bg-red-500'
          }`} />
          <span className="text-xs text-gray-600">
            {connectionStatus === 'connected' ? 'Conectado' : 
             connectionStatus === 'connecting' ? 'Conectando...' : 
             'Desconectado'}
          </span>
        </div>

        {/* Recording Controls */}
        <Button
          variant={isRecording ? "destructive" : "outline"}
          size="sm"
          onClick={isRecording ? stopRecording : startRecording}
          disabled={!isConnected}
          className="flex items-center gap-1"
        >
          {isRecording ? (
            <>
              <MicOff className="h-4 w-4" />
              <span className="text-xs">Parar</span>
            </>
          ) : (
            <>
              <Mic className="h-4 w-4" />
              <span className="text-xs">Gravar</span>
            </>
          )}
        </Button>

        {/* TTS Controls */}
        <Button
          variant="outline"
          size="sm"
          onClick={isPlaying ? stopSpeaking : () => requestGuidance('status')}
          disabled={!isConnected}
          className="flex items-center gap-1"
        >
          {isPlaying ? (
            <>
              <VolumeX className="h-4 w-4" />
              <span className="text-xs">Parar</span>
            </>
          ) : (
            <>
              <Volume2 className="h-4 w-4" />
              <span className="text-xs">Status</span>
            </>
          )}
        </Button>

        {/* Quick Actions */}
        <div className="flex items-center gap-1 border-l border-gray-200 pl-2">
          <Button
            variant="ghost"
            size="sm"
            onClick={() => requestGuidance('next_step')}
            disabled={!isConnected}
            className="text-xs"
          >
            Próximo
          </Button>
          <Button
            variant="ghost" 
            size="sm"
            onClick={() => requestGuidance('validate_current')}
            disabled={!isConnected}
            className="text-xs"
          >
            Validar
          </Button>
        </div>

        {/* Loading indicator */}
        {connectionStatus === 'connecting' && (
          <Loader2 className="h-4 w-4 animate-spin text-gray-500" />
        )}
      </div>
    </div>
  );
};

export default VoiceMic;