import { useState, useEffect, useRef, useCallback } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Alert, AlertDescription } from "@/components/ui/alert";
import {
  Film,
  Upload,
  Scissors,
  Type,
  Volume2,
  VolumeX,
  RotateCw,
  Maximize2,
  Palette,
  Download,
  Play,
  Pause,
  SkipBack,
  SkipForward,
  Layers,
  Image,
  Clock,
  Zap,
  ChevronRight,
  Plus,
  Trash2,
  Settings,
  Wand2,
  Subtitles,
  Crop,
  Move,
  Droplets,
} from "lucide-react";
import { makeApiCall, getBackendUrl } from "@/utils/api";

// ===== Types =====

interface VideoSource {
  source_id: string;
  filename: string;
  label: string;
  file_path: string;
  mime_type: string;
  file_size: number;
  probe?: VideoProbe;
  uploaded_at: string;
  generated?: boolean;
}

interface VideoProbe {
  duration: number;
  width: number;
  height: number;
  fps: number;
  video_codec: string;
  audio_codec?: string;
  bitrate?: number;
  file_size: number;
}

interface VideoProject {
  id: string;
  name: string;
  description?: string;
  status: string;
  sources: VideoSource[];
  operations: OperationRecord[];
  output?: { file_path: string; format: string; probe?: VideoProbe };
  created_at: string;
  updated_at: string;
}

interface OperationRecord {
  operation_id: string;
  source_id: string;
  operation: string;
  params: Record<string, unknown>;
  output_path: string;
  executed_at: string;
}

type ToolType =
  | "trim"
  | "resize"
  | "crop"
  | "rotate"
  | "speed"
  | "overlay_text"
  | "filter_apply"
  | "audio_volume"
  | "watermark"
  | "subtitle"
  | "thumbnail"
  | "audio_extract";

interface ToolConfig {
  icon: React.ReactNode;
  label: string;
  description: string;
  color: string;
}

// ===== Constants =====

const TOOLS: Record<ToolType, ToolConfig> = {
  trim: {
    icon: <Scissors className="w-5 h-5" />,
    label: "Cortar",
    description: "Recortar trecho do v\u00eddeo",
    color: "text-blue-500",
  },
  resize: {
    icon: <Maximize2 className="w-5 h-5" />,
    label: "Redimensionar",
    description: "Alterar resolu\u00e7\u00e3o",
    color: "text-green-500",
  },
  crop: {
    icon: <Crop className="w-5 h-5" />,
    label: "Recortar \u00c1rea",
    description: "Cortar regi\u00e3o espec\u00edfica",
    color: "text-yellow-500",
  },
  rotate: {
    icon: <RotateCw className="w-5 h-5" />,
    label: "Rotacionar",
    description: "Girar o v\u00eddeo",
    color: "text-purple-500",
  },
  speed: {
    icon: <Zap className="w-5 h-5" />,
    label: "Velocidade",
    description: "Acelerar ou desacelerar",
    color: "text-orange-500",
  },
  overlay_text: {
    icon: <Type className="w-5 h-5" />,
    label: "Texto",
    description: "Adicionar texto sobre o v\u00eddeo",
    color: "text-pink-500",
  },
  filter_apply: {
    icon: <Palette className="w-5 h-5" />,
    label: "Filtros",
    description: "Aplicar filtros visuais",
    color: "text-indigo-500",
  },
  audio_volume: {
    icon: <Volume2 className="w-5 h-5" />,
    label: "Volume",
    description: "Ajustar volume do \u00e1udio",
    color: "text-teal-500",
  },
  watermark: {
    icon: <Droplets className="w-5 h-5" />,
    label: "Marca d'\u00e1gua",
    description: "Adicionar marca d'\u00e1gua",
    color: "text-cyan-500",
  },
  subtitle: {
    icon: <Subtitles className="w-5 h-5" />,
    label: "Legendas",
    description: "Adicionar legendas",
    color: "text-amber-500",
  },
  thumbnail: {
    icon: <Image className="w-5 h-5" />,
    label: "Thumbnail",
    description: "Extrair frame como imagem",
    color: "text-rose-500",
  },
  audio_extract: {
    icon: <VolumeX className="w-5 h-5" />,
    label: "Extrair \u00c1udio",
    description: "Extrair faixa de \u00e1udio",
    color: "text-gray-500",
  },
};

const FILTERS = [
  { id: "grayscale", label: "Preto & Branco", emoji: "\u26ab" },
  { id: "sepia", label: "S\u00e9pia", emoji: "\ud83d\udfe4" },
  { id: "blur", label: "Desfoque", emoji: "\ud83c\udf2b\ufe0f" },
  { id: "sharpen", label: "N\u00edtido", emoji: "\ud83d\udd2a" },
  { id: "brightness", label: "Brilho", emoji: "\u2600\ufe0f" },
  { id: "contrast", label: "Contraste", emoji: "\ud83c\udf13" },
  { id: "saturation", label: "Satura\u00e7\u00e3o", emoji: "\ud83c\udf08" },
];

const RESOLUTIONS = [
  { value: "360p", label: "360p", desc: "640\u00d7360" },
  { value: "480p", label: "480p", desc: "854\u00d7480" },
  { value: "720p", label: "HD 720p", desc: "1280\u00d7720" },
  { value: "1080p", label: "Full HD", desc: "1920\u00d71080" },
  { value: "1440p", label: "2K", desc: "2560\u00d71440" },
  { value: "2160p", label: "4K", desc: "3840\u00d72160" },
];

// ===== Helpers =====

function formatDuration(seconds: number): string {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}

function formatFileSize(bytes: number): string {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(0)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

// ===== Component =====

const VideoEditor = () => {
  // State
  const [projects, setProjects] = useState<VideoProject[]>([]);
  const [currentProject, setCurrentProject] = useState<VideoProject | null>(null);
  const [selectedSource, setSelectedSource] = useState<VideoSource | null>(null);
  const [activeTool, setActiveTool] = useState<ToolType | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [showNewProject, setShowNewProject] = useState(false);
  const [newProjectName, setNewProjectName] = useState("");

  // Tool-specific state
  const [trimStart, setTrimStart] = useState(0);
  const [trimEnd, setTrimEnd] = useState(10);
  const [selectedResolution, setSelectedResolution] = useState("1080p");
  const [rotateAngle, setRotateAngle] = useState(90);
  const [speedFactor, setSpeedFactor] = useState(1.0);
  const [overlayText, setOverlayText] = useState("");
  const [textX, setTextX] = useState(50);
  const [textY, setTextY] = useState(50);
  const [textSize, setTextSize] = useState(36);
  const [textColor, setTextColor] = useState("white");
  const [selectedFilter, setSelectedFilter] = useState("grayscale");
  const [filterIntensity, setFilterIntensity] = useState(1.0);
  const [audioVolume, setAudioVolume] = useState(1.0);
  const [watermarkText, setWatermarkText] = useState("");
  const [watermarkPosition, setWatermarkPosition] = useState("bottom_right");
  const [watermarkOpacity, setWatermarkOpacity] = useState(0.5);
  const [cropX, setCropX] = useState(0);
  const [cropY, setCropY] = useState(0);
  const [cropW, setCropW] = useState(1280);
  const [cropH, setCropH] = useState(720);
  const [thumbnailTime, setThumbnailTime] = useState(0);

  const fileInputRef = useRef<HTMLInputElement>(null);

  // ===== API Calls =====

  const fetchProjects = useCallback(async () => {
    try {
      setIsLoading(true);
      setError("");
      const data = await makeApiCall("/video/projects", "GET");
      setProjects(data.projects || []);
    } catch (err: any) {
      console.warn("Video API not available:", err.message);
      setProjects([]);
      if (err.message?.includes("Failed to fetch") || err.message?.includes("NetworkError")) {
        setError("Backend n\u00e3o dispon\u00edvel. Inicie o servidor: cd backend && python3 server.py");
      } else {
        setError(err.message);
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProjects();
  }, [fetchProjects]);

  const createProject = async () => {
    if (!newProjectName.trim()) return;
    try {
      setIsLoading(true);
      const data = await makeApiCall("/video/projects", "POST", {
        name: newProjectName.trim(),
      });
      setShowNewProject(false);
      setNewProjectName("");
      await fetchProjects();
      // Load the new project
      const project = await makeApiCall(`/video/projects/${data.id}`, "GET");
      setCurrentProject(project);
      setSuccessMsg("Projeto criado com sucesso!");
      setTimeout(() => setSuccessMsg(""), 3000);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const loadProject = async (projectId: string) => {
    try {
      setIsLoading(true);
      const project = await makeApiCall(`/video/projects/${projectId}`, "GET");
      setCurrentProject(project);
      setSelectedSource(null);
      setActiveTool(null);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  const deleteProject = async (projectId: string) => {
    try {
      await makeApiCall(`/video/projects/${projectId}`, "DELETE");
      if (currentProject?.id === projectId) {
        setCurrentProject(null);
        setSelectedSource(null);
      }
      await fetchProjects();
      setSuccessMsg("Projeto exclu\u00eddo");
      setTimeout(() => setSuccessMsg(""), 3000);
    } catch (err: any) {
      setError(err.message);
    }
  };

  const uploadSource = async (file: File) => {
    if (!currentProject) return;
    try {
      setIsProcessing(true);
      setError("");

      const formData = new FormData();
      formData.append("file", file);
      formData.append("label", file.name);

      const token = localStorage.getItem("osprey_token");
      const response = await fetch(
        `${getBackendUrl()}/api/video/projects/${currentProject.id}/sources`,
        {
          method: "POST",
          headers: {
            ...(token && { Authorization: `Bearer ${token}` }),
          },
          body: formData,
        }
      );

      if (!response.ok) {
        const err = await response.json().catch(() => ({}));
        throw new Error(err.detail || "Upload failed");
      }

      await loadProject(currentProject.id);
      setSuccessMsg("V\u00eddeo enviado com sucesso!");
      setTimeout(() => setSuccessMsg(""), 3000);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const executeOperation = async () => {
    if (!currentProject || !selectedSource || !activeTool) return;

    let params: Record<string, unknown> = {};

    switch (activeTool) {
      case "trim":
        params = { start_time: trimStart, end_time: trimEnd };
        break;
      case "resize":
        params = { resolution: selectedResolution };
        break;
      case "crop":
        params = { x: cropX, y: cropY, width: cropW, height: cropH };
        break;
      case "rotate":
        params = { angle: rotateAngle };
        break;
      case "speed":
        params = { factor: speedFactor, adjust_audio: true };
        break;
      case "overlay_text":
        params = {
          text: overlayText,
          x: textX,
          y: textY,
          font_size: textSize,
          font_color: textColor,
        };
        break;
      case "filter_apply":
        params = { filter_name: selectedFilter, intensity: filterIntensity };
        break;
      case "audio_volume":
        params = { volume: audioVolume };
        break;
      case "watermark":
        params = {
          text: watermarkText,
          position: watermarkPosition,
          opacity: watermarkOpacity,
        };
        break;
      case "thumbnail":
        params = { time: thumbnailTime };
        break;
      case "audio_extract":
      case "subtitle":
        break;
    }

    try {
      setIsProcessing(true);
      setError("");

      await makeApiCall(
        `/video/projects/${currentProject.id}/operations`,
        "POST",
        {
          source_id: selectedSource.source_id,
          operation: activeTool,
          params,
        }
      );

      await loadProject(currentProject.id);
      setSuccessMsg(`Opera\u00e7\u00e3o "${TOOLS[activeTool].label}" aplicada com sucesso!`);
      setTimeout(() => setSuccessMsg(""), 3000);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  const exportVideo = async (format = "mp4") => {
    if (!currentProject) return;
    try {
      setIsProcessing(true);
      const result = await makeApiCall(
        `/video/projects/${currentProject.id}/export`,
        "POST",
        {
          format,
          video_codec: "h264",
          audio_codec: "aac",
        }
      );
      setSuccessMsg(`V\u00eddeo exportado: ${result.output_path}`);
      setTimeout(() => setSuccessMsg(""), 5000);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsProcessing(false);
    }
  };

  // ===== Render Helpers =====

  const renderToolPanel = () => {
    if (!activeTool) return null;

    const toolPanels: Record<string, React.ReactNode> = {
      trim: (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              In\u00edcio (segundos)
            </label>
            <input
              type="number"
              min={0}
              step={0.5}
              value={trimStart}
              onChange={(e) => setTrimStart(parseFloat(e.target.value) || 0)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Fim (segundos)
            </label>
            <input
              type="number"
              min={0}
              step={0.5}
              value={trimEnd}
              onChange={(e) => setTrimEnd(parseFloat(e.target.value) || 0)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
            />
          </div>
          {selectedSource?.probe && (
            <p className="text-xs text-gray-500">
              Dura\u00e7\u00e3o total: {formatDuration(selectedSource.probe.duration)}
            </p>
          )}
        </div>
      ),

      resize: (
        <div className="space-y-2">
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Resolu\u00e7\u00e3o
          </label>
          {RESOLUTIONS.map((res) => (
            <button
              key={res.value}
              onClick={() => setSelectedResolution(res.value)}
              className={`w-full text-left px-3 py-2 rounded-lg border transition-colors ${
                selectedResolution === res.value
                  ? "border-green-500 bg-green-50 text-green-700"
                  : "border-gray-200 hover:border-gray-300"
              }`}
            >
              <span className="font-medium">{res.label}</span>
              <span className="text-xs text-gray-500 ml-2">{res.desc}</span>
            </button>
          ))}
        </div>
      ),

      crop: (
        <div className="grid grid-cols-2 gap-3">
          <div>
            <label className="block text-xs text-gray-600 mb-1">X</label>
            <input type="number" value={cropX} onChange={(e) => setCropX(parseInt(e.target.value) || 0)} className="w-full px-2 py-1.5 border rounded text-sm" />
          </div>
          <div>
            <label className="block text-xs text-gray-600 mb-1">Y</label>
            <input type="number" value={cropY} onChange={(e) => setCropY(parseInt(e.target.value) || 0)} className="w-full px-2 py-1.5 border rounded text-sm" />
          </div>
          <div>
            <label className="block text-xs text-gray-600 mb-1">Largura</label>
            <input type="number" value={cropW} onChange={(e) => setCropW(parseInt(e.target.value) || 0)} className="w-full px-2 py-1.5 border rounded text-sm" />
          </div>
          <div>
            <label className="block text-xs text-gray-600 mb-1">Altura</label>
            <input type="number" value={cropH} onChange={(e) => setCropH(parseInt(e.target.value) || 0)} className="w-full px-2 py-1.5 border rounded text-sm" />
          </div>
        </div>
      ),

      rotate: (
        <div className="space-y-3">
          <label className="block text-sm font-medium text-gray-700">
            \u00c2ngulo de Rota\u00e7\u00e3o
          </label>
          <div className="flex gap-2">
            {[90, 180, 270].map((angle) => (
              <button
                key={angle}
                onClick={() => setRotateAngle(angle)}
                className={`flex-1 py-2 px-3 rounded-lg border text-sm font-medium transition-colors ${
                  rotateAngle === angle
                    ? "border-purple-500 bg-purple-50 text-purple-700"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                {angle}\u00b0
              </button>
            ))}
          </div>
        </div>
      ),

      speed: (
        <div className="space-y-4">
          <label className="block text-sm font-medium text-gray-700">
            Velocidade: {speedFactor.toFixed(2)}x
          </label>
          <input
            type="range"
            min={0.25}
            max={4}
            step={0.25}
            value={speedFactor}
            onChange={(e) => setSpeedFactor(parseFloat(e.target.value))}
            className="w-full accent-orange-500"
          />
          <div className="flex justify-between text-xs text-gray-400">
            <span>0.25x</span>
            <span>1x</span>
            <span>2x</span>
            <span>4x</span>
          </div>
          <div className="flex gap-2">
            {[0.5, 1.0, 1.5, 2.0].map((s) => (
              <button
                key={s}
                onClick={() => setSpeedFactor(s)}
                className={`flex-1 py-1.5 text-xs rounded border ${
                  speedFactor === s
                    ? "border-orange-500 bg-orange-50 text-orange-700"
                    : "border-gray-200"
                }`}
              >
                {s}x
              </button>
            ))}
          </div>
        </div>
      ),

      overlay_text: (
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Texto</label>
            <input
              type="text"
              value={overlayText}
              onChange={(e) => setOverlayText(e.target.value)}
              placeholder="Digite o texto..."
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-pink-500 outline-none"
            />
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label className="block text-xs text-gray-600 mb-1">Posi\u00e7\u00e3o X</label>
              <input type="number" value={textX} onChange={(e) => setTextX(parseInt(e.target.value) || 0)} className="w-full px-2 py-1.5 border rounded text-sm" />
            </div>
            <div>
              <label className="block text-xs text-gray-600 mb-1">Posi\u00e7\u00e3o Y</label>
              <input type="number" value={textY} onChange={(e) => setTextY(parseInt(e.target.value) || 0)} className="w-full px-2 py-1.5 border rounded text-sm" />
            </div>
          </div>
          <div>
            <label className="block text-xs text-gray-600 mb-1">Tamanho: {textSize}px</label>
            <input
              type="range"
              min={12}
              max={120}
              value={textSize}
              onChange={(e) => setTextSize(parseInt(e.target.value))}
              className="w-full accent-pink-500"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-600 mb-1">Cor</label>
            <div className="flex gap-2">
              {["white", "black", "red", "yellow", "blue", "green"].map((c) => (
                <button
                  key={c}
                  onClick={() => setTextColor(c)}
                  className={`w-7 h-7 rounded-full border-2 transition-transform ${
                    textColor === c ? "border-gray-800 scale-110" : "border-gray-300"
                  }`}
                  style={{
                    backgroundColor: c === "white" ? "#fff" : c === "black" ? "#000" : c,
                  }}
                />
              ))}
            </div>
          </div>
        </div>
      ),

      filter_apply: (
        <div className="space-y-3">
          <label className="block text-sm font-medium text-gray-700">Filtro</label>
          <div className="grid grid-cols-2 gap-2">
            {FILTERS.map((f) => (
              <button
                key={f.id}
                onClick={() => setSelectedFilter(f.id)}
                className={`px-3 py-2 rounded-lg border text-sm text-left transition-colors ${
                  selectedFilter === f.id
                    ? "border-indigo-500 bg-indigo-50 text-indigo-700"
                    : "border-gray-200 hover:border-gray-300"
                }`}
              >
                <span className="mr-1">{f.emoji}</span> {f.label}
              </button>
            ))}
          </div>
          <div>
            <label className="block text-xs text-gray-600 mb-1">
              Intensidade: {filterIntensity.toFixed(1)}
            </label>
            <input
              type="range"
              min={0}
              max={2}
              step={0.1}
              value={filterIntensity}
              onChange={(e) => setFilterIntensity(parseFloat(e.target.value))}
              className="w-full accent-indigo-500"
            />
          </div>
        </div>
      ),

      audio_volume: (
        <div className="space-y-4">
          <label className="block text-sm font-medium text-gray-700">
            Volume: {(audioVolume * 100).toFixed(0)}%
          </label>
          <input
            type="range"
            min={0}
            max={3}
            step={0.1}
            value={audioVolume}
            onChange={(e) => setAudioVolume(parseFloat(e.target.value))}
            className="w-full accent-teal-500"
          />
          <div className="flex justify-between text-xs text-gray-400">
            <span>Mudo</span>
            <span>100%</span>
            <span>200%</span>
            <span>300%</span>
          </div>
        </div>
      ),

      watermark: (
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Texto da Marca
            </label>
            <input
              type="text"
              value={watermarkText}
              onChange={(e) => setWatermarkText(e.target.value)}
              placeholder="Ex: \u00a9 Minha Empresa"
              className="w-full px-3 py-2 border rounded-lg"
            />
          </div>
          <div>
            <label className="block text-xs text-gray-600 mb-1">Posi\u00e7\u00e3o</label>
            <div className="grid grid-cols-3 gap-1">
              {[
                { v: "top_left", l: "\u2196" },
                { v: "top_right", l: "\u2197" },
                { v: "center", l: "\u25ce" },
                { v: "bottom_left", l: "\u2199" },
                { v: "bottom_right", l: "\u2198" },
              ].map((p) => (
                <button
                  key={p.v}
                  onClick={() => setWatermarkPosition(p.v)}
                  className={`py-2 text-lg rounded border ${
                    watermarkPosition === p.v
                      ? "border-cyan-500 bg-cyan-50"
                      : "border-gray-200"
                  }`}
                >
                  {p.l}
                </button>
              ))}
            </div>
          </div>
          <div>
            <label className="block text-xs text-gray-600 mb-1">
              Opacidade: {(watermarkOpacity * 100).toFixed(0)}%
            </label>
            <input
              type="range"
              min={0.1}
              max={1}
              step={0.1}
              value={watermarkOpacity}
              onChange={(e) => setWatermarkOpacity(parseFloat(e.target.value))}
              className="w-full accent-cyan-500"
            />
          </div>
        </div>
      ),

      thumbnail: (
        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tempo (segundos)
            </label>
            <input
              type="number"
              min={0}
              step={0.5}
              value={thumbnailTime}
              onChange={(e) => setThumbnailTime(parseFloat(e.target.value) || 0)}
              className="w-full px-3 py-2 border rounded-lg"
            />
          </div>
        </div>
      ),

      subtitle: (
        <div className="text-sm text-gray-500">
          <p>Em breve: interface de edi\u00e7\u00e3o de legendas.</p>
          <p className="mt-2">Use a API diretamente para adicionar legendas.</p>
        </div>
      ),

      audio_extract: (
        <div className="text-sm text-gray-500">
          <p>Clique em "Aplicar" para extrair a faixa de \u00e1udio do v\u00eddeo selecionado.</p>
        </div>
      ),
    };

    return toolPanels[activeTool] || null;
  };

  // ===== Main Render =====

  // Project list view
  if (!currentProject) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-5xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                <Film className="w-8 h-8 text-blue-600" />
                Editor de V\u00eddeo
              </h1>
              <p className="text-gray-500 mt-1">Edite seus v\u00eddeos de forma intuitiva</p>
            </div>
            <button
              onClick={() => setShowNewProject(true)}
              className="flex items-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
            >
              <Plus className="w-5 h-5" />
              Novo Projeto
            </button>
          </div>

          {/* Messages */}
          {error && (
            <Alert className="mb-4 border-yellow-200 bg-yellow-50">
              <AlertDescription className="text-yellow-800">
                {error}
              </AlertDescription>
            </Alert>
          )}
          {successMsg && (
            <Alert className="mb-4 border-green-200 bg-green-50">
              <AlertDescription className="text-green-700">{successMsg}</AlertDescription>
            </Alert>
          )}

          {/* New Project Dialog */}
          {showNewProject && (
            <Card className="mb-6 border-blue-200">
              <CardContent className="pt-6">
                <div className="flex gap-3">
                  <input
                    type="text"
                    value={newProjectName}
                    onChange={(e) => setNewProjectName(e.target.value)}
                    placeholder="Nome do projeto..."
                    className="flex-1 px-4 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 outline-none"
                    onKeyDown={(e) => e.key === "Enter" && createProject()}
                    autoFocus
                  />
                  <button
                    onClick={createProject}
                    disabled={isLoading}
                    className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50"
                  >
                    Criar
                  </button>
                  <button
                    onClick={() => setShowNewProject(false)}
                    className="px-4 py-2 border rounded-lg hover:bg-gray-50"
                  >
                    Cancelar
                  </button>
                </div>
              </CardContent>
            </Card>
          )}

          {/* Projects Grid */}
          {isLoading && projects.length === 0 ? (
            <div className="text-center py-20 text-gray-400">Carregando...</div>
          ) : projects.length === 0 ? (
            <div className="text-center py-20">
              <Film className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-500">Nenhum projeto ainda</h3>
              <p className="text-gray-400 mt-1">Crie um novo projeto para come\u00e7ar a editar</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {projects.map((project) => (
                <Card
                  key={project.id}
                  className="cursor-pointer hover:shadow-md transition-shadow group"
                  onClick={() => loadProject(project.id)}
                >
                  <CardContent className="pt-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <h3 className="font-semibold text-gray-900 group-hover:text-blue-600 transition-colors">
                          {project.name}
                        </h3>
                        <p className="text-sm text-gray-500 mt-1">
                          {project.sources?.length || 0} arquivo(s)
                          {" \u2022 "}
                          {project.operations?.length || 0} opera\u00e7\u00e3o(\u00f5es)
                        </p>
                        <Badge
                          className="mt-2"
                          variant={
                            project.status === "completed"
                              ? "default"
                              : project.status === "processing"
                              ? "secondary"
                              : "outline"
                          }
                        >
                          {project.status}
                        </Badge>
                      </div>
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          deleteProject(project.id);
                        }}
                        className="p-1.5 text-gray-400 hover:text-red-500 opacity-0 group-hover:opacity-100 transition-opacity"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          )}
        </div>
      </div>
    );
  }

  // ===== Editor View =====

  return (
    <div className="min-h-screen bg-gray-900 text-white flex flex-col">
      {/* Top Bar */}
      <div className="h-14 bg-gray-800 border-b border-gray-700 flex items-center px-4 gap-4">
        <button
          onClick={() => {
            setCurrentProject(null);
            setSelectedSource(null);
            setActiveTool(null);
            fetchProjects();
          }}
          className="text-gray-400 hover:text-white transition-colors"
        >
          <ChevronRight className="w-5 h-5 rotate-180" />
        </button>
        <Film className="w-5 h-5 text-blue-400" />
        <span className="font-semibold">{currentProject.name}</span>
        <Badge variant="outline" className="text-gray-300 border-gray-600">
          {currentProject.status}
        </Badge>

        <div className="ml-auto flex items-center gap-2">
          <button
            onClick={() => exportVideo("mp4")}
            disabled={isProcessing || currentProject.sources.length === 0}
            className="flex items-center gap-2 px-3 py-1.5 bg-green-600 hover:bg-green-700 disabled:opacity-50 rounded-lg text-sm font-medium transition-colors"
          >
            <Download className="w-4 h-4" />
            Exportar MP4
          </button>
          <button
            onClick={() => exportVideo("webm")}
            disabled={isProcessing || currentProject.sources.length === 0}
            className="flex items-center gap-2 px-3 py-1.5 bg-gray-700 hover:bg-gray-600 disabled:opacity-50 rounded-lg text-sm font-medium transition-colors"
          >
            Exportar WebM
          </button>
        </div>
      </div>

      {/* Messages */}
      {error && (
        <div className="px-4 py-2 bg-red-900/50 border-b border-red-800 text-red-300 text-sm flex items-center justify-between">
          <span>{error}</span>
          <button onClick={() => setError("")} className="text-red-400 hover:text-red-200">
            \u2715
          </button>
        </div>
      )}
      {successMsg && (
        <div className="px-4 py-2 bg-green-900/50 border-b border-green-800 text-green-300 text-sm">
          {successMsg}
        </div>
      )}

      {/* Processing Bar */}
      {isProcessing && (
        <div className="px-4 py-2 bg-blue-900/50 border-b border-blue-800">
          <div className="flex items-center gap-3">
            <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
            <span className="text-blue-300 text-sm">Processando...</span>
          </div>
        </div>
      )}

      {/* Main Layout: 3-column */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left: Source Files */}
        <div className="w-64 bg-gray-800 border-r border-gray-700 flex flex-col">
          <div className="p-3 border-b border-gray-700 flex items-center justify-between">
            <span className="text-sm font-medium text-gray-300">Arquivos</span>
            <button
              onClick={() => fileInputRef.current?.click()}
              className="p-1.5 text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
              title="Enviar v\u00eddeo"
            >
              <Upload className="w-4 h-4" />
            </button>
            <input
              ref={fileInputRef}
              type="file"
              accept="video/*,audio/*"
              className="hidden"
              onChange={(e) => {
                const file = e.target.files?.[0];
                if (file) uploadSource(file);
                e.target.value = "";
              }}
            />
          </div>

          <div className="flex-1 overflow-y-auto p-2 space-y-1">
            {currentProject.sources.length === 0 ? (
              <div
                className="flex flex-col items-center justify-center h-40 border-2 border-dashed border-gray-600 rounded-lg cursor-pointer hover:border-blue-500 transition-colors"
                onClick={() => fileInputRef.current?.click()}
              >
                <Upload className="w-8 h-8 text-gray-500 mb-2" />
                <span className="text-sm text-gray-500">Enviar v\u00eddeo</span>
              </div>
            ) : (
              currentProject.sources.map((source) => (
                <button
                  key={source.source_id}
                  onClick={() => setSelectedSource(source)}
                  className={`w-full text-left px-3 py-2.5 rounded-lg text-sm transition-colors ${
                    selectedSource?.source_id === source.source_id
                      ? "bg-blue-600/30 text-blue-300 border border-blue-500/50"
                      : "text-gray-300 hover:bg-gray-700"
                  }`}
                >
                  <div className="flex items-center gap-2">
                    {source.generated ? (
                      <Wand2 className="w-3.5 h-3.5 text-purple-400 flex-shrink-0" />
                    ) : (
                      <Film className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                    )}
                    <span className="truncate">{source.label || source.filename}</span>
                  </div>
                  <div className="mt-1 text-xs text-gray-500 pl-5.5">
                    {formatFileSize(source.file_size)}
                    {source.probe && ` \u2022 ${formatDuration(source.probe.duration)}`}
                  </div>
                </button>
              ))
            )}
          </div>
        </div>

        {/* Center: Preview + Info */}
        <div className="flex-1 flex flex-col">
          {/* Preview Area */}
          <div className="flex-1 flex items-center justify-center bg-black/50 relative">
            {selectedSource ? (
              <div className="text-center">
                <div className="bg-gray-800 rounded-xl p-8 max-w-md">
                  <Film className="w-16 h-16 text-blue-400 mx-auto mb-4" />
                  <h3 className="font-semibold text-lg">{selectedSource.label || selectedSource.filename}</h3>
                  {selectedSource.probe && (
                    <div className="mt-4 grid grid-cols-2 gap-3 text-sm">
                      <div className="bg-gray-700/50 rounded-lg p-2.5">
                        <div className="text-gray-400 text-xs">Resolu\u00e7\u00e3o</div>
                        <div className="font-mono">{selectedSource.probe.width}\u00d7{selectedSource.probe.height}</div>
                      </div>
                      <div className="bg-gray-700/50 rounded-lg p-2.5">
                        <div className="text-gray-400 text-xs">Dura\u00e7\u00e3o</div>
                        <div className="font-mono">{formatDuration(selectedSource.probe.duration)}</div>
                      </div>
                      <div className="bg-gray-700/50 rounded-lg p-2.5">
                        <div className="text-gray-400 text-xs">FPS</div>
                        <div className="font-mono">{selectedSource.probe.fps}</div>
                      </div>
                      <div className="bg-gray-700/50 rounded-lg p-2.5">
                        <div className="text-gray-400 text-xs">Codec</div>
                        <div className="font-mono">{selectedSource.probe.video_codec}</div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="text-center text-gray-500">
                <Layers className="w-12 h-12 mx-auto mb-3 opacity-50" />
                <p>Selecione um arquivo para editar</p>
              </div>
            )}
          </div>

          {/* Timeline / Operations History */}
          <div className="h-32 bg-gray-800 border-t border-gray-700 p-3 overflow-x-auto">
            <div className="text-xs text-gray-400 mb-2 font-medium">
              Hist\u00f3rico de Opera\u00e7\u00f5es ({currentProject.operations.length})
            </div>
            {currentProject.operations.length === 0 ? (
              <div className="text-sm text-gray-500 flex items-center gap-2">
                <Clock className="w-4 h-4" />
                Nenhuma opera\u00e7\u00e3o aplicada ainda
              </div>
            ) : (
              <div className="flex gap-2">
                {currentProject.operations.map((op, i) => (
                  <div
                    key={op.operation_id}
                    className="flex-shrink-0 bg-gray-700/50 border border-gray-600 rounded-lg px-3 py-2 text-xs"
                  >
                    <div className="font-medium text-gray-200">
                      {i + 1}. {TOOLS[op.operation as ToolType]?.label || op.operation}
                    </div>
                    <div className="text-gray-500 mt-0.5">
                      {new Date(op.executed_at).toLocaleTimeString()}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Right: Tools Panel */}
        <div className="w-72 bg-gray-800 border-l border-gray-700 flex flex-col">
          {/* Tool Grid */}
          <div className="p-3 border-b border-gray-700">
            <span className="text-sm font-medium text-gray-300">Ferramentas</span>
            <div className="grid grid-cols-4 gap-1.5 mt-2">
              {(Object.entries(TOOLS) as [ToolType, ToolConfig][]).map(([key, tool]) => (
                <button
                  key={key}
                  onClick={() => setActiveTool(activeTool === key ? null : key)}
                  disabled={!selectedSource}
                  className={`flex flex-col items-center py-2 px-1 rounded-lg text-xs transition-all ${
                    activeTool === key
                      ? "bg-blue-600/30 text-blue-300 ring-1 ring-blue-500/50"
                      : selectedSource
                      ? "text-gray-400 hover:bg-gray-700 hover:text-gray-200"
                      : "text-gray-600 cursor-not-allowed"
                  }`}
                  title={tool.description}
                >
                  <span className={activeTool === key ? "text-blue-400" : tool.color}>
                    {tool.icon}
                  </span>
                  <span className="mt-1 leading-tight text-center" style={{ fontSize: "10px" }}>
                    {tool.label}
                  </span>
                </button>
              ))}
            </div>
          </div>

          {/* Tool Settings */}
          <div className="flex-1 overflow-y-auto p-3">
            {activeTool ? (
              <div>
                <h3 className="text-sm font-semibold text-gray-200 mb-3 flex items-center gap-2">
                  <span className={TOOLS[activeTool].color}>{TOOLS[activeTool].icon}</span>
                  {TOOLS[activeTool].label}
                </h3>
                <div className="text-gray-300">{renderToolPanel()}</div>

                <button
                  onClick={executeOperation}
                  disabled={isProcessing}
                  className="w-full mt-4 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:opacity-50 rounded-lg font-medium text-sm transition-colors flex items-center justify-center gap-2"
                >
                  {isProcessing ? (
                    <>
                      <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                      Processando...
                    </>
                  ) : (
                    <>
                      <Wand2 className="w-4 h-4" />
                      Aplicar
                    </>
                  )}
                </button>
              </div>
            ) : selectedSource ? (
              <div className="text-center text-gray-500 mt-10">
                <Settings className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">Selecione uma ferramenta</p>
              </div>
            ) : (
              <div className="text-center text-gray-600 mt-10">
                <Move className="w-8 h-8 mx-auto mb-2 opacity-30" />
                <p className="text-sm">Selecione um arquivo primeiro</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoEditor;
